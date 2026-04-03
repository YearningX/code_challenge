"""
Test Qwen API Key availability
"""
import requests
import json

def test_qwen_api():
    """Test if the Qwen API key is valid"""

    api_key = "sk-your-qwen-api-key-here"

    # Test with DashScope (Alibaba Cloud) - OpenAI compatible endpoint
    urls = [
        "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
    ]

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Test OpenAI compatible endpoint
    print("=" * 60)
    print("Testing Qwen API Key...")
    print("=" * 60)

    # Try qwen-plus model
    test_data = {
        "model": "qwen-plus",
        "messages": [
            {"role": "user", "content": "Hello, this is a test."}
        ],
        "max_tokens": 10
    }

    try:
        print("\n[1/2] Testing DashScope OpenAI-compatible endpoint...")
        response = requests.post(
            "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            headers=headers,
            json=test_data,
            timeout=10
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✓ API Key is VALID!")
            print(f"Model: qwen-plus")
            print(f"Response: {result.get('choices', [{}])[0].get('message', {}).get('content', 'N/A')}")
            return True
        else:
            print(f"✗ Request failed with status {response.status_code}")
            print(f"Response: {response.text[:200]}")

    except Exception as e:
        print(f"✗ Error: {e}")

    # Try alternative endpoint
    try:
        print("\n[2/2] Testing alternative DashScope endpoint...")
        alt_data = {
            "model": "qwen-plus",
            "input": {
                "messages": [
                    {"role": "user", "content": "Hello"}
                ]
            }
        }
        response = requests.post(
            "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
            headers=headers,
            json=alt_data,
            timeout=10
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✓ API Key is VALID!")
            print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)[:300]}")
            return True
        else:
            print(f"✗ Request failed with status {response.status_code}")
            print(f"Response: {response.text[:200]}")

    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("✗ API Key test failed")
    print("\nPossible reasons:")
    print("1. Invalid API Key")
    print("2. Network connectivity issues")
    print("3. API endpoint changed")
    print("4. Insufficient permissions/quota")
    print("\nPlease check:")
    print("- API Key is correct")
    print("- Account has sufficient quota")
    print("- Network can access dashscope.aliyuncs.com")

    return False

if __name__ == "__main__":
    is_valid = test_qwen_api()
    exit(0 if is_valid else 1)
