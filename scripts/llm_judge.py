"""
LLM-as-Judge Evaluation Script using GPT-4
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, 'src')

from pathlib import Path
from me_ecu_agent.document_processor import DocumentProcessor
from me_ecu_agent.vectorstore import VectorStoreManager
from me_ecu_agent.graph import ECUQueryAgent
import pandas as pd
from openai import OpenAI


def setup_agent():
    """Setup optimized agent."""
    print("Setting up optimized agent...")
    processor = DocumentProcessor()
    product_chunks = processor.process_documents("data")
    manager = VectorStoreManager()
    manager.create_stores(product_chunks)

    agent = ECUQueryAgent()
    agent.register_retriever("ECU-700", manager.get_retriever("ECU-700", k=10))
    agent.register_retriever("ECU-800", manager.get_retriever("ECU-800", k=15))

    return agent


def llm_judge_evaluate(question, response, expected, context=""):
    """
    Use configured LLM (e.g., GPT-4 or Qwen-plus) to evaluate the response quality.

    Returns a score between 0 and 1.
    """
    from me_ecu_agent.model_config import get_model_config
    model_config = get_model_config()

    client = OpenAI(
        api_key=model_config.api_key,
        base_url=model_config.base_url
    )

    evaluation_prompt = f"""You are an expert evaluator for a RAG (Retrieval-Augmented Generation) system.

Your task is to evaluate how well the Actual Answer answers the Question compared to the Expected Answer.

**Evaluation Criteria:**

1. **Correctness (40% weight)**: Is the information in the Actual Answer factually correct according to the Context? 
2. **Completeness (30% weight)**: Does the Actual Answer include all relevant information from the Expected Answer?
3. **Relevance (20% weight)**: Is the Actual Answer relevant to the question?
4. **Clarity (10% weight)**: Is the Actual Answer clear and well-structured?

**Scoring Guidelines:**
- **1.0 (Perfect)**: The Actual Answer is completely correct, complete, and clear. It matches or exceeds the Expected Answer.
- **0.8-0.9 (Excellent)**: The Actual Answer is correct and complete with minor differences in wording or structure.
- **0.6-0.7 (Good)**: The Actual Answer is mostly correct but may miss some details or have minor inaccuracies.
- **0.4-0.5 (Fair)**: The Actual Answer has some correct information but is incomplete or contains inaccuracies.
- **0.2-0.3 (Poor)**: The Actual Answer is mostly incorrect or irrelevant.
- **0.0-0.1 (Very Poor)**: The Actual Answer is completely wrong or doesn't address the question.

**Important Notes:**
- Focus on the INFORMATION content, not the exact wording.
- Use the provided Context to verify technical accuracy.
- If the Actual Answer provides correct information present in the Context but NOT in the Expected Answer, DO NOT penalize it; reward accuracy.
- If the Expected Answer includes information not directly asked in the question, don't penalize the Actual Answer for omitting it.

**Input:**

Question: {question}

Context: {context}

Expected Answer: {expected}

Actual Answer: {response}

**Output:**
Provide your evaluation in the following format:

Score: [0.0 to 1.0]
Reasoning: [Brief explanation of your score]

