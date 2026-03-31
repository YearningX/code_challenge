"""
MLflow Model Serving Test Script

OPTIMIZED (2026-03-31): Comprehensive testing script for MLflow model
including model loading, prediction, and serving validation.

Usage:
    python scripts/test_mlflow_serving.py
"""

import os
import sys
from pathlib import Path

import mlflow.pyfunc
import pandas as pd


def test_model_loading(model_uri: str):
    """
    Test model loading from MLflow.

    Args:
        model_uri: MLflow model URI
    """
    print("\n" + "="*60)
    print("Test 1: Model Loading")
    print("="*60)

    try:
        print(f"Loading model from: {model_uri}")
        model = mlflow.pyfunc.load_model(model_uri)
        print("✓ Model loaded successfully")
        return model
    except Exception as e:
        print(f"✗ Model loading failed: {e}")
        return None


def test_single_query_prediction(model, query: str):
    """
    Test single query prediction.

    Args:
        model: Loaded MLflow model
        query: Test query
    """
    print("\n" + "="*60)
    print("Test 2: Single Query Prediction")
    print("="*60)

    try:
        print(f"Query: {query}")
        result = model.predict({"query": query})

        if isinstance(result, list) and len(result) > 0:
            response = result[0]
            if isinstance(response, dict):
                # Detailed response format
                print(f"Response: {response.get('response', 'No response')}")
                print(f"Status: {response.get('status', 'unknown')}")
                print(f"Latency: {response.get('latency_seconds', 'N/A')}s")
            else:
                # Simple response format
                print(f"Response: {response}")
            print("✓ Single query prediction successful")
            return True
        else:
            print("✗ Unexpected response format")
            return False

    except Exception as e:
        print(f"✗ Prediction failed: {e}")
        return False


def test_batch_prediction(model, queries: list):
    """
    Test batch prediction with multiple queries.

    Args:
        model: Loaded MLflow model
        queries: List of test queries
    """
    print("\n" + "="*60)
    print("Test 3: Batch Prediction")
    print("="*60)

    try:
        print(f"Processing {len(queries)} queries...")
        results = model.predict(queries)

        if len(results) == len(queries):
            print("✓ Batch prediction successful")
            print(f"Received {len(results)} responses")

            for i, (query, result) in enumerate(zip(queries, results), 1):
                print(f"\nQuery {i}: {query[:50]}...")
                if isinstance(result, dict):
                    print(f"Response: {result.get('response', 'No response')[:100]}...")
                else:
                    print(f"Response: {result[:100]}...")

            return True
        else:
            print(f"✗ Response count mismatch: expected {len(queries)}, got {len(results)}")
            return False

    except Exception as e:
        print(f"✗ Batch prediction failed: {e}")
        return False


def test_dataframe_input(model):
    """
    Test prediction with DataFrame input.

    Args:
        model: Loaded MLflow model
    """
    print("\n" + "="*60)
    print("Test 4: DataFrame Input")
    print("="*60)

    try:
        df = pd.DataFrame({
            "query": [
                "What is ECU-750?",
                "Compare ECU-850 and ECU-850b"
            ]
        })

        print("Input DataFrame:")
        print(df)

        results = model.predict(df)

        if len(results) == len(df):
            print("✓ DataFrame prediction successful")
            return True
        else:
            print("✗ Response count mismatch")
            return False

    except Exception as e:
        print(f"✗ DataFrame prediction failed: {e}")
        return False


def test_string_input(model):
    """
    Test prediction with plain string input.

    Args:
        model: Loaded MLflow model
    """
    print("\n" + "="*60)
    print("Test 5: String Input")
    print("="*60)

    try:
        query = "What is the operating temperature range for ECU-850?"
        print(f"Query: {query}")

        result = model.predict(query)

        if isinstance(result, list) and len(result) > 0:
            print(f"Response: {result[0][:100]}...")
            print("✓ String input prediction successful")
            return True
        else:
            print("✗ Unexpected response format")
            return False

    except Exception as e:
        print(f"✗ String input prediction failed: {e}")
        return False


