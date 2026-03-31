"""
End-to-end testing of ECU Agent on test questions.

This script tests the agent against the 10 predefined test questions
and compares responses with expected answers.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pathlib import Path
from me_ecu_agent.document_processor import DocumentProcessor
from me_ecu_agent.vectorstore import VectorStoreManager
from me_ecu_agent.graph import ECUQueryAgent
import pandas as pd


def setup_agent():
    """Initialize agent with vector stores."""
    print("Setting up ECU Agent...")
    
    # Step 1: Process documents
    print("1. Processing documents...")
    processor = DocumentProcessor()
    data_dir = Path("data")
    
    if not data_dir.exists():
        print(f"Error: data directory not found at {data_dir}")
        return None
    
    # Check for markdown files
    md_files = list(data_dir.glob("*.md"))
    if not md_files:
        print(f"Error: No .md files found in {data_dir}")
        print(f"Files in data directory: {list(data_dir.iterdir())}")
        return None
    
    print(f"   Found {len(md_files)} markdown files")
    
    # Process documents
    try:
        product_chunks = processor.process_documents(str(data_dir))
        print(f"   Processed {len(product_chunks['ECU-700'])} ECU-700 chunks")
        print(f"   Processed {len(product_chunks['ECU-800'])} ECU-800 chunks")
    except Exception as e:
        print(f"Error processing documents: {e}")
        return None
    
    # Step 2: Create vector stores
    print("2. Creating vector stores...")
    manager = VectorStoreManager()
    try:
        manager.create_stores(product_chunks)
        print("   Vector stores created successfully")
    except Exception as e:
        print(f"Error creating vector stores: {e}")
        return None
    
    # Step 3: Initialize agent
    print("3. Initializing agent...")
    agent = ECUQueryAgent()
    agent.register_retriever("ECU-700", manager.get_retriever("ECU-700"))
    agent.register_retriever("ECU-800", manager.get_retriever("ECU-800"))
    print("   Agent initialized successfully")
    
    return agent


def test_questions(agent, questions_file):
    """Test agent on predefined questions."""
    print(f"\nTesting agent on questions from {questions_file}...")
    
    # Load questions
    try:
        df = pd.read_csv(questions_file)
    except Exception as e:
        print(f"Error loading questions: {e}")
        return
    
    print(f"Loaded {len(df)} test questions\n")
    
    results = []
    
    for idx, row in df.iterrows():
        question_id = row['Question_ID']
        category = row['Category']
        question = row['Question']
        expected = row['Expected_Answer']
        criteria = row['Evaluation_Criteria']
        
        print(f"\n{'='*80}")
        print(f"Question {question_id}: {category}")
        print(f"Q: {question}")
        print(f"{'='*80}")
        
        # Query agent
        try:
            result = agent.invoke(question)
            response = result.get('response', 'No response generated')
            detected_pl = result.get('detected_product_line', 'unknown')
            
            print(f"Detected Product Line: {detected_pl}")
            print(f"\nAgent Response:")
            print(f"{response}")
            print(f"\nExpected Answer:")
            print(f"{expected}")
            print(f"\nEvaluation Criteria: {criteria}")
            
            # Simple evaluation: check if key terms match
            score = evaluate_response(response, expected, category)
            print(f"\nSimilarity Score: {score:.2f}/1.00")
            
            results.append({
                'Question_ID': question_id,
                'Category': category,
                'Question': question,
                'Detected_PL': detected_pl,
                'Agent_Response': response,
                'Expected_Answer': expected,
                'Score': score
            })
            
        except Exception as e:
            print(f"Error processing question {question_id}: {e}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
    
    return results


def evaluate_response(response, expected, category):
    """Simple similarity evaluation."""
    response_lower = response.lower()
    expected_lower = expected.lower()
    
    # Extract key numbers and terms from expected answer
    import re
    
    # Look for numbers (temperatures, capacities, etc.)
    expected_numbers = re.findall(r'\d+\.?\d*\s*[°c°CcFfmggBb]+', expected_lower)
    response_numbers = re.findall(r'\d+\.?\d*\s*[°c°CcFfmggBb]+', response_lower)
    
    # Calculate score based on matches
    if not expected_numbers:
        # No numbers to match, check word overlap
        expected_words = set(expected_lower.split())
        response_words = set(response_lower.split())
        overlap = len(expected_words & response_words)
        score = min(overlap / len(expected_words), 1.0) if expected_words else 0.0
    else:
        # Check how many expected numbers appear in response
        matches = sum(1 for num in expected_numbers if num in response_lower)
        score = matches / len(expected_numbers)
    
    return score


def main():
    """Main test execution."""
    print("="*80)
    print("ECU Agent End-to-End Testing")
    print("="*80)
    
    # Setup agent
    agent = setup_agent()
    if agent is None:
        print("\n❌ Failed to setup agent. Exiting.")
        return
    
    # Test questions
    questions_file = "data/test-questions.csv"
    if not Path(questions_file).exists():
        print(f"\n❌ Questions file not found: {questions_file}")
        return
    
    results = test_questions(agent, questions_file)
    
    if results:
        # Summary
        print(f"\n{'='*80}")
        print("TEST SUMMARY")
        print(f"{'='*80}")
        
        avg_score = sum(r['Score'] for r in results) / len(results)
        print(f"Total Questions: {len(results)}")
        print(f"Average Similarity Score: {avg_score:.2f}/1.00")
        
        print(f"\nScores by Question:")
        for r in results:
            status = "✅" if r['Score'] > 0.7 else "⚠️" if r['Score'] > 0.4 else "❌"
            print(f"  Q{r['Question_ID']}: {r['Score']:.2f} {status}")
        
        # Save results
        results_df = pd.DataFrame(results)
        output_file = "data/test-results.csv"
        results_df.to_csv(output_file, index=False)
        print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
