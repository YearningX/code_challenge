# -*- coding: utf-8 -*-
"""Check available Qwen models including embedding models"""
import requests
import json

api_key = "sk-your-qwen-api-key-here"

print("=" * 70)
print("Checking Qwen/DashScope Available Models")
print("=" * 70)

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Test 1: Chat models
print("\n[1/3] Testing Chat Models (qwen-plus, qwen-turbo, qwen-max)")
print("-" * 70)

chat_models = ["qwen-plus", "qwen-turbo", "qwen-max", "qwen-long"]

for model in chat_models:
    try:
        data = {
            "model": model,
            "messages": [{"role": "user", "content": "hi"}],
            "max_tokens": 5
        }
        response = requests.post(
            "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=10
        )

        if response.status_code == 200:
            print(f"  [OK] {model} - Available")
        else:
            print(f"  [X] {model} - Not available (Status: {response.status_code})")
    except Exception as e:
        print(f"  [X] {model} - Error: {str(e)[:50]}")

# Test 2: Embedding models (OpenAI compatible endpoint)
print("\n[2/3] Testing Embedding Models (OpenAI Compatible)")
print("-" * 70)

embedding_models = [
    "text-embedding-v3",
    "text-embedding-v2",
    "text-embedding-v1",
    "text-embedding-async-v2",
    "text-embedding-async-v1"
]

for model in embedding_models:
    try:
        data = {
            "model": model,
            "input": "test embedding",
            "dimensions": 1536  # Same as OpenAI's ada-002
        }
        response = requests.post(
            "https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings",
            headers=headers,
            json=data,
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            embedding_dim = len(result.get('data', [{}])[0].get('embedding', []))
            print(f"  [OK] {model} - Available (dim: {embedding_dim})")
        else:
            print(f"  [X] {model} - Not available (Status: {response.status_code})")
    except Exception as e:
        print(f"  [X] {model} - Error: {str(e)[:50]}")

# Test 3: Native DashScope embedding endpoint
print("\n[3/3] Testing Native DashScope Embedding API")
print("-" * 70)

try:
    data = {
        "model": "text-embedding-v3",
        "input": {
            "texts": ["test embedding"]
        },
        "parameters": {
            "text_type": "document"
        }
    }
    response = requests.post(
        "https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/text-embedding",
        headers=headers,
        json=data,
        timeout=10
    )

    if response.status_code == 200:
        result = response.json()
        print("  [OK] Native API - Available")
        print(f"  Model: text-embedding-v3")
        print(f"  Output: {json.dumps(result, ensure_ascii=False)[:200]}...")
    else:
        print(f"  [X] Native API - Status: {response.status_code}")
        print(f"  Response: {response.text[:200]}")
except Exception as e:
    print(f"  [X] Native API - Error: {str(e)[:100]}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("Available models for OpenAI replacement:")
print("  - Chat: qwen-plus (recommended), qwen-turbo, qwen-max")
print("  - Embedding: text-embedding-v3, text-embedding-v2")
print("\nRecommended configuration:")
print("  - OpenAI Base URL: https://dashscope.aliyuncs.com/compatible-mode/v1")
print("  - Chat Model: qwen-plus")
print("  - Embedding Model: text-embedding-v3")
print("=" * 70)
