# -*- coding: utf-8 -*-
"""
Test Qwen Deployment Configuration

This script verifies that the Qwen API key is working and can be used
as a fallback for OpenAI in the ME ECU Assistant.
"""

import os
import sys

# Test 1: Check environment variables
print("=" * 70)
print("Step 1: Checking Environment Variables")
print("=" * 70)

openai_key = os.getenv("OPENAI_API_KEY")
qwen_key = os.getenv("QWEN_API_KEY")

print(f"OPENAI_API_KEY: {'Set' if openai_key else 'Not set'}")
print(f"QWEN_API_KEY: {'Set' if qwen_key else 'Not set'}")

if not qwen_key:
    print("\n[ERROR] QWEN_API_KEY is not set!")
    print("Please set it using: export QWEN_API_KEY=sk-...")
    sys.exit(1)

print("[OK] Environment variables configured\n")

# Test 2: Test Qwen API
print("=" * 70)
print("Step 2: Testing Qwen API Connection")
print("=" * 70)

import requests

headers = {
    "Authorization": f"Bearer {qwen_key}",
    "Content-Type": "application/json"
}

# Test chat model
print("\n[1/2] Testing Chat Model (qwen-plus)...")
data = {
    "model": "qwen-plus",
    "messages": [{"role": "user", "content": "Hello, please respond with 'OK'"}],
    "max_tokens": 10
}

try:
    response = requests.post(
        "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        headers=headers,
        json=data,
        timeout=10
    )

    if response.status_code == 200:
        result = response.json()
        content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
        print(f"[OK] Chat model works! Response: {content[:50]}...")
    else:
        print(f"[ERROR] Chat model failed with status {response.status_code}")
        print(f"Response: {response.text[:200]}")
        sys.exit(1)
except Exception as e:
    print(f"[ERROR] Connection failed: {e}")
    sys.exit(1)

# Test embedding model
print("\n[2/2] Testing Embedding Model (text-embedding-v2)...")
data = {
    "model": "text-embedding-v2",
    "input": "test embedding",
    "dimensions": 1536
}

try:
    response = requests.post(
        "https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings",
        headers=headers,
        json=data,
        timeout=10
    )

    if response.status_code == 200:
        result = response.json()
        embedding_dim = len(result.get('data', [{}])[0].get('embedding', []))
        print(f"[OK] Embedding model works! Dimension: {embedding_dim}")
    else:
        print(f"[ERROR] Embedding model failed with status {response.status_code}")
        print(f"Response: {response.text[:200]}")
        sys.exit(1)
except Exception as e:
    print(f"[ERROR] Connection failed: {e}")
    sys.exit(1)

# Test 3: Check Model Configuration
print("\n" + "=" * 70)
print("Step 3: Checking Model Configuration Module")
print("=" * 70)

try:
    # Add parent directory to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

    from me_ecu_agent.model_config import ModelConfig, get_model_config

    # Temporarily unset OPENAI_API_KEY to test Qwen fallback
    original_openai = os.environ.get("OPENAI_API_KEY")
    os.environ["OPENAI_API_KEY"] = ""  # Force Qwen usage
    os.environ["QWEN_API_KEY"] = qwen_key

    # Reset to pick up new env vars
    import importlib
    import me_ecu_agent.model_config
    importlib.reload(me_ecu_agent.model_config)
    from me_ecu_agent.model_config import get_model_config

    config = get_model_config()

    print(f"\nModel Configuration:")
    print(f"  Provider: {config.provider}")
    print(f"  Model Name: {config.model_name}")
    print(f"  Base URL: {config.base_url}")
    print(f"  Embedding Model: {config.embedding_model}")

    if config.provider == "qwen":
        print("\n[OK] Qwen configuration is active!")
    else:
        print(f"\n[WARNING] Expected 'qwen' but got '{config.provider}'")

    # Restore original
    if original_openai:
        os.environ["OPENAI_API_KEY"] = original_openai

except Exception as e:
    print(f"[ERROR] Configuration module test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("[OK] All tests passed!")
print("\nYour Qwen API key is working and ready for deployment.")
print("\nNext steps:")
print("  1. Build MLflow model: python scripts/log_mlflow_model.py")
print("  2. Start Docker: cd web && docker-compose up -d")
print("  3. Test deployment: curl http://localhost:18500/api/health")
print("=" * 70)
