# 🚀 快速参考 - ME ECU Assistant 开发模式

## ⚡ 三种启动方式

### 1️⃣ 本地开发模式（推荐）⭐

```bash
# Windows
start-dev.bat

# Linux/Mac
chmod +x start-dev.sh
./start-dev.sh

# 或直接运行
python dev_server.py
```

**特点：**
- ✅ 修改 `index.html` 后刷新浏览器即可
- ✅ 修改 Python 代码自动重启
- ✅ 无需Docker，快速开发

---

### 2️⃣ Docker开发模式

```bash
# 启动开发模式容器
docker-compose -f docker-compose-dev.yml up

# 后台运行
docker-compose -f docker-compose-dev.yml up -d

# 停止
docker-compose -f docker-compose-dev.yml down
```

**特点：**
- ✅ 前端文件通过volume挂载，修改实时生效
- ✅ 容器化环境，与生产一致
- ⚠️ 需要Docker环境

---

### 3️⃣ Docker生产模式

```bash
# 构建并启动
docker-compose up -d

# 重新构建（修改前端后）
docker-compose build && docker-compose up -d
```

**特点：**
- ✅ 生产环境部署
- ⚠️ 修改前端需要重新构建镜像

---

## 📝 常用操作

### 修改前端界面

```bash
# 1. 启动开发模式
python dev_server.py

# 2. 打开浏览器
http://localhost:18500

# 3. 编辑 index.html

# 4. 保存并刷新浏览器 (F5)
```

### 修改后端API

```bash
# 1. 启动开发模式（自动热重载）
python dev_server.py

# 2. 编辑 api_server.py

# 3. 保存（自动重启）
```

### 查看日志

```bash
# 本地模式
python dev_server.py
# 日志直接显示在控制台

# Docker模式
docker-compose logs -f ecu-assistant-api
```

---

## 🔍 调试技巧

### 前端调试
1. 打开浏览器开发者工具 (F12)
2. Console查看JavaScript错误
3. Network查看API请求
4. Elements实时修改CSS测试

### 后端调试
1. 查看 `dev_server.py` 控制台输出
2. 访问 `/api/dev/status` 检查状态
3. 使用 `print()` 输出调试信息

### 清除缓存
```
浏览器硬刷新: Ctrl+Shift+R (Windows)
             Cmd+Shift+R (Mac)
```

---

## 📊 性能对比

| 模式 | 启动时间 | 前端修改生效 | 后端修改生效 | 适用场景 |
|------|----------|-------------|-------------|----------|
| 本地开发 | ~5s | ⚡ 即时 | ⚡ 自动 | 日常开发 |
| Docker开发 | ~30s | ⚡ 即时 | 🔄 重启容器 | 集成测试 |
| Docker生产 | ~30s | 🔨 重新构建 | 🔨 重新构建 | 生产部署 |

---

## 🆘 故障排除

### 端口被占用
```bash
# Windows
netstat -ano | findstr :18500
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:18500 | xargs kill -9

# 或修改端口
# 编辑 dev_server.py 中的 DEV_CONFIG["port"]
```

### 依赖缺失
```bash
pip install -r requirements.txt
```

### 模型加载失败
```bash
# 检查MLflow模型路径
ls ../models/ecu_agent_model_local/ecu_agent_model

# 或修改模型路径
# 编辑 config.py 中的 MODEL_URI
```

---

## 📞 获取帮助

- 📖 详细文档：`DEV-GUIDE.md`
- 🐳 Docker文档：`DOCKER-DEPLOYMENT.md`
- 📋 项目README：`README.md`

---

**Happy Coding! 🎉**