def test_error_handling(model):
    """
    Test error handling with invalid inputs.

    Args:
        model: Loaded MLflow model
    """
    print("\n" + "="*60)
    print("Test 6: Error Handling")
    print("="*60)

    test_cases = [
        ("Empty query", ""),
        ("Very long query", "x" * 5000),
        ("Non-string input", 123),
    ]

    passed = 0
    for name, test_input in test_cases:
        try:
            print(f"\nTesting: {name}")
            result = model.predict({"query": test_input})

            # Check if error is handled gracefully
            if isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], dict):
                    if result[0].get("status") == "error":
                        print(f"✓ Error handled gracefully")
                        passed += 1
                    else:
                        print(f"~ No error raised for {name}")
                else:
                    print(f"~ Unexpected format for {name}")
            else:
                print(f"~ Unexpected response for {name}")

        except Exception as e:
            print(f"✗ Unhandled exception: {e}")

    print(f"\nError handling: {passed}/{len(test_cases)} tests passed")
    return passed > 0


def test_performance(model):
    """
    Test prediction performance.

    Args:
        model: Loaded MLflow model
    """
    print("\n" + "="*60)
    print("Test 7: Performance")
    print("="*60)

    import time

    query = "What is ECU-850?"
    iterations = 5

    times = []
    for i in range(iterations):
        start_time = time.time()
        model.predict({"query": query})
        elapsed = time.time() - start_time
        times.append(elapsed)
        print(f"Iteration {i+1}: {elapsed:.2f}s")

    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)

    print(f"\nPerformance Statistics:")
    print(f"  Average: {avg_time:.2f}s")
    print(f"  Min: {min_time:.2f}s")
    print(f"  Max: {max_time:.2f}s")

    if avg_time < 10.0:
        print("✓ Performance meets requirement (<10s)")
        return True
    else:
        print("✗ Performance below requirement (>=10s)")
        return False


def run_all_tests(model_uri: str):
    """
    Run all tests.

    Args:
        model_uri: MLflow model URI
    """
    print("\n" + "="*60)
    print("MLflow Model Serving Test Suite")
    print("="*60)
    print(f"Model URI: {model_uri}")
    print("="*60)

    # Test 1: Load model
    model = test_model_loading(model_uri)
    if not model:
        print("\n✗ Cannot proceed without loaded model")
        return False

    # Test 2-7: Various prediction tests
    results = []

    # Single query
    results.append(test_single_query_prediction(
        model,
        "What is the maximum operating temperature for ECU-750?"
    ))

    # Batch prediction
    results.append(test_batch_prediction(
        model,
        [
            "What is ECU-750?",
            "What is ECU-850?",
            "Compare ECU-850 and ECU-850b"
        ]
    ))

    # DataFrame input
    results.append(test_dataframe_input(model))

    # String input
    results.append(test_string_input(model))

    # Error handling
    results.append(test_error_handling(model))

    # Performance
    results.append(test_performance(model))

    # Print summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    total = len(results)
    passed = sum(results)
    print(f"Total tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success rate: {passed/total*100:.1f}%")
    print("="*60)

    return passed >= total * 0.8  # 80% pass rate


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Test MLflow model serving")
    parser.add_argument(
        "--model-uri",
        type=str,
        default=None,
        help="MLflow model URI (default: latest model from ME_ECU_Assistant experiment)"
    )
    args = parser.parse_args()

    # Determine model URI
    if args.model_uri:
        model_uri = args.model_uri
    else:
        # Load latest model from experiment
        print("Fetching latest model from ME_ECU_Assistant experiment...")
        mlflow.set_tracking_uri("sqlite:///mlflow.db")
        experiment = mlflow.get_experiment_by_name("ME_ECU_Assistant")

        if not experiment:
            print("✗ Experiment 'ME_ECU_Assistant' not found")
            print("Please run 'python scripts/log_mlflow_model.py' first")
            return 1

        # Get latest run
        runs = mlflow.search_runs(experiment.experiment_id, order_by=["start_time DESC"], max_results=1)
        if len(runs) == 0:
            print("✗ No runs found in experiment")
            return 1

        run_id = runs.iloc[0]["run_id"]
        model_uri = f"runs:/{run_id}/ecu_agent_model"
        print(f"Latest run ID: {run_id}")

    # Run tests
    success = run_all_tests(model_uri)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
