# 🐳 Docker Quick Start - ME ECU Assistant

## 一键启动命令

```bash
# 1. 进入web目录
cd web

# 2. 构建并启动（首次运行需要2-3分钟）
docker-compose up --build -d

# 3. 查看日志
docker-compose logs -f

# 4. 检查健康状态
curl http://localhost:8000/api/health

# 5. 打开Web界面
# 双击 index.html 文件
```

## 演示模式快速命令

```bash
# 启动系统
cd web && docker-compose up -d

# 等待启动完成（约30秒）
timeout 30

# 测试查询
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query":"What is ECU-750?"}'

# 演示结束后停止
docker-compose down
```

## 常用命令

```bash
# 查看容器状态
docker-compose ps

# 查看实时日志
docker-compose logs -f ecu-assistant-api

# 重启容器
docker-compose restart

# 停止容器
docker-compose down

# 完全清理（包括卷）
docker-compose down -v
```

## 故障排除

**问题：端口8000已被占用**
```bash
# 修改docker-compose.yml中的端口映射
ports:
  - "8001:8000"  # 使用8001端口
```

**问题：容器启动失败**
```bash
# 查看详细日志
docker-compose logs ecu-assistant-api

# 重新构建
docker-compose build --no-cache
docker-compose up -d
```

**问题：无法连接到API**
```bash
# 检查容器是否在运行
docker-compose ps

# 检查健康状态
docker inspect --format='{{.State.Health.Status}}' ecu-assistant-api

# 进入容器调试
docker-compose exec ecu-assistant-api bash
```

## 成功标志

当看到以下输出时，系统已准备就绪：

```
✓ Container status: "Up"
✓ Health check: "healthy"
✓ API response: {"status":"healthy","model_loaded":true}
✓ Web界面可以访问
```

---

**预计时间**：
- 首次构建：2-3分钟
- 后续启动：10-15秒