Provide ONLY the score and reasoning, nothing else.
"""

    try:
        completion = client.chat.completions.create(
            model=model_config.model_name,
            messages=[
                {"role": "system", "content": "You are an expert evaluator for RAG systems."},
                {"role": "user", "content": evaluation_prompt}
            ],
            temperature=0.0,  # Consistent evaluation
            max_tokens=500
        )

        result = completion.choices[0].message.content.strip()

        # Extract score from result
        if "Score:" in result:
            score_line = [line for line in result.split('\n') if 'Score:' in line][0]
            score_str = score_line.split('Score:')[1].strip().split()[0]
            score = float(score_str)
        else:
            # Fallback: try to extract first number
            import re
            numbers = re.findall(r'0\.\d+|1\.0|0\.0', result)
            score = float(numbers[0]) if numbers else 0.0

        return score, result

    except Exception as e:
        print(f"Error in LLM evaluation: {e}")
        return 0.0, f"Error: {e}"


def test_all_questions_with_llm_judge(agent, questions_file):
    """Test all questions with LLM-as-Judge evaluation."""
    print("Testing all questions with GPT-4 as Judge...")
    print()

    df = pd.read_csv(questions_file)

    results = []
    for idx, row in df.iterrows():
        q_id = row['Question_ID']
        category = row['Category']
        question = row['Question']
        expected = row['Expected_Answer']

        print(f"Q{q_id}: {category}")
        print(f"Query: {question}")

        try:
            result = agent.invoke(question)
            response = result.get('response', 'No response')
            detected = result.get('detected_product_line', 'unknown')

            print(f"Detected: {detected}")
            print(f"Response: {response[:200]}...")

            # Use GPT-4 as judge
            context = result.get('retrieved_context', '')
            score, reasoning = llm_judge_evaluate(question, response, expected, context)

            print(f"Score: {score:.2f}")
            print(f"Reasoning: {reasoning.split('Reasoning:')[1].strip() if 'Reasoning:' in reasoning else 'N/A'}")
            print("-" * 80)

            results.append({
                'Question_ID': q_id,
                'Category': category,
                'Question': question,
                'Detected_PL': detected,
                'Response': response,
                'Expected_Answer': expected,
                'Score': score,
                'LLM_Reasoning': reasoning
            })

        except Exception as e:
            print(f"ERROR: {e}")
            results.append({
                'Question_ID': q_id,
                'Category': category,
                'Question': question,
                'Response': f"Error: {e}",
                'Expected_Answer': expected,
                'Score': 0.0,
                'LLM_Reasoning': f"Error: {e}"
            })

    return results


def main():
    print("="*80)
    print("ECU AGENT TEST - LLM-AS-JUDGE EVALUATION (GPT-4)")
    print("Date: 2026-03-30")
    print("="*80)
    print()

    agent = setup_agent()

    results = test_all_questions_with_llm_judge(agent, "data/test-questions.csv")

    # Calculate statistics
    scores = [r['Score'] for r in results]
    avg_score = sum(scores) / len(scores)
    perfect = sum(1 for s in scores if s >= 0.9)
    excellent = sum(1 for s in scores if 0.8 <= s < 0.9)
    good = sum(1 for s in scores if 0.7 <= s < 0.8)
    fair = sum(1 for s in scores if 0.6 <= s < 0.7)
    poor = sum(1 for s in scores if s < 0.6)

    print()
    print("="*80)
    print("FINAL RESULTS - LLM-AS-JUDGE EVALUATION")
    print("="*80)
    print(f"Total Questions: {len(results)}")
    print(f"Average Score: {avg_score:.2f}/1.00")
    print(f"Perfect (>=0.9): {perfect}/{len(results)}")
    print(f"Excellent (0.8-0.9): {excellent}/{len(results)}")
    print(f"Good (0.7-0.8): {good}/{len(results)}")
    print(f"Fair (0.6-0.7): {fair}/{len(results)}")
    print(f"Poor (<0.6): {poor}/{len(results)}")
    print()

    # Score breakdown
    print("Score Breakdown:")
    for r in results:
        score = r['Score']
        if score >= 0.9:
            status = "PERFECT"
        elif score >= 0.8:
            status = "EXCELLENT"
        elif score >= 0.7:
            status = "GOOD"
        elif score >= 0.6:
            status = "FAIR"
        else:
            status = "POOR"
        print(f"  Q{r['Question_ID']}: {score:.2f} ({status})")

    print()
    if avg_score >= 0.85:
        print("EXCELLENT: Exceeded 85%!")
    elif avg_score >= 0.80:
        print("SUCCESS: Met 80% target")
    elif avg_score >= 0.75:
        print("GOOD: Close to target")
    elif avg_score >= 0.70:
        print("ACCEPTABLE: Above 70%")
    else:
        print("NEEDS IMPROVEMENT")

    # Save results
    results_df = pd.DataFrame(results)
    output_file = "data/test-results-llm-judge.csv"
    results_df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\nFull results saved to: {output_file}")
    print("Evaluation Method: GPT-4 LLM-as-Judge")


if __name__ == "__main__":
    main()
