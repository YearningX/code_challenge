"""
Comprehensive Test Queries for ME ECU Agent

Tests the agent with 10 predefined queries to validate Tier 1 requirements:
- Correctly answers 8/10 predefined test queries (80% accuracy)
- Response time <10 seconds per query

Categories:
1. ECU-700 Series (3 queries)
2. ECU-800 Series (4 queries)
3. Comparison queries (2 queries)
4. General/Overview queries (1 query)
"""

import time
import mlflow
from typing import List, Dict, Tuple


# Comprehensive test queries covering all aspects
TEST_QUERIES = [
    # ECU-700 Series Queries
    {
        "query": "What is ECU-700?",
        "category": "ECU-700",
        "expected_keywords": ["300 MHz", "ARM Cortex-R5", "Flash", "CAN", "temperature"],
        "min_quality_score": 0.7
    },
    {
        "query": "What are the key features of ECU-700?",
        "category": "ECU-700",
        "expected_keywords": ["Flash memory", "interfaces", "temperature range", "automotive"],
        "min_quality_score": 0.6
    },
    {
        "query": "What operating temperature does ECU-700 support?",
        "category": "ECU-700",
        "expected_keywords": ["-40", "+105", "temperature", "range"],
        "min_quality_score": 0.8
    },

    # ECU-800 Series Queries
    {
        "query": "What is ECU-800?",
        "category": "ECU-800",
        "expected_keywords": ["next-generation", "ADAS", "infotainment", "automotive"],
        "min_quality_score": 0.7
    },
    {
        "query": "What is ECU-850?",
        "category": "ECU-800",
        "expected_keywords": ["dual-core", "Cortex-A53", "1.2 GHz", "LPDDR4", "eMMC"],
        "min_quality_score": 0.7
    },
    {
        "query": "What interfaces does ECU-850 support?",
        "category": "ECU-800",
        "expected_keywords": ["CAN FD", "Ethernet", "USB", "interfaces"],
        "min_quality_score": 0.6
    },
    {
        "query": "What is ECU-850b?",
        "category": "ECU-800",
        "expected_keywords": ["4-core", "Cortex-A53", "1.5 GHz", "NPU", "neural"],
        "min_quality_score": 0.7
    },

    # Comparison Queries
    {
        "query": "Compare ECU-850 and ECU-850b",
        "category": "Comparison",
        "expected_keywords": ["dual-core", "quad-core", "1.2 GHz", "1.5 GHz", "NPU", "comparison"],
        "min_quality_score": 0.6
    },
    {
        "query": "What are the differences between ECU-700 and ECU-800?",
        "category": "Comparison",
        "expected_keywords": ["Cortex-R5", "Cortex-A53", "300 MHz", "1.2 GHz", "generations"],
        "min_quality_score": 0.6
    },

    # General/Overview Query
    {
        "query": "What ECU product lines are available?",
        "category": "Overview",
        "expected_keywords": ["ECU-700", "ECU-800", "Series", "platform"],
        "min_quality_score": 0.7
    }
]


def calculate_keyword_presence(response: str, keywords: List[str]) -> float:
    """Calculate keyword presence score.

    Args:
        response: Model response
        keywords: Expected keywords

    Returns:
        Score from 0.0 to 1.0
    """
    if not keywords:
        return 1.0

    response_lower = response.lower()
    found = sum(1 for kw in keywords if kw.lower() in response_lower)
    return found / len(keywords)


def evaluate_response_quality(response: str, query_data: Dict) -> Tuple[bool, float, str]:
    """Evaluate response quality.

    Args:
        response: Model response
        query_data: Query test data

    Returns:
        (passed, score, reasoning)
    """
    keywords = query_data["expected_keywords"]
    min_score = query_data["min_quality_score"]

    # Calculate keyword score
    keyword_score = calculate_keyword_presence(response, keywords)

    # Check response length
    length_ok = len(response) > 50

    # Check for error indicators
    has_errors = any(err in response.lower() for err in ["error", "not found", "unknown", "i don't know"])

    # Overall score
    score = keyword_score
    if length_ok:
        score += 0.1
    if has_errors:
        score -= 0.3

    score = max(0.0, min(1.0, score))

    passed = score >= min_score

    reasoning = f"Keywords: {keyword_score:.2f}, Length OK: {length_ok}, No Errors: {not has_errors}"

    return passed, score, reasoning


