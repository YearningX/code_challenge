# Ubuntu Deployment Guide - Complete Qwen Solution

## ✅ Successfully Implemented

Your ECU Agent can now **fully use Qwen (Alibaba Cloud)** without needing to access OpenAI!

### 🎯 Current Configuration

```bash
LLM_PROVIDER=qwen              # Chat Model: Qwen qwen-plus
EMBEDDINGS_PROVIDER=qwen       # Embeddings: Qwen text-embedding-v2
QWEN_API_KEY=your-api-key-placeholder
```

### 📊 Test Results

**Query**: "What is ECU-750?"
- ✅ Query Analysis: Qwen `qwen-plus`
- ✅ Vector Retrieval: Qwen `text-embedding-v2`
- ✅ Response Synthesis: Qwen `qwen-plus`
- ✅ Latency: 10.5 seconds
- ✅ Product Line Detection: ECU-700 (accurate)

**Response Quality**: Excellent! Provided complete technical specifications for ECU-750.

---

## 🚀 Ubuntu Server Deployment Steps

### Prerequisites

- Ubuntu server (with access to Alibaba Cloud DashScope API)
- Docker and Docker Compose installed
- Qwen API Key (configured)

### Step 1: Prepare Code

```bash
# On local Windows machine
cd F:/projects/BOSCH_Code_Challenge

# Create deployment package (including all necessary files)
tar -czf bosch_ecu_agent_qwen.tar.gz \
    --exclude='.git' \
    --exclude='mlruns' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='node_modules' \
    .
```

### Step 2: Upload to Ubuntu

```bash
# Upload using SCP
scp bosch_ecu_agent_qwen.tar.gz user@your-server:/home/user/

# Or use other methods (FTP, Git, etc.)
```

### Step 3: Extract and Configure on Ubuntu

```bash
# SSH to Ubuntu server
ssh user@your-server

# Extract
cd /home/user
mkdir -p bosch_ecu_agent
cd bosch_ecu_agent
tar -xzf ../bosch_ecu_agent_qwen.tar.gz

# Create .env file
cat > .env << 'EOF'
# LLM Configuration
LLM_PROVIDER=qwen
QWEN_API_KEY=your-api-key-placeholder
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# Embeddings Configuration
EMBEDDINGS_PROVIDER=qwen
QWEN_API_KEY=your-api-key-placeholder

# Langfuse Configuration
LANGFUSE_SECRET_KEY=your-api-key-placeholder
LANGFUSE_PUBLIC_KEY=your-api-key-placeholder
LANGFUSE_BASE_URL=https://langfuse.cccoder.top

# Server Configuration
API_HOST=0.0.0.0
API_PORT=18500
API_RELOAD=false
EOF

# Verify .env file
cat .env
```

### Step 4: Build and Start Service

```bash
# Enter web directory
cd web

# Build and start Docker container
docker-compose build --no-cache
docker-compose up -d

# View logs to confirm successful startup
docker-compose logs -f ecu-assistant-api
```

**Expected Log Output**:
```
Embeddings Configuration
============================================================
Provider: qwen
Model: text-embedding-v2
============================================================
Using Qwen embeddings (direct API call to DashScope)
Loaded ECU-700 store from /app/models/.../ecu_700_index
Loaded ECU-800 store from /app/models/.../ecu_800_index

ECUQueryAgent - Model Configuration
============================================================
Provider: qwen
Model: qwen-plus
Base URL: https://dashscope.aliyuncs.com/compatible-mode/v1
============================================================
✓ Agent initialized with Langfuse tracing
```

### Step 5: Verify Deployment

```bash
# Health check
curl http://localhost:18500/api/health

# Test query
curl -X POST http://localhost:18500/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is ECU-750?"}'
```

**Expected Response**: Returns detailed technical information about ECU-750.

### Step 6: Configure Reverse Proxy (Optional)

If you need to access via domain name, you can configure Nginx:

```bash
# Install Nginx
sudo apt update
sudo apt install nginx -y

# Create configuration file
sudo tee /etc/nginx/sites-available/bosch-ecu << 'EOF'
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:18500;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable configuration
sudo ln -s /etc/nginx/sites-available/bosch-ecu /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔍 Troubleshooting

### Issue 1: Container Won't Start

```bash
# Check logs
docker-compose logs ecu-assistant-api

# Common issues:
# - .env file format error
# - Port 18500 occupied
# - Docker permission issues
```

### Issue 2: API Call Failures

```bash
# Check network connectivity
curl https://dashscope.aliyuncs.com/api/v1

# Verify API key
echo $QWEN_API_KEY

# Check environment variables in Docker container
docker-compose exec ecu-assistant-api env | grep QWEN
```

### Issue 3: Vector Store Loading Failed

```bash
# Check vector store directory
ls -la models/ecu_agent_model_local/ecu_agent_model/artifacts/

# Check permissions
docker-compose exec ecu-assistant-api ls -la /app/models/
```

---

## 📊 Monitoring and Maintenance

### View Real-time Logs

```bash
docker-compose logs -f ecu-assistant-api
```

### Restart Service

```bash
cd /path/to/bosch_ecu_agent/web
docker-compose restart
```

### Update Code

```bash
# 1. Backup current version
cp -r bosch_ecu_agent bosch_ecu_agent.backup

# 2. Upload new code
# 3. Rebuild
cd bosch_ecu_agent/web
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## 🔐 Security Recommendations

1. **Protect .env file**:
```bash
chmod 600 .env
```

2. **Use firewall**:
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

3. **Regular updates**:
```bash
# Regularly pull security updates
sudo apt update && sudo apt upgrade -y
```

4. **Monitor resource usage**:
```bash
docker stats ecu-assistant-api
```

---

## 📈 Performance Optimization

### Adjust Docker Resource Limits

Edit `docker-compose.yml`:

```yaml
services:
  ecu-assistant-api:
    # ... other configurations
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          memory: 2G
```

### Enable Caching

Add to `.env`:

```bash
# Optional: Enable response caching
ENABLE_CACHE=true
CACHE_TTL=3600
```

---

## 🎯 Cost Estimation

### Qwen API Pricing (Reference)

- **qwen-plus**: ¥0.004/1K tokens
- **text-embedding-v2**: ¥0.0007/1K tokens

### Monthly Cost Estimation (10,000 queries)

- **LLM (Chat)**: 6M tokens × ¥0.004 = ¥24
- **Embeddings**: 15M tokens × ¥0.0007 = ¥10.5
- **Total**: **About ¥35/month**

Compared to OpenAI solution (about ¥94/month), **saves 63%**!

---

## 📞 Support

If you encounter issues, please check:

1. ✅ Docker logs: `docker-compose logs -f`
2. ✅ Environment variables: `docker-compose exec ecu-assistant-api env | grep -E "(QWEN|LLM|EMBEDDINGS)"`
3. ✅ API connectivity: `curl https://dashscope.aliyuncs.com/api/v1`
4. ✅ Vector stores: Check if FAISS index files exist

---

**After deployment is complete, your ECU Agent will:**
- ✅ Run fully on Qwen/Alibaba Cloud
- ✅ No need to access OpenAI
- ✅ Suitable for China server deployment
- ✅ Cost reduced by 63%

Good luck with your deployment! 🚀
