# 🚀 ME ECU Assistant - 开发环境配置指南

## 📖 概述

本项目的前端是**纯静态HTML + JavaScript**，没有使用Node.js/npm构建工具。后端使用Python FastAPI服务器。

---

## 🎯 三种使用模式对比

### 1️⃣ **本地开发模式** (强烈推荐前端调试时使用)

#### ✅ 优势
- ✨ **前端修改实时生效** - 修改 `index.html` 后只需刷新浏览器
- 🔄 **自动热重载** - Python代码修改后自动重启服务器
- ⚡ **快速迭代** - 无需等待Docker构建
- 🔧 **完整功能** - 保留所有生产环境API

#### 🚀 使用方法

```bash
# 1. 进入web目录
cd web

# 2. 安装依赖（首次运行）
pip install -r requirements.txt

# 3. 启动开发服务器
python dev_server.py
```

#### 📱 访问地址
```
http://localhost:18500
```

#### 💡 工作流程
```
1. 启动开发服务器
   └─> python dev_server.py

2. 打开浏览器访问
   └─> http://localhost:18500

3. 修改 index.html
   └─> 保存文件

4. 刷新浏览器 (F5 或 Ctrl+R)
   └─> 立即看到修改效果 ✨
```

---

### 2️⃣ **Docker开发模式** (使用Volume挂载)

#### ✅ 优势
- 🐳 容器化环境一致性
- 📁 前端文件实时同步
- 🔄 无需重新构建镜像

#### 🚀 使用方法

```bash
# 1. 修改 docker-compose.yml，添加前端文件挂载
# 在 ecu-assistant-api 服务的 volumes 部分添加：
volumes:
  # ... 其他挂载 ...
  - ./index.html:/app/index.html:ro  # 添加这行

# 2. 启动服务
docker-compose up ecu-assistant-api

# 3. 修改 index.html 后刷新浏览器即可
```

#### 📱 访问地址
```
http://localhost:18500
```

---

### 3️⃣ **生产模式** (Docker完整构建)

#### ✅ 优势
- 🏭 生产环境部署
- 🔒 稳定可靠
- 📦 完整容器化

#### 🚀 使用方法

```bash
# 1. 构建镜像
docker-compose build

# 2. 启动服务
docker-compose up -d

# 3. 修改前端后需要重新构建
docker-compose build && docker-compose up -d
```

---

## 🔧 常见问题解答

### Q1: 修改 index.html 后如何立即看到效果？

**A:**
- **本地开发模式**：直接刷新浏览器 (F5)
- **Docker开发模式**：直接刷新浏览器 (F5)
- **生产Docker模式**：需要重新构建镜像 `docker-compose build && docker-compose up -d`

### Q2: 为什么没有 npm run dev？

**A:** 本项目的前端是纯静态HTML，没有使用Node.js生态系统。不需要构建步骤，直接修改HTML文件即可。

### Q3: 如何启用前端热重载（自动刷新）？

**A:** 可以使用浏览器的Live Reload插件，或者：

```bash
# 安装live-reload工具
pip install livereload

# 修改 dev_server.py 添加 livereload 支持
# (已包含在dev_server.py中，刷新浏览器即可)
```

### Q4: 修改Python代码后需要重启吗？

**A:**
- **本地开发模式**：自动重启 ✅
- **Docker模式**：需要重启容器 `docker-compose restart ecu-assistant-api`

---

## 📝 推荐的开发工作流

### 🎨 前端开发（UI调整）

```bash
# 1. 启动本地开发服务器
cd web
python dev_server.py

# 2. 打开浏览器
# http://localhost:18500

# 3. 修改 index.html
# 4. 保存文件
# 5. 刷新浏览器 (Ctrl+R)
# 6. 重复步骤3-5
```

### 🔧 后端开发（API调整）

```bash
# 1. 启动本地开发服务器（自动热重载）
python dev_server.py

# 2. 修改 api_server.py
# 3. 保存文件（服务器自动重启）
# 4. 测试API
```

### 🐳 容器化测试

```bash
# 1. 使用volume挂载模式
# 编辑 docker-compose.yml 添加：- ./index.html:/app/index.html:ro

# 2. 启动容器
docker-compose up ecu-assistant-api

# 3. 测试修改

# 4. 确认无误后构建生产镜像
docker-compose build && docker-compose up -d
```

---

## 🎯 不同场景推荐方案

| 场景 | 推荐模式 | 理由 |
|------|---------|------|
| 🔥 快速UI调试 | 本地开发 | 修改立见，无需等待 |
| 🧪 功能测试 | 本地开发 | 快速迭代，方便调试 |
| 🐛 问题排查 | 本地开发 | 可直接查看日志 |
| 🏭 生产部署 | Docker构建 | 稳定可靠 |
| 👥 团队协作 | Docker | 环境一致 |

---

## 💡 最佳实践

### 1. 前端开发
- ✅ 使用本地开发模式 `python dev_server.py`
- ✅ 使用浏览器开发者工具（F12）调试
- ✅ 修改后及时刷新浏览器查看效果

### 2. 后端开发
- ✅ 本地开发模式支持自动重载
- ✅ 查看控制台日志确认修改生效
- ✅ 使用 `/api/dev/status` 检查开发状态

### 3. 版本控制
- ✅ 开发时使用本地模式
- ✅ 测试通过后提交代码
- ✅ CI/CD流程中使用Docker构建

### 4. 性能优化
- ✅ 浏览器缓存：开发时可禁用缓存（Ctrl+Shift+R）
- ✅ 压缩资源：生产环境可压缩HTML/CSS/JS
- ✅ CDN部署：生产环境可使用CDN加速

---

## 🔗 相关文件

- 📄 `dev_server.py` - 本地开发服务器
- 📄 `api_server.py` - FastAPI服务器
- 📄 `index.html` - 前端界面
- 📄 `docker-compose.yml` - Docker配置
- 📄 `Dockerfile` - 镜像构建配置

---

## 📞 获取帮助

如遇问题，请检查：
1. Python版本：`python --version` (需要3.11+)
2. 依赖安装：`pip install -r requirements.txt`
3. 端口占用：确保18500端口未被占用
4. 模型文件：确认MLflow模型可用

---

**Happy Coding! 🚀**
