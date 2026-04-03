# Qwen API Key Configuration - Complete Guide

## ✅ Configuration Status

### Your New API Key
```
sk-your-qwen-api-key-here ✓
```

**Status:** Tested and valid

### Current Configuration

#### `.env` File ✓
```bash
LLM_PROVIDER=qwen
QWEN_API_KEY=sk-your-qwen-api-key-here
OPENAI_API_KEY=
```

#### Environment Variables in Container ✓
```bash
QWEN_API_KEY=sk-d5e7ff1fede04efea...ff7b
LLM_PROVIDER=qwen
```

#### MLflow Model ✓
Built with configuration:
```
Provider: qwen
Model: qwen-plus
Base URL: https://dashscope.aliyuncs.com/compatible-mode/v1
```

## ⚠️ Current Issue

Query returns 401 error trying to access OpenAI instead of Qwen.

**Root Cause:** LangChain's ChatOpenAI is not receiving the correct base_url parameter.

## 🔧 Solution

The issue is that ChatOpenAI needs explicit configuration. The model has been rebuilt with the correct code, but we need to verify the API key is being passed correctly.

### Quick Verification

Run this test to see the actual configuration:

```python
import os
from dotenv import load_dotenv
from me_ecu_agent.model_config import ModelConfig

load_dotenv()
config = ModelConfig.from_env()

print(f"Provider: {config.provider}")
print(f"Model: {config.model_name}")
print(f"Base URL: {config.base_url}")
print(f"API Key: {config.api_key[:20]}...")
```

Expected output:
```
Provider: qwen
Model: qwen-plus
Base URL: https://dashscope.aliyuncs.com/compatible-mode/v1
API Key: sk-d5e7ff1fede04efeab...
```

### If Issue Persists

The ChatOpenAI initialization in `graph.py` line 50 should receive these params:

```python
ChatOpenAI(
    model="qwen-plus",
    api_key="sk-your-qwen-api-key-here",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    temperature=0.0
)
```

## 📝 Files Modified

1. `.env` - New Qwen API key
2. `src/me_ecu_agent/model_config.py` - Auto provider selection
3. `src/me_ecu_agent/graph.py` - Uses ModelConfig
4. `src/me_ecu_agent/mlflow_model.py` - Passes ModelConfig
5. `web/docker-compose.yml` - Loads .env file

## 🧪 Testing Commands

```bash
# 1. Check configuration
python scripts/check_qwen_status.py

# 2. Test API directly
curl -X POST https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions \
  -H "Authorization: Bearer sk-your-qwen-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{"model": "qwen-plus", "messages": [{"role": "user", "content": "Hi"}]}'

# 3. Check container environment
docker-compose exec ecu-assistant-api env | grep QWEN

# 4. Test the service
curl -X POST http://localhost:18500/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is ECU-750?"}'
```

## 🚀 For Ubuntu Deployment

When deploying to Ubuntu server:

```bash
# 1. Copy code to server
scp -r . user@server:/path/to/

# 2. SSH to server
ssh user@server

# 3. Navigate to directory
cd /path/to/BOSCH_Code_Challenge

# 4. Verify .env file has correct QWEN_API_KEY
cat .env | grep QWEN

# 5. Rebuild MLflow model
python scripts/log_mlflow_model.py

# 6. Start container
cd web && docker-compose up -d

# 7. Check logs
docker-compose logs -f ecu-assistant-api | grep "Model provider"
```

## ✅ What's Working

- Qwen API Key is valid and tested ✓
- Environment variables are set correctly ✓
- Model configuration module detects Qwen ✓
- Docker container loads .env file ✓
- API health endpoint responds ✓

## ⚠️ What Needs Debugging

- LangChain ChatOpenAI configuration
- Verify base_url is being passed correctly
- Check if there's caching of old configuration

## 📞 Next Steps

1. **Verify local configuration** with test script above
2. **If local works**, the issue might be Docker volume mounting
3. **Rebuild without cache** to ensure fresh model

---

**Your API Key:** `sk-your-qwen-api-key-here`
**Status:** Configured, debugging final integration
**Last Updated:** 2026-04-03
