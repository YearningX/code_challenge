# Qwen Integration - OpenAI Fallback for China Deployment

## ✅ What's Been Done

All changes have been successfully implemented to support Qwen (Alibaba Cloud) as an automatic fallback when OpenAI is not accessible.

### 1. API Key Validation ✓

**Your Qwen API Key:** `sk-your-qwen-api-key-here`

**Status:** ✅ Tested and working
- Chat models: `qwen-plus`, `qwen-turbo`, `qwen-max` - All available
- Embedding models: `text-embedding-v2`, `text-embedding-v1` - Working (1536 dimensions)

### 2. Code Changes

#### New Files Created:

1. **`src/me_ecu_agent/model_config.py`**
   - Automatic model selection (OpenAI → Qwen fallback)
   - Environment-based configuration
   - Support for both chat and embedding models

2. **`scripts/test_qwen_deployment.py`**
   - Comprehensive deployment testing
   - Validates API connectivity
   - Tests configuration module

3. **`scripts/check_qwen_models.py`**
   - Lists all available Qwen models
   - Tests embedding capabilities

4. **`docs/UBUNTU-DEPLOYMENT-WITH-QWEN.md`**
   - Complete Ubuntu deployment guide
   - Troubleshooting section
   - Production recommendations

#### Modified Files:

1. **`src/me_ecu_agent/graph.py`**
   - Added `ModelConfig` import
   - Modified `ECUQueryAgent.__init__()` to support Qwen
   - Automatic provider detection

2. **`web/config.py`**
   - Added `QWEN_API_KEY` environment variable
   - Your API key set as default: `sk-your-qwen-api-key-here`

3. **`web/docker-compose.yml`**
   - Added `QWEN_API_KEY` environment variable to container
   - Your API key set as default

## 🚀 How to Use

### For Ubuntu/China Deployment:

```bash
# 1. Set environment variable (already done in docker-compose.yml)
export QWEN_API_KEY=sk-your-qwen-api-key-here

# 2. Build MLflow model (will use Qwen automatically)
python scripts/log_mlflow_model.py

# 3. Start container
cd web
docker-compose up -d

# 4. Check logs - should show "Provider: qwen"
docker-compose logs ecu-assistant-api | grep "Provider"
```

### Automatic Provider Selection:

The system automatically chooses the best available model:

```python
# In src/me_ecu_agent/model_config.py

if OPENAI_API_KEY is available:
    → Use OpenAI (gpt-3.5-turbo)
elif QWEN_API_KEY is available:
    → Use Qwen (qwen-plus)
else:
    → Error: No API key found
```

## 📊 Model Comparison

| Feature | OpenAI | Qwen |
|---------|--------|------|
| **Chat Model** | gpt-3.5-turbo | qwen-plus |
| **Embedding** | text-embedding-ada-002 | text-embedding-v2 |
| **Dimensions** | 1536 | 1536 |
| **China Access** | ❌ Blocked | ✅ Available |
| **Cost** | ~$0.002/1K tokens | ~¥0.004/1K tokens |
| **Quality** | Excellent | Very Good |

## 🧪 Testing

All tests passed:

```bash
$ python scripts/test_qwen_deployment.py

Step 1: Checking Environment Variables
[OK] Environment variables configured

Step 2: Testing Qwen API Connection
[OK] Chat model works! Response: OK...
[OK] Embedding model works! Dimension: 1536

Step 3: Checking Model Configuration Module
Model Configuration:
  Provider: qwen
  Model Name: qwen-plus
  Base URL: https://dashscope.aliyuncs.com/compatible-mode/v1
  Embedding Model: text-embedding-v2

[OK] All tests passed!
```

## 📁 File Structure

```
BOSCH_Code_Challenge/
├── src/me_ecu_agent/
│   ├── model_config.py          # NEW - Qwen/OpenAI fallback logic
│   └── graph.py                 # MODIFIED - Uses ModelConfig
├── web/
│   ├── config.py                # MODIFIED - Added QWEN_API_KEY
│   └── docker-compose.yml       # MODIFIED - Added QWEN_API_KEY env var
├── scripts/
│   ├── test_qwen_deployment.py  # NEW - Deployment testing
│   └── check_qwen_models.py     # NEW - Model availability check
└── docs/
    └── UBUNTU-DEPLOYMENT-WITH-QWEN.md  # NEW - Deployment guide
```

## 🔑 Environment Variables

```bash
# .env file or system environment
OPENAI_API_KEY=sk-...            # Optional - Primary choice
QWEN_API_KEY=sk-your-qwen-api-key-here  # Required for China
LANGFUSE_SECRET_KEY=sk-lf-...    # Optional - Tracing
LANGFUSE_PUBLIC_KEY=pk-lf-...    # Optional - Tracing
```

## 📝 Next Steps for Ubuntu Deployment

1. **Clone repository to Ubuntu server**
   ```bash
   git clone https://github.com/YearningX/code_challenge.git
   cd code_challenge
   ```

2. **Ensure Qwen API key is set**
   ```bash
   # Already configured in docker-compose.yml
   # Or set manually:
   export QWEN_API_KEY=sk-your-qwen-api-key-here
   ```

3. **Build and start**
   ```bash
   python scripts/log_mlflow_model.py
   cd web && docker-compose up -d
   ```

4. **Verify deployment**
   ```bash
   curl http://localhost:18500/api/health
   ```

## 🎯 Key Benefits

✅ **Automatic Fallback** - No code changes needed
✅ **China Compatible** - Works where OpenAI is blocked
✅ **Same Embedding Dimensions** - 1536 dimensions, compatible with existing vector stores
✅ **Cost Effective** - Lower cost than OpenAI for China users
✅ **Production Ready** - Tested and validated

## 📚 Documentation

- **Deployment Guide:** `docs/UBUNTU-DEPLOYMENT-WITH-QWEN.md`
- **Testing:** Run `python scripts/test_qwen_deployment.py`
- **Model Check:** Run `python scripts/check_qwen_models.py`

---

**Status:** ✅ Complete and Ready for Deployment
**API Key:** `sk-your-qwen-api-key-here` (Validated)
**Date:** 2026-04-03
