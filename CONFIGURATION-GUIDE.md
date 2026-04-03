# ECU Agent - Configuration Guide

## 📋 Configuration System Overview

Your ECU Agent now supports complete configuration through the `.env` file, allowing independent selection of LLM and Embeddings providers.

## 🎯 Configuration Options

### Current Status

✅ **LLM (Chat Model)**: Using Qwen (`qwen-plus`) - Fully functional
✅ **Embeddings (Embedding Model)**: Using custom Qwen embeddings - Fully functional
✅ **Pure Qwen Solution**: Complete Qwen integration working, no OpenAI access needed

## 🔧 Recommended Configuration Options

### Option 1: Pure Qwen (Current Implementation - Recommended)

**Configuration**: Use Qwen for both LLM and Embeddings

**Advantages**:
- ✓ No OpenAI access required
- ✓ 63% cost savings vs pure OpenAI (¥35/month vs ¥94/month)
- ✓ Perfect for China deployment
- ✓ Full customization control

**.env Configuration**:
```bash
# LLM Configuration - Use Qwen
LLM_PROVIDER=qwen
QWEN_API_KEY=sk-your-qwen-api-key-here
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# Embeddings Configuration - Use Qwen
EMBEDDINGS_PROVIDER=qwen
QWEN_API_KEY=sk-your-qwen-api-key-here
```

**Result**:
- Query Analysis: Qwen (qwen-plus)
- Response Synthesis: Qwen (qwen-plus)
- Vector Retrieval: Qwen (text-embedding-v2)

---

### Option 2: Hybrid Configuration (OpenAI + Qwen)

**Configuration**: Use Qwen for LLM, OpenAI for Embeddings

**Advantages**:
- ✓ Leverage existing OpenAI-created vector stores
- ✓ Lower latency for embeddings
- ✓ Cost-effective (LLM is the main cost)

**.env Configuration**:
```bash
# LLM Configuration - Use Qwen
LLM_PROVIDER=qwen
QWEN_API_KEY=sk-your-qwen-api-key-here

# Embeddings Configuration - Use OpenAI
EMBEDDINGS_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-api-key-here
```

**Result**:
- Query Analysis: Qwen (qwen-plus)
- Response Synthesis: Qwen (qwen-plus)
- Vector Retrieval: OpenAI (text-embedding-ada-002)

**Cost**: ~¥34/month (10K queries)

---

### Option 3: Pure OpenAI

**Configuration**: Use OpenAI for both LLM and Embeddings

**.env Configuration**:
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-api-key-here

EMBEDDINGS_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-api-key-here
```

**Cost**: ~¥94/month (10K queries)

---

## 🚀 Quick Start (Pure Qwen - Current Setup)

### Step 1: Verify .env Configuration

```bash
cd F:/projects/BOSCH_Code_Challenge
cat .env
```

Expected content:
```bash
LLM_PROVIDER=qwen
QWEN_API_KEY=your-api-key-placeholder
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
EMBEDDINGS_PROVIDER=qwen
```

### Step 2: Start Service

```bash
cd web
docker-compose restart
```

### Step 3: Verify Configuration

```bash
# Check logs for provider information
docker-compose logs ecu-assistant-api | grep "Provider:"
```

Expected output:
```
Provider: qwen
Model: qwen-plus
Base URL: https://dashscope.aliyuncs.com/compatible-mode/v1
```

### Step 4: Test Query

```bash
curl -X POST http://localhost:18500/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is ECU-750?"}'
```

---

## 📊 Cost Analysis

### Monthly Cost Comparison (10,000 queries/month)

| Configuration | LLM Cost | Embeddings Cost | Total Cost | Savings |
|--------------|----------|----------------|-----------|---------|
| **Pure Qwen** | ¥24 | ¥10.5 | **¥35** | **63%** |
| Hybrid (Qwen LLM + OpenAI Emb) | ¥24 | ¥10 | **¥34** | 64% |
| Pure OpenAI | ¥84 | ¥10 | **¥94** | baseline |

### Cost Breakdown

**Qwen API Pricing**:
- `qwen-plus`: ¥0.004/1K tokens
- `text-embedding-v2`: ¥0.0007/1K tokens

**OpenAI API Pricing**:
- `gpt-3.5-turbo`: $0.002/1K tokens ≈ ¥0.014/1K tokens
- `text-embedding-ada-002`: $0.0001/1K tokens ≈ ¥0.0007/1K tokens

---

## 🎓 Configuration Details

### Environment Variables

#### LLM Configuration

```bash
# Provider Selection
LLM_PROVIDER=auto|openai|qwen

