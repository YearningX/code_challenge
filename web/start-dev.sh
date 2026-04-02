#!/bin/bash
# 本地开发环境启动脚本 - Linux/Mac
# 用于前端开发，支持实时热重载

set -e

echo ""
echo "========================================"
echo "  ME ECU Assistant - 本地开发模式"
echo "========================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3，请先安装Python 3.11+"
    exit 1
fi

echo "✅ Python环境检测通过"
python3 --version
echo ""

# 检查是否在正确的目录
if [ ! -f "index.html" ]; then
    echo "❌ 错误: 请在web目录下运行此脚本"
    exit 1
fi

echo "✅ 工作目录: $(pwd)"
echo ""

# 检查依赖是否安装
echo "🔍 检查依赖..."
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "⚠️  依赖未安装，正在安装..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
    echo "✅ 依赖安装完成"
else
    echo "✅ 依赖已安装"
fi

echo ""
echo "========================================"
echo "  🚀 启动开发服务器"
echo "========================================"
echo ""
echo "💡 使用提示:"
echo "   - 服务地址: http://localhost:18500"
echo "   - 修改 index.html 后刷新浏览器 (Cmd+R)"
echo "   - 修改 Python 代码会自动重启服务器"
echo "   - 按 Ctrl+C 停止服务器"
echo ""
echo "========================================"
echo ""

# 启动开发服务器
python3 dev_server.py
