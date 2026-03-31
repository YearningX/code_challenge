"""
Model Validation Script

Validates deployed MLflow model by loading and running test queries.

Usage:
    python scripts/deployment/validate_model.py --model-uri <model_uri>
"""

import argparse
import sys
import time


def validate_model(model_uri: str) -> int:
    """
    Validate MLflow model.

    Args:
        model_uri: MLflow model URI

    Returns:
        0 if validation passed, 1 otherwise
    """
    print("="*60)
    print("MLflow Model Validation")
    print("="*60)
    print(f"Model URI: {model_uri}")

    try:
        import mlflow.pyfunc

        # Load model
        print("\n[1] Loading model...")
        model = mlflow.pyfunc.load_model(model_uri)
        print("[PASS] Model loaded successfully")

        # Test queries
        test_queries = [
            {
                "query": "What is ECU-750?",
                "expected_keywords": ["ECU-700", "Series", "MHz", "Flash"]
            },
            {
                "query": "What is ECU-850?",
                "expected_keywords": ["ECU-800", "Cortex-A53", "LPDDR4", "eMMC"]
            },
            {
                "query": "Compare ECU-850 and ECU-850b",
                "expected_keywords": ["GHz", "NPU", "RAM", "comparison"]
            }
        ]

        print("\n[2] Running test queries...")
        all_passed = True

        for i, test_case in enumerate(test_queries, 1):
            query = test_case["query"]
            expected = test_case["expected_keywords"]

            print(f"\n  Query {i}: {query}")
            start_time = time.time()

            try:
                result = model.predict({"query": query})
                latency = time.time() - start_time

                # Extract response
                if isinstance(result, list) and len(result) > 0:
                    response = result[0]
                    if isinstance(response, dict):
                        response_text = response.get('response', '')
                    else:
                        response_text = str(response)
                else:
                    response_text = str(result)

                # Check for expected keywords
                keywords_found = sum(1 for kw in expected if kw.lower() in response_text.lower())
                keywords_score = keywords_found / len(expected)

                passed = keywords_score >= 0.5 and latency < 10.0

                print(f"    Latency: {latency:.2f}s")
                print(f"    Keywords: {keywords_found}/{len(expected)} found")
                print(f"    {'[PASS]' if passed else '[FAIL]'} Query {i}")

                if not passed:
                    all_passed = False

            except Exception as e:
                print(f"    [ERROR] Query failed: {e}")
                all_passed = False

        # Summary
        print("\n" + "="*60)
        if all_passed:
            print("[SUCCESS] Model validation passed!")
            print("  - All queries executed successfully")
            print("  - Response quality acceptable")
            print("  - Latency within requirements")
            print("="*60)
            return 0
        else:
            print("[FAILURE] Model validation failed!")
            print("  - Some queries failed or quality issues")
            print("="*60)
            return 1

    except Exception as e:
        print(f"\n[ERROR] Validation failed: {e}")
        import traceback
        traceback.print_exc()
        print("="*60)
        return 1


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Validate MLflow model")
    parser.add_argument(
        "--model-uri",
        type=str,
        required=True,
        help="MLflow model URI to validate"
    )

    args = parser.parse_args()
    return validate_model(args.model_uri)


if __name__ == "__main__":
    sys.exit(main())