# OpenAI (if LLM_PROVIDER=openai)
OPENAI_API_KEY=sk-...

# Qwen (if LLM_PROVIDER=qwen)
QWEN_API_KEY=sk-...
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

#### Embeddings Configuration

```bash
# Provider Selection
EMBEDDINGS_PROVIDER=auto|openai|qwen

# OpenAI (if EMBEDDINGS_PROVIDER=openai)
OPENAI_API_KEY=sk-...

# Qwen (if EMBEDDINGS_PROVIDER=qwen)
QWEN_API_KEY=sk-...
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

### Provider Selection Logic

#### Auto Mode (LLM_PROVIDER=auto)

1. Try OpenAI if `OPENAI_API_KEY` is set
2. Fallback to Qwen if `QWEN_API_KEY` is set
3. Raise error if neither is available

#### Forced Mode

- `LLM_PROVIDER=openai`: Use OpenAI only
- `LLM_PROVIDER=qwen`: Use Qwen only

Same logic applies to `EMBEDDINGS_PROVIDER`.

---

## 🔍 Troubleshooting

### Issue 1: "No API key found"

**Solution**: Configure at least one API key in `.env`:
```bash
# For Qwen
QWEN_API_KEY=sk-your-key

# For OpenAI
OPENAI_API_KEY=sk-your-key
```

### Issue 2: "Provider not usable"

**Solution**: Verify API key is valid:
```bash
# Test Qwen key
curl -X POST https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions \
  -H "Authorization: Bearer YOUR_QWEN_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "qwen-plus", "messages": [{"role": "user", "content": "Hi"}]}'
```

### Issue 3: "Model loading failed"

**Solution**: Check container logs:
```bash
docker-compose logs ecu-assistant-api | grep -E "(ERROR|WARNING|Provider)"
```

### Issue 4: Embeddings API Error

**Solution**: Ensure `EMBEDDINGS_PROVIDER` matches your setup:
- For vector stores created with OpenAI embeddings: Use `EMBEDDINGS_PROVIDER=openai`
- For new Qwen setup: Use `EMBEDDINGS_PROVIDER=qwen` (current implementation)

---

## 📝 Configuration Examples

### Example 1: Pure Qwen (China Deployment)

```bash
# .env
LLM_PROVIDER=qwen
QWEN_API_KEY=your-api-key-placeholder
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
EMBEDDINGS_PROVIDER=qwen
```

### Example 2: Hybrid (Cost Optimization)

```bash
# .env
LLM_PROVIDER=qwen
QWEN_API_KEY=your-api-key-placeholder
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
EMBEDDINGS_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-key
```

### Example 3: Development (Auto Selection)

```bash
# .env
LLM_PROVIDER=auto
OPENAI_API_KEY=sk-dev-key
QWEN_API_KEY=sk-backup-key
EMBEDDINGS_PROVIDER=auto
```

---

## 🎯 Best Practices

### 1. Use Environment-Specific Configuration

```bash
# Development .env
LLM_PROVIDER=auto

# Production .env (China)
LLM_PROVIDER=qwen
EMBEDDINGS_PROVIDER=qwen
```

### 2. Secure API Keys

- Never commit `.env` to version control
- Use `.env.example` as template
- Rotate keys regularly
- Use different keys for dev/prod

### 3. Monitor Costs

```bash
# Check Qwen usage
# Login to DashScope console: https://dashscope.console.aliyun.com/

# Check OpenAI usage
# Login to OpenAI dashboard: https://platform.openai.com/usage
```

---

## 📚 Additional Documentation

- **UBUNTU-DEPLOYMENT-QWEN.md**: Ubuntu deployment guide
- **QWEN-INTEGRATION-COMPLETE.md**: Implementation details
- **.env.example**: Configuration template

---

## 🆘 Support

For configuration issues:

1. Check logs: `docker-compose logs -f ecu-assistant-api`
2. Verify environment: `docker-compose exec ecu-assistant-api env | grep -E "(LLM|EMBEDDINGS|QWEN|OPENAI)"`
3. Test API connectivity manually
4. Review documentation in this guide

---

**Last Updated**: 2026-04-03
**Status**: Pure Qwen configuration fully functional
**Recommendation**: Use Pure Qwen for China deployment
