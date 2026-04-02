# 🚀 Quick Reference - ME ECU Assistant Development Mode

## ⚡ Three Startup Methods

### 1️⃣ Local Development Mode (Recommended) ⭐

```bash
# Windows
start-dev.bat

# Linux/Mac
chmod +x start-dev.sh
./start-dev.sh

# Or run directly
python dev_server.py
```

**Features:**
- ✅ Refresh browser after modifying `index.html`
- ✅ Auto-restart on Python code changes
- ✅ No Docker needed, fast development

---

### 2️⃣ Docker Development Mode

```bash
# Start development container
docker-compose -f docker-compose-dev.yml up

# Run in background
docker-compose -f docker-compose-dev.yml up -d

# Stop
docker-compose -f docker-compose-dev.yml down
```

**Features:**
- ✅ Frontend files mounted via volume, real-time updates
- ✅ Containerized environment, consistent with production
- ⚠️ Requires Docker environment

---

### 3️⃣ Docker Production Mode

```bash
# Build and start
docker-compose up -d

# Rebuild (after frontend changes)
docker-compose build && docker-compose up -d
```

**Features:**
- ✅ Production deployment
- ⚠️ Requires rebuilding image after frontend changes

---

## 📝 Common Operations

### Modify Frontend Interface

```bash
# 1. Start development mode
python dev_server.py

# 2. Open browser
http://localhost:18500

# 3. Edit index.html

# 4. Save and refresh browser (F5)
```

### Modify Backend API

```bash
# 1. Start development mode (auto hot-reload)
python dev_server.py

# 2. Edit api_server.py

# 3. Save (auto-restart)
```

### View Logs

```bash
# Local mode
python dev_server.py
# Logs displayed directly in console

# Docker mode
docker-compose logs -f ecu-assistant-api
```

---

## 🔍 Troubleshooting

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :18500
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:18500 | xargs kill -9

# Or change port
# Edit dev_server.py DEV_CONFIG["port"]
```

### Missing Dependencies
```bash
pip install -r requirements.txt
```

### Model Loading Failed
```bash
# Check MLflow model path
ls ../models/ecu_agent_model_local/ecu_agent_model

# Or modify model path
# Edit config.py MODEL_URI
```

---

## 📊 Performance Comparison

| Mode | Startup Time | Frontend Update | Backend Update | Use Case |
|------|-------------|----------------|----------------|----------|
| Local Dev | ~5s | ⚡ Instant | ⚡ Auto | Daily development |
| Docker Dev | ~30s | ⚡ Instant | 🔄 Restart container | Integration testing |
| Docker Prod | ~30s | 🔨 Rebuild | 🔨 Rebuild | Production deployment |

---

## 🆘 Troubleshooting

### Frontend Errors
1. Open DevTools (F12)
2. Check Console for JavaScript errors
3. Check Network tab for failed requests

### Backend Errors
1. Check console output in local mode
2. Check `/api/dev/status` for development status
3. Use `print()` for debugging information

### Clear Cache
```
Browser hard refresh: Ctrl+Shift+R (Windows)
                     Cmd+Shift+R (Mac)
```

---

## 🔗 Related Files

- 📖 `DEV-GUIDE.md` - Comprehensive development guide
- 🐳 `docker-compose.yml` - Docker configuration
- 🐳 `docker-compose-dev.yml` - Development Docker configuration
- ⚙️ `config.py` - Application configuration
- 📝 `README.md` - Project overview

---

**Happy Coding! 🎉**
