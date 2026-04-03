# -*- coding: utf-8 -*-
"""Test Qwen API Key"""
import requests
import json

api_key = "sk-your-qwen-api-key-here"

print("Testing Qwen API Key via DashScope...")
print("=" * 60)

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

data = {
    "model": "qwen-plus",
    "messages": [
        {"role": "user", "content": "Hello, this is a test."}
    ],
    "max_tokens": 10
}

try:
    response = requests.post(
        "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        headers=headers,
        json=data,
        timeout=10
    )

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print("[OK] API Key is VALID!")
        print(f"Model: qwen-plus")
        content = result.get('choices', [{}])[0].get('message', {}).get('content', 'N/A')
        print(f"Response: {content}")
        print("=" * 60)
        print("SUCCESS: Qwen API is ready to use!")
    else:
        print(f"[ERROR] Status {response.status_code}")
        print(f"Response: {response.text[:200]}")
        exit(1)

except Exception as e:
    print(f"[ERROR] {e}")
    exit(1)
