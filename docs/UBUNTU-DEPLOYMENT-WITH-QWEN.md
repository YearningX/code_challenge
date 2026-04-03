# Ubuntu Server Deployment Guide with Qwen Fallback

This guide explains how to deploy the ME ECU Assistant on an Ubuntu server using Qwen (Alibaba Cloud) as a fallback when OpenAI is not accessible.

## 📋 Prerequisites

- Ubuntu 20.04+ or similar Linux distribution
- Docker and Docker Compose installed
- At least 4GB RAM and 10GB disk space
- Qwen API Key from Alibaba Cloud DashScope

## 🔑 Get Qwen API Key

1. Visit [Alibaba Cloud DashScope](https://dashscope.aliyun.com/)
2. Register/Login to your account
3. Navigate to API Key Management
4. Create a new API Key
5. Save the key (format: `sk-xxxxxxxxxxxxxxxx`)

**Your provided API Key:** `sk-your-qwen-api-key-here` ✓ (Tested and working)

## 📦 Quick Deployment Steps

### Step 1: Clone Repository

```bash
git clone https://github.com/YearningX/code_challenge.git
cd code_challenge
```

### Step 2: Configure Environment Variables

Create a `.env` file in the project root:

```bash
cat > .env << EOF
# LLM Configuration (Choose one)
# Option 1: Use OpenAI (if accessible)
OPENAI_API_KEY=your-openai-api-key-here

# Option 2: Use Qwen (for China deployment - recommended)
QWEN_API_KEY=sk-your-qwen-api-key-here

# Langfuse Tracing (Optional)
LANGFUSE_SECRET_KEY=sk-your-langfuse-secret-key-here
LANGFUSE_PUBLIC_KEY=pk-your-langfuse-public-key-here
LANGFUSE_BASE_URL=https://langfuse.cccoder.top

# Server Configuration
API_HOST=0.0.0.0
API_PORT=18500
EOF
```

### Step 3: Build MLflow Model

```bash
# Install Python dependencies
pip install -r requirements.txt

# Build MLflow model with Qwen support
python scripts/log_mlflow_model.py
```

### Step 4: Start Docker Container

```bash
cd web
docker-compose up -d
```

### Step 5: Verify Deployment

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f ecu-assistant-api

# Test API endpoint
curl http://localhost:18500/api/health
```

Access the web interface at: `http://your-server-ip:18500`

## 🔧 Configuration Details

### Model Selection Priority

The system automatically selects the best available LLM:

1. **Primary:** OpenAI (if `OPENAI_API_KEY` is set)
   - Model: `gpt-3.5-turbo`
   - Embedding: `text-embedding-ada-002`

2. **Fallback:** Qwen (if `QWEN_API_KEY` is set)
   - Model: `qwen-plus`
   - Embedding: `text-embedding-v2`

**Automatic Detection:**
- If `OPENAI_API_KEY` is present and valid → Use OpenAI
- Otherwise → Use Qwen

### Available Qwen Models

| Model | Description | Use Case |
|-------|-------------|----------|
| `qwen-plus` | Balanced performance/ cost | **Recommended** |
| `qwen-turbo` | Faster, lower cost | Simple queries |
| `qwen-max` | Highest quality | Complex reasoning |
| `qwen-long` | Long context | Long documents |

## 🧪 Testing Qwen Integration

### Test API Key

```bash
python scripts/check_qwen_models.py
```

Expected output:
```
[OK] qwen-plus - Available
[OK] qwen-turbo - Available
[OK] qwen-max - Available
[OK] text-embedding-v2 - Available (dim: 1536)
```

### Test Full System

```bash
# Test with sample query
curl -X POST http://localhost:18500/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the specifications of ECU-750?"}'
```

## 🔒 Security Considerations

1. **Never commit API keys to Git**
   - Use environment variables
   - Add `.env` to `.gitignore`

2. **Protect API Keys**
   - Restrict API key permissions in DashScope console
   - Set usage limits and quotas
   - Monitor usage regularly

3. **Network Security**
   - Use firewall to restrict access
   - Consider reverse proxy with HTTPS (see nginx in docker-compose.yml)

## 🐛 Troubleshooting

### Issue: "No API key found"

**Solution:**
```bash
# Check if QWEN_API_KEY is set
echo $QWEN_API_KEY

# Set it manually
export QWEN_API_KEY=sk-your-qwen-api-key-here

# Or add to .env file
echo "QWEN_API_KEY=sk-your-qwen-api-key-here" >> .env
```

### Issue: "Cannot connect to DashScope"

**Solution:**
- Check internet connectivity
- Verify firewall allows HTTPS (port 443)
- Test API endpoint: `curl -I https://dashscope.aliyuncs.com`

### Issue: "Model not found"

**Solution:**
- Verify model name in logs
- Check model availability: `python scripts/check_qwen_models.py`
- Try alternative model (e.g., `qwen-turbo` instead of `qwen-plus`)

### Issue: "Container exits immediately"

**Solution:**
```bash
# Check logs
docker-compose logs ecu-assistant-api

# Common fixes:
# 1. Rebuild model
python scripts/log_mlflow_model.py

# 2. Restart container
docker-compose restart

# 3. Check MLflow model path
ls -la models/ecu_agent_model_local/ecu_agent_model/
```

## 📊 Performance Comparison

| Metric | OpenAI (gpt-3.5-turbo) | Qwen (qwen-plus) |
|--------|----------------------|------------------|
| Response Time | ~2-3s | ~2-3s |
| Quality | Excellent | Very Good |
| Cost | ~$0.002/1K tokens | ~¥0.004/1K tokens |
| China Access | ❌ Blocked | ✅ Available |

## 🎯 Production Recommendations

### For China Deployment:

1. **Use Qwen as primary:**
   ```bash
   # In .env file
   OPENAI_API_KEY=
   QWEN_API_KEY=sk-your-qwen-api-key-here
   ```

2. **Set resource limits:**
   ```yaml
   # In docker-compose.yml
   services:
     ecu-assistant-api:
       deploy:
         resources:
           limits:
             cpus: '2'
             memory: 4G
   ```

3. **Enable auto-restart:**
   ```yaml
   restart: unless-stopped
   ```

4. **Monitor logs:**
   ```bash
   # Follow logs in real-time
   docker-compose logs -f ecu-assistant-api | grep -i qwen
   ```

## 📝 Environment Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key | - | No* |
| `QWEN_API_KEY` | Qwen/DashScope API key | - | No* |
| `LANGFUSE_SECRET_KEY` | Langfuse secret | - | No |
| `LANGFUSE_PUBLIC_KEY` | Langfuse public key | - | No |
| `API_HOST` | Server bind address | 0.0.0.0 | No |
| `API_PORT` | Server port | 18500 | No |

\* At least one of `OPENAI_API_KEY` or `QWEN_API_KEY` must be provided.

## 🎓 Additional Resources

- [Qwen Documentation](https://help.aliyun.com/zh/dashscope/)
- [LangChain Qwen Integration](https://python.langchain.com/docs/integrations/chat/qwen/)
- [Project README](../README.md)

## ✅ Deployment Checklist

- [ ] Qwen API key obtained and tested
- [ ] Repository cloned to server
- [ ] `.env` file configured with API keys
- [ ] MLflow model built successfully
- [ ] Docker container started
- [ ] Health check endpoint responds
- [ ] Web interface accessible
- [ ] Test query executed successfully
- [ ] Logs show correct model provider (Qwen)
- [ ] Firewall configured (if needed)
- [ ] Auto-restart enabled

---

**Last Updated:** 2026-04-03
**Maintainer:** Bosch Code Challenge Team
