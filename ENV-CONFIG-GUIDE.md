# How to Configure LLM Provider with .env File

This guide explains how to configure your ME ECU Assistant to use either **OpenAI** or **Qwen** (Alibaba Cloud) as the LLM provider.

## 📋 Quick Setup

### Step 1: Copy Example Configuration

```bash
cp .env.example .env
```

### Step 2: Edit `.env` File

Open `.env` in your text editor and choose your provider:

## 🔧 Configuration Options

### Option 1: Use OpenAI (International)

For deployment outside China where OpenAI is accessible:

```bash
# .env file
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-abc123...your-key-here
QWEN_API_KEY=
```

**To get OpenAI API key:**
1. Visit https://platform.openai.com/api-keys
2. Create a new API key
3. Copy and paste into `.env` file

### Option 2: Use Qwen (China)

For deployment in China where OpenAI is blocked:

```bash
# .env file
LLM_PROVIDER=qwen
OPENAI_API_KEY=
QWEN_API_KEY=sk-your-qwen-api-key-here
```

**Your Qwen API key is already provided and tested!**

### Option 3: Auto-Detect (Recommended)

System automatically uses OpenAI if available, otherwise falls back to Qwen:

```bash
# .env file
LLM_PROVIDER=auto
OPENAI_API_KEY=sk-proj-abc123...
QWEN_API_KEY=sk-your-qwen-api-key-here
```

## 📊 Provider Comparison

| Feature | OpenAI | Qwen |
|---------|--------|------|
| **Model** | gpt-3.5-turbo | qwen-plus |
| **China Access** | ❌ Blocked | ✅ Available |
| **Quality** | Excellent | Very Good |
| **Cost** | ~$0.002/1K tokens | ~¥0.004/1K tokens |
| **Speed** | 2-3s | 2-3s |

## 🧪 Test Your Configuration

After editing `.env`, test the configuration:

```bash
# Test current configuration
python scripts/test_qwen_deployment.py

# Expected output should show:
# Provider: openai  OR  Provider: qwen
# (depending on your LLM_PROVIDER setting)
```

## 🚀 Deployment

After configuring `.env`:

```bash
# 1. Build MLflow model
python scripts/log_mlflow_model.py

# 2. Start Docker container
cd web
docker-compose up -d

# 3. Check logs to verify provider
docker-compose logs ecu-assistant-api | grep "Provider"
```

## 📝 Complete .env Example

```bash
# ==================================================
# LLM Configuration - Choose ONE provider
# ==================================================

# Provider Selection: auto, openai, or qwen
LLM_PROVIDER=auto

# Option 1: OpenAI (for international deployment)
OPENAI_API_KEY="sk-proj-abc123...your-key-here"

# Option 2: Qwen/Alibaba Cloud (for China deployment)
QWEN_API_KEY="sk-your-qwen-api-key-here"

# ==================================================
# Langfuse Tracing (Optional)
# ==================================================
LANGFUSE_SECRET_KEY="sk-your-langfuse-secret-key-here"
LANGFUSE_PUBLIC_KEY="pk-your-langfuse-public-key-here"
LANGFUSE_BASE_URL="https://langfuse.cccoder.top"

# ==================================================
# Server Configuration
# ==================================================
API_HOST=0.0.0.0
API_PORT=18500
API_RELOAD=false
```

## ❓ Common Issues

### Issue: "Provider not selected correctly"

**Solution:** Check your `.env` file for typos in `LLM_PROVIDER` value. Must be exactly: `auto`, `openai`, or `qwen`

### Issue: "API key error"

**Solution:**
- Ensure API keys are not wrapped in extra quotes
- Remove any spaces around `=` signs
- Verify key is correct and active

### Issue: "Want to switch providers"

**Solution:**
1. Edit `.env` file
2. Change `LLM_PROVIDER` value
3. Rebuild model: `python scripts/log_mlflow_model.py`
4. Restart container: `cd web && docker-compose restart`

## 🔒 Security Best Practices

✅ **DO:**
- Keep `.env` file private (never commit to Git)
- Use different API keys for dev/prod
- Rotate API keys regularly

❌ **DON'T:**
- Share `.env` file or API keys
- Commit `.env` to version control
- Use production keys in development

## 📚 Additional Resources

- **Full Deployment Guide:** `docs/UBUNTU-DEPLOYMENT-WITH-QWEN.md`
- **Qwen Integration Details:** `QWEN-INTEGRATION.md`
- **Testing:** `scripts/test_qwen_deployment.py`

---

**Need Help?** Check the logs: `docker-compose logs ecu-assistant-api | grep -i provider`
