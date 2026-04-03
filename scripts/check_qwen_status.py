# -*- coding: utf-8 -*-
"""
Check Qwen Configuration Status

Verify that the new Qwen API key is properly configured and working.
"""

import os
import sys
import requests
from dotenv import load_dotenv

print("=" * 70)
print("Qwen Configuration Status Check")
print("=" * 70)

# Load .env file
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

# Step 1: Check .env file
print("\n[1/4] Checking .env file configuration...")
print("-" * 70)

qwen_key = os.getenv("QWEN_API_KEY", "").strip('"').strip("'")
llm_provider = os.getenv("LLM_PROVIDER", "auto").lower()
openai_key = os.getenv("OPENAI_API_KEY", "").strip('"').strip("'")

print(f"LLM_PROVIDER: {llm_provider}")
print(f"QWEN_API_KEY: {'Set' if qwen_key and qwen_key != 'sk-your-qwen-api-key-here' else 'Not set'}")
print(f"OPENAI_API_KEY: {'Set' if openai_key and openai_key != 'sk-your-openai-api-key-here' else 'Not set'}")

if not qwen_key or qwen_key == "sk-your-qwen-api-key-here":
    print("\n[ERROR] QWEN_API_KEY not configured in .env file!")
    sys.exit(1)

print(f"\nQWEN_API_KEY: {qwen_key[:20]}...{qwen_key[-4:]}")

# Step 2: Test API key
print("\n[2/4] Testing Qwen API key...")
print("-" * 70)

headers = {
    "Authorization": f"Bearer {qwen_key}",
    "Content-Type": "application/json"
}

data = {
    "model": "qwen-plus",
    "messages": [{"role": "user", "content": "Test"}],
    "max_tokens": 5
}

try:
    response = requests.post(
        "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        headers=headers,
        json=data,
        timeout=10
    )

    if response.status_code == 200:
        print("[OK] Qwen API key is valid and working!")
    else:
        print(f"[ERROR] API key test failed with status {response.status_code}")
        print(f"Response: {response.text[:200]}")
        sys.exit(1)
except Exception as e:
    print(f"[ERROR] Connection failed: {e}")
    sys.exit(1)

# Step 3: Check model configuration
print("\n[3/4] Checking model configuration module...")
print("-" * 70)

try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from me_ecu_agent.model_config import ModelConfig

    config = ModelConfig.from_env()

    print(f"Provider: {config.provider}")
    print(f"Model: {config.model_name}")
    print(f"Base URL: {config.base_url}")
    print(f"Embedding Model: {config.embedding_model}")

    if config.provider == "qwen":
        print("\n[OK] Model configured to use Qwen!")
    else:
        print(f"\n[WARNING] Provider is '{config.provider}', expected 'qwen'")

except Exception as e:
    print(f"[ERROR] Configuration check failed: {e}")
    sys.exit(1)

# Step 4: Test API endpoint
print("\n[4/4] Testing local API endpoint...")
print("-" * 70)

try:
    response = requests.get("http://localhost:18500/api/health", timeout=5)

    if response.status_code == 200:
        result = response.json()
        print("[OK] API is running!")
        print(f"Status: {result.get('status')}")
        print(f"Model loaded: {result.get('model_loaded')}")
    else:
        print(f"[ERROR] API returned status {response.status_code}")
except Exception as e:
    print(f"[WARNING] Could not connect to API: {e}")
    print("This is normal if Docker container is not running.")

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("[OK] Qwen API key is configured correctly!")
print(f"\nConfiguration:")
print(f"  - Provider: qwen")
print(f"  - Model: qwen-plus")
print(f"  - API Key: {qwen_key[:20]}...{qwen_key[-4:]}")
print(f"  - Base URL: https://dashscope.aliyuncs.com/compatible-mode/v1")

print("\nNext steps:")
print("  1. Rebuild MLflow model: python scripts/log_mlflow_model.py")
print("  2. Restart Docker: cd web && docker-compose restart")
print("  3. Test query: curl -X POST http://localhost:18500/api/query ...")

print("\n" + "=" * 70)
