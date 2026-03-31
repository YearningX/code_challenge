#!/usr/bin/env python3
"""
Quick Test Script for ME ECU Assistant API

Tests the API endpoints without running the full server.
"""

import sys
import json

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing imports...")
    try:
        import fastapi
        import uvicorn
        import mlflow
        from pydantic import BaseModel
        print("[OK] All imports successful")
        return True
    except ImportError as e:
        print(f"[FAIL] Import failed: {e}")
        return False

def test_model_loading():
    """Test if MLflow model can be loaded."""
    print("\nTesting MLflow model loading...")
    try:
        import mlflow

        MODEL_URI = "runs:/20f8fa846aea4dd183fa8bbe3739efb6/ecu_agent_model"
        print(f"Loading model from: {MODEL_URI}")

        model = mlflow.pyfunc.load_model(MODEL_URI)
        print("[OK] Model loaded successfully")

        # Test prediction
        print("\nTesting model prediction...")
        test_query = "What is ECU-750?"
        result = model.predict({"query": test_query})
        print(f"[OK] Prediction successful")
        print(f"  Query: {test_query}")
        print(f"  Response length: {len(str(result))} characters")

        return True
    except Exception as e:
        print(f"[FAIL] Model loading failed: {e}")
        return False

def test_api_module():
    """Test if api_server module can be imported."""
    print("\nTesting API server module...")
    try:
        sys.path.insert(0, '.')
        # Just test import, don't run the server
        import ast
        with open('api_server.py', 'r', encoding='utf-8') as f:
            code = f.read()
            ast.parse(code)
        print("[OK] API server code is valid Python")
        return True
    except Exception as e:
        print(f"[FAIL] API server validation failed: {e}")
        return False

def test_frontend_file():
    """Test if frontend HTML file exists and is valid."""
    print("\nTesting frontend file...")
    try:
        import os
        if not os.path.exists('index.html'):
            print("[FAIL] index.html not found")
            return False

        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()
            if len(content) < 1000:
                print("[FAIL] index.html seems too small")
                return False

        print(f"[OK] index.html found ({len(content)} characters)")
        return True
    except Exception as e:
        print(f"[FAIL] Frontend test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("ME ECU Assistant - Pre-flight Check")
    print("=" * 60)

    results = []

    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Model Loading", test_model_loading()))
    results.append(("API Module", test_api_module()))
    results.append(("Frontend File", test_frontend_file()))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{name:20s} {status}")

    print("-" * 60)
    print(f"Result: {passed}/{total} tests passed")

    if passed == total:
        print("\n[SUCCESS] All tests passed! You can start the server:")
        print("  python api_server.py")
        print("  or")
        print("  python start_server.py")
        return 0
    else:
        print("\n[ERROR] Some tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
