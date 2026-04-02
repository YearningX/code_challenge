# 🚀 ME ECU Assistant - Development Environment Setup Guide

## 📖 Overview

The frontend of this project is **pure static HTML + JavaScript**, with no Node.js/npm build tools. The backend uses Python FastAPI server.

---

## 🎯 Comparison of Three Usage Modes

### 1️⃣ **Local Development Mode** (Highly recommended for frontend debugging)

#### ✅ Advantages
- ✨ **Real-time frontend updates** - Just refresh browser after modifying `index.html`
- 🔄 **Automatic hot-reload** - Server auto-restarts on Python code changes
- ⚡ **Fast iteration** - No need to wait for Docker builds
- 🔧 **Full functionality** - All production environment APIs available

#### 🚀 Usage

```bash
# 1. Enter web directory
cd web

# 2. Install dependencies (first time only)
pip install -r requirements.txt

# 3. Start development server
python dev_server.py
```

#### 📱 Access URL
```
http://localhost:18500
```

#### 💡 Workflow
```
1. Start development server
   └─> python dev_server.py

2. Open browser
   └─> http://localhost:18500

3. Modify index.html
   └─> Save file

4. Refresh browser (F5 or Ctrl+R)
   └─> See changes immediately ✨
```

---

### 2️⃣ **Docker Development Mode** (Using Volume Mount)

#### ✅ Advantages
- 🐳 Consistent containerized environment
- 📁 Real-time frontend file sync
- 🔄 No need to rebuild image

#### 🚀 Usage

```bash
# 1. Modify docker-compose.yml, add frontend file mount
# Add to volumes section of ecu-assistant-api service:
volumes:
  # ... other mounts ...
  - ./index.html:/app/index.html:ro  # Add this line

# 2. Start service
docker-compose up ecu-assistant-api

# 3. Refresh browser after modifying index.html
```

#### 📱 Access URL
```
http://localhost:18500
```

---

### 3️⃣ **Production Mode** (Full Docker Build)

#### ✅ Advantages
- 🏭 Production deployment
- 🔒 Stable and reliable
- 📦 Complete containerization

#### 🚀 Usage

```bash
# 1. Build image
docker-compose build

# 2. Start service
docker-compose up -d

# 3. Rebuild after frontend changes
docker-compose build && docker-compose up -d
```

---

## 🔧 Frequently Asked Questions

### Q1: How to see changes immediately after modifying index.html?

**A:**
- **Local development mode**: Just refresh browser (F5)
- **Docker development mode**: Just refresh browser (F5)
- **Production Docker mode**: Need to rebuild image `docker-compose build && docker-compose up -d`

### Q2: Why is there no npm run dev?

**A:** The frontend is pure static HTML with no Node.js ecosystem. No build step required, just modify HTML files directly.

### Q3: How to enable frontend hot-reload (auto-refresh)?

**A:** You can use browser Live Reload extensions, or:

```bash
# Install live-reload tool
pip install livereload

# Modify dev_server.py to add livereload support
# (Already included in dev_server.py, just refresh browser)
```

### Q4: Do I need to restart after modifying Python code?

**A:**
- **Local development mode**: Auto-restart ✅
- **Docker mode**: Need to restart container `docker-compose restart ecu-assistant-api`

---

## 📝 Recommended Development Workflow

### 🎨 Frontend Development (UI Adjustments)

```bash
# 1. Start local development server
cd web
python dev_server.py

# 2. Open browser
# http://localhost:18500

# 3. Modify index.html
# 4. Save file
# 5. Refresh browser (Ctrl+R)
# 6. Repeat steps 3-5
```

### 🔧 Backend Development (API Adjustments)

```bash
# 1. Start local development server (auto hot-reload)
python dev_server.py

# 2. Modify api_server.py
# 3. Save file (server auto-restarts)
# 4. Test API
```

### 🐳 Container Testing

```bash
# 1. Use volume mount mode
# Edit docker-compose.yml add: - ./index.html:/app/index.html:ro

# 2. Start container
docker-compose up ecu-assistant-api

# 3. Test changes

# 4. Build production image after confirmation
docker-compose build && docker-compose up -d
```

---

## 🎯 Recommended Solutions for Different Scenarios

| Scenario | Recommended Mode | Reason |
|----------|----------------|--------|
| 🔥 Fast UI debugging | Local Development | See changes immediately |
| 🧪 Feature testing | Local Development | Fast iteration, easy debugging |
| 🐛 Troubleshooting | Local Development | Direct log access |
| 🏭 Production deployment | Docker Build | Stable and reliable |
| 👥 Team collaboration | Docker | Consistent environment |

---

## 💡 Best Practices

### 1. Frontend Development
- ✅ Use local development mode `python dev_server.py`
- ✅ Use browser DevTools (F12) for debugging
- ✅ Refresh browser promptly after changes

### 2. Backend Development
- ✅ Local development mode supports auto-reload
- ✅ Check console logs to confirm changes
- ✅ Use `/api/dev/status` to check development status

### 3. Version Control
- ✅ Use local mode during development
- ✅ Commit code after testing
- ✅ Use Docker build in CI/CD pipeline

### 4. Performance Optimization
- ✅ Browser cache: Disable cache during development (Ctrl+Shift+R)
- ✅ Resource compression: Compress HTML/CSS/JS in production
- ✅ CDN deployment: Use CDN acceleration in production

---

## 🔗 Related Files

- 📄 `dev_server.py` - Local development server
- 📄 `api_server.py` - FastAPI server
- 📄 `index.html` - Frontend interface
- 📄 `docker-compose.yml` - Docker configuration
- 📄 `Dockerfile` - Image build configuration

---

## 📞 Getting Help

If you encounter issues, please check:
1. Python version: `python --version` (requires 3.11+)
2. Dependency installation: `pip install -r requirements.txt`
3. Port availability: Ensure port 18500 is not in use
4. Model files: Confirm MLflow model is available

---

**Happy Coding! 🚀**
