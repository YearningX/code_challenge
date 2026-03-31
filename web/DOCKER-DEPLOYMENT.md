# 🐳 Docker Deployment Guide - ME ECU Assistant

Production-ready Docker deployment for ME ECU Engineering Assistant.

---

## 🚀 Quick Start

### Prerequisites

- Docker Desktop installed (https://www.docker.com/products/docker-desktop)
- Docker Compose (included with Docker Desktop)
- 2GB free disk space
- 4GB RAM recommended

### Step 1: Build and Start (2 minutes)

```bash
cd web
docker-compose up --build
```

First run will take 2-3 minutes to build the image.

### Step 2: Verify Deployment

```bash
# Check container status
docker-compose ps

# Test API health
curl http://localhost:8000/api/health

# View logs
docker-compose logs -f ecu-assistant-api
```

### Step 3: Open Web Interface

Double-click `index.html` or open in browser:
```
file:///F:/projects/BOSCH_Code_Challenge/web/index.html
```

---

## 📋 Docker Commands Reference

### Basic Operations

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f ecu-assistant-api
```

### Build & Rebuild

```bash
# Build images without starting
docker-compose build

# Rebuild from scratch (no cache)
docker-compose build --no-cache

# Force recreate containers
docker-compose up -d --force-recreate
```

### Maintenance

```bash
# Check container health
docker-compose ps

# Execute command in container
docker-compose exec ecu-assistant-api bash

# Check resource usage
docker stats

# Clean up old images
docker image prune -a
```

### Debugging

```bash
# View detailed logs
docker-compose logs --tail=100 ecu-assistant-api

# Shell access to container
docker-compose exec ecu-assistant-api /bin/bash

# Check environment variables
docker-compose exec ecu-assistant-api env

# Test API from inside container
docker-compose exec ecu-assistant-api curl http://localhost:8000/api/health
```

---

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Model URI
MLFLOW_MODEL_URI=runs:/20f8fa846aea4dd183fa8bbe3739efb6/ecu_agent_model

# Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false
```

### Ports

| Service | Internal | External | Description |
|---------|----------|----------|-------------|
| ecu-assistant-api | 8000 | 8000 | FastAPI Server |
| nginx (optional) | 80 | 80 | Reverse Proxy |

### Volumes

| Host | Container | Mode | Description |
|------|-----------|------|-------------|
| ../mlruns | /app/mlruns | ro | MLflow Artifacts |
| ../data | /app/data | ro | Documentation Files |
| ./api_server.py | /app/api_server.py | ro | API Server Code |
| ./config.py | /app/config.py | ro | Configuration |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│  Docker Host (Windows/Mac/Linux)           │
│                                             │
│  ┌───────────────────────────────────────┐  │
│  │  ecu-assistant-api Container          │  │
│  │  - Python 3.11                        │  │
│  │  - FastAPI Server                     │  │
│  │  - MLflow Model                       │  │
│  │  - Port 8000                          │  │
│  └───────────────────────────────────────┘  │
│               ↓                              │
│  ┌───────────────────────────────────────┐  │
│  │  Host Browser                         │  │
│  │  - index.html                         │  │
│  │  - Static files                       │  │
│  └───────────────────────────────────────┘  │
│                                             │
│  Volumes:                                   │
│  - ../mlruns (MLflow artifacts)            │
│  - ../data (Documentation)                 │
└─────────────────────────────────────────────┘
```

---

## 🔍 Troubleshooting

### Issue: Port 8000 already in use

**Solution**: Change port in docker-compose.yml
```yaml
ports:
  - "8001:8000"  # Use 8001 on host
```

### Issue: MLflow model not found

**Solution**: Check MLFLOW_MODEL_URI in .env
```bash
# Verify model exists
docker-compose exec ecu-assistant-api python -c "
import mlflow
mlflow.pyfunc.load_model('runs:/20f8fa846aea4dd183fa8bbe3739efb6/ecu_agent_model')
"
```

### Issue: Container won't start

**Solution**: Check logs
```bash
docker-compose logs ecu-assistant-api
```

Common issues:
- Missing MLflow artifacts → Ensure `../mlruns` exists
- Permission denied → Check file permissions
- Out of memory → Increase Docker memory limit

### Issue: High memory usage

**Solution**: Limit container resources in docker-compose.yml
```yaml
services:
  ecu-assistant-api:
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
```

### Issue: Slow performance

**Solution**: Optimize Docker Desktop
- Increase memory allocation (4GB+)
- Increase CPU cores (2+)
- Use SSD for Docker storage
- Enable file sharing optimizations

---

## 🚢 Production Deployment

### Option 1: Docker Compose (Current)

```bash
# Start in detached mode
docker-compose up -d

# Enable production profile (with Nginx)
docker-compose --profile production up -d
```

### Option 2: Kubernetes

```bash
# Build and push image
docker build -t your-registry/ecu-assistant:latest .
docker push your-registry/ecu-assistant:latest

# Apply Kubernetes manifests
kubectl apply -f k8s/
```

### Option 3: Cloud Deployment

**AWS ECS**:
```bash
# Push to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin <ecr-url>
docker tag ecu-assistant:latest <ecr-url>/ecu-assistant:latest
docker push <ecr-url>/ecu-assistant:latest
```

**Azure Container Instances**:
```bash
az container create \
  --resource-group myResourceGroup \
  --name ecu-assistant \
  --image your-registry/ecu-assistant:latest \
  --ports 8000
```

**Google Cloud Run**:
```bash
gcloud run deploy ecu-assistant \
  --image gcr.io/your-project/ecu-assistant:latest \
  --platform managed \
  --port 8000
```

---

## 📊 Monitoring & Logging

### Health Checks

```bash
# Automated health check
watch -n 5 'curl -s http://localhost:8000/api/health | jq .'

# Docker health status
docker inspect --format='{{.State.Health.Status}}' ecu-assistant-api
```

### Log Management

```bash
# Follow logs in real-time
docker-compose logs -f

# Export logs
docker-compose logs > ecu-assistant.log

# Log analysis
docker-compose logs | grep ERROR
docker-compose logs | grep "Query completed"
```

### Metrics Collection

```bash
# Container stats
docker stats ecu-assistant-api

# Resource usage
docker-compose top
```

---

## 🔒 Security Best Practices

1. **Use specific image versions**
   ```dockerfile
   FROM python:3.11-slim  # Good
   FROM python:latest     # Bad
   ```

2. **Run as non-root user**
   ```dockerfile
   RUN useradd -m appuser
   USER appuser
   ```

3. **Scan images for vulnerabilities**
   ```bash
   docker scan ecu-assistant-api:latest
   ```

4. **Use secrets management**
   ```yaml
   services:
     ecu-assistant-api:
       secrets:
         - openai_api_key
   ```

5. **Enable HTTPS** (use Nginx profile)
   ```bash
   docker-compose --profile production up -d
   ```

---

## 📦 Backup & Restore

### Backup

```bash
# Export container image
docker save ecu-assistant-api:latest > ecu-assistant.tar

# Backup volumes
docker run --rm -v ecu-assistant-mlflow-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/mlflow-backup.tar.gz /data
```

### Restore

```bash
# Load container image
docker load < ecu-assistant.tar

# Restore volumes
docker run --rm -v ecu-assistant-mlflow-data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/mlflow-backup.tar.gz -C /
```

---

## 🧪 Testing

### Integration Tests

```bash
# Test API endpoints
docker-compose up -d
sleep 10
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query":"What is ECU-750?"}'
```

### Performance Tests

```bash
# Load testing
ab -n 100 -c 10 http://localhost:8000/api/health

# Benchmark query latency
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/query \
    -H "Content-Type: application/json" \
    -d '{"query":"What is ECU-750?"}'
done
```

---

## 📝 Checklist

Before presenting to leadership:

- [ ] Docker Compose builds successfully
- [ ] Container starts without errors
- [ ] Health check returns "healthy"
- [ ] Query endpoint works
- [ ] Web interface connects
- [ ] All demo queries succeed
- [ ] Logs show no errors
- [ ] Resource usage is acceptable
- [ ] Browser can access API

---

## 🎯 Quick Commands for Demo

```bash
# 1. Start system
cd web
docker-compose up -d

# 2. Wait for ready status
docker-compose logs -f | grep "Application startup complete"

# 3. Test health
curl http://localhost:8000/api/health

# 4. Open web interface
# Double-click index.html

# 5. Run demo
# Click demo buttons in web interface

# 6. Stop after demo
docker-compose down
```

---

## 📞 Support

**Docker Issues**:
- Docker Desktop: https://docs.docker.com/desktop/
- Docker Compose: https://docs.docker.com/compose/

**Application Issues**:
- Check logs: `docker-compose logs -f`
- Health check: `curl http://localhost:8000/api/health`
- API docs: http://localhost:8000/api/docs

---

**Version**: 1.0.0
**Last Updated**: 2026-03-31
**Status**: Production Ready
