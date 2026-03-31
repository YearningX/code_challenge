"""
Quick MLflow Model Test

Simple test to verify MLflow model loading and prediction.
"""

import sys
import mlflow.pyfunc


def main():
    """Test MLflow model."""
    model_uri = "runs:/20f8fa846aea4dd183fa8bbe3739efb6/ecu_agent_model"

    print("="*60)
    print("MLflow Model Quick Test")
    print("="*60)
    print(f"Loading model from: {model_uri}")

    try:
        # Load model
        model = mlflow.pyfunc.load_model(model_uri)
        print("[OK] Model loaded successfully")

        # Test single query
        print("\n" + "="*60)
        print("Test 1: Single Query")
        print("="*60)
        query = "What is ECU-850?"
        print(f"Query: {query}")

        result = model.predict({"query": query})
        print(f"Response: {result[0] if isinstance(result, list) and len(result) > 0 else result}")

        # Test batch queries
        print("\n" + "="*60)
        print("Test 2: Batch Queries")
        print("="*60)
        queries = [
            {"query": "What is ECU-750?"},
            {"query": "Compare ECU-850 and ECU-850b"}
        ]
        print(f"Queries: {[q['query'] for q in queries]}")

        results = model.predict(queries)
        for i, result in enumerate(results, 1):
            # Handle both string and dict responses
            if isinstance(result, str):
                response = result
            elif isinstance(result, dict):
                response = result.get('response', str(result))
            elif isinstance(result, list) and len(result) > 0:
                response = result[0]
            else:
                response = str(result)
            print(f"\nResult {i}:")
            print(f"  {response[:200]}...")

        print("\n" + "="*60)
        print("[SUCCESS] All tests passed!")
        print("="*60)
        return 0

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