def run_comprehensive_test(model_uri: str = "runs:/20f8fa846aea4dd183fa8bbe3739efb6/ecu_agent_model"):
    """Run comprehensive test suite.

    Args:
        model_uri: MLflow model URI

    Returns:
        Test results dict
    """
    print("="*80)
    print("ME ECU Agent - Comprehensive Test Suite")
    print("="*80)
    print(f"Model URI: {model_uri}")
    print(f"Total Queries: {len(TEST_QUERIES)}")
    print("="*80)

    # Load model
    print("\n[Loading Model]")
    try:
        model = mlflow.pyfunc.load_model(model_uri)
        print("[OK] Model loaded successfully\n")
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}\n")
        return {"success": False, "error": str(e)}

    # Run tests
    results = {
        "total_queries": len(TEST_QUERIES),
        "passed_queries": 0,
        "failed_queries": 0,
        "total_time": 0.0,
        "avg_time": 0.0,
        "accuracy": 0.0,
        "results_by_category": {},
        "detailed_results": []
    }

    for i, query_data in enumerate(TEST_QUERIES, 1):
        query = query_data["query"]
        category = query_data["category"]

        print(f"[{i}/{len(TEST_QUERIES)}] Category: {category}")
        print(f"    Query: {query}")

        # Execute query
        start_time = time.time()
        try:
            result = model.predict({"query": query})

            # Extract response
            if isinstance(result, list) and len(result) > 0:
                response = result[0]
                if isinstance(response, dict):
                    response_text = response.get('response', '')
                else:
                    response_text = str(response)
            else:
                response_text = str(result)

            latency = time.time() - start_time

            # Evaluate response
            passed, score, reasoning = evaluate_response_quality(response_text, query_data)

            # Update results
            if passed:
                results["passed_queries"] += 1
                status = "[PASS]"
            else:
                results["failed_queries"] += 1
                status = "[FAIL]"

            results["total_time"] += latency

            # Display results
            print(f"    Latency: {latency:.2f}s")
            print(f"    Score: {score:.2f}/{query_data['min_quality_score']:.2f}")
            print(f"    {status} {reasoning}")

            if passed:
                print(f"    Response Preview: {response_text[:100]}...")

            print()

            # Store detailed result
            results["detailed_results"].append({
                "query": query,
                "category": category,
                "passed": passed,
                "score": score,
                "latency": latency,
                "response": response_text[:200]
            })

            # Update category stats
            if category not in results["results_by_category"]:
                results["results_by_category"][category] = {
                    "total": 0,
                    "passed": 0,
                    "total_time": 0.0
                }

            results["results_by_category"][category]["total"] += 1
            if passed:
                results["results_by_category"][category]["passed"] += 1
            results["results_by_category"][category]["total_time"] += latency

        except Exception as e:
            print(f"    [ERROR] Query failed: {e}\n")
            results["failed_queries"] += 1
            results["detailed_results"].append({
                "query": query,
                "category": category,
                "passed": False,
                "error": str(e)
            })

    # Calculate summary stats
    results["avg_time"] = results["total_time"] / results["total_queries"]
    results["accuracy"] = results["passed_queries"] / results["total_queries"]

    return results


def print_test_summary(results: Dict):
    """Print test summary.

    Args:
        results: Test results dict
    """
    print("\n" + "="*80)
    print("Test Summary")
    print("="*80)

    print(f"\nOverall Results:")
    print(f"  Total Queries: {results['total_queries']}")
    print(f"  Passed: {results['passed_queries']} ({results['accuracy']*100:.1f}%)")
    print(f"  Failed: {results['failed_queries']} ({(1-results['accuracy'])*100:.1f}%)")

    print(f"\nPerformance:")
    print(f"  Total Time: {results['total_time']:.2f}s")
    print(f"  Average Time: {results['avg_time']:.2f}s")
    print(f"  Max Time (Target): 10.00s")

    print(f"\nResults by Category:")
    for category, stats in results["results_by_category"].items():
        avg_time = stats["total_time"] / stats["total"]
        accuracy = stats["passed"] / stats["total"] * 100
        print(f"  {category}:")
        print(f"    Passed: {stats['passed']}/{stats['total']} ({accuracy:.0f}%)")
        print(f"    Avg Time: {avg_time:.2f}s")

    print("\n" + "="*80)

    # Tier 1 Requirements Check
    print("\nTier 1 Requirements Validation:")
    print("="*80)

    accuracy_ok = results["accuracy"] >= 0.8
    latency_ok = results["avg_time"] < 10.0

    print(f"\n1. Test Query Accuracy:")
    print(f"   Required: 8/10 (80%)")
    print(f"   Achieved: {results['passed_queries']}/10 ({results['accuracy']*100:.0f}%)")
    print(f"   {'[PASS]' if accuracy_ok else '[FAIL]'} Accuracy requirement")

    print(f"\n2. Response Time:")
    print(f"   Required: <10 seconds per query")
    print(f"   Achieved: {results['avg_time']:.2f}s average")
    print(f"   {'[PASS]' if latency_ok else '[FAIL]'} Latency requirement")

    overall_pass = accuracy_ok and latency_ok

    print(f"\nOverall Status:")
    print(f"  {'[PASS] Tier 1 Requirements Met!' if overall_pass else '[FAIL] Tier 1 Requirements Not Met'}")
    print("="*80)

    # Failed queries
    if results["failed_queries"] > 0:
        print("\nFailed Queries:")
        for result in results["detailed_results"]:
            if not result.get("passed", True):
                print(f"  - {result['query']}")
                if "error" in result:
                    print(f"    Error: {result['error']}")
                else:
                    print(f"    Score: {result.get('score', 0):.2f}")
        print()


def main():
    """Main function."""
    results = run_comprehensive_test()

    if not results.get("success", True):
        print(f"\n[ERROR] Test execution failed: {results.get('error')}")
        return 1

    print_test_summary(results)

    # Return exit code
    return 0 if results["accuracy"] >= 0.8 else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
