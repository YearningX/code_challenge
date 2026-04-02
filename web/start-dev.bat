@echo off
REM 本地开发环境启动脚本 - Windows
REM 用于前端开发，支持实时热重载

echo.
echo ========================================
echo   ME ECU Assistant - 本地开发模式
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.11+
    pause
    exit /b 1
)

echo ✅ Python环境检测通过
echo.

REM 检查是否在正确的目录
if not exist "index.html" (
    echo ❌ 错误: 请在web目录下运行此脚本
    pause
    exit /b 1
)

echo ✅ 工作目录: %CD%
echo.

REM 检查并停止Docker容器
echo 🔍 检查Docker容器...
docker ps --format "{{.Names}}" | findstr "ecu-assistant" >nul 2>&1
if not errorlevel 1 (
    echo ⚠️  发现运行中的Docker容器，正在停止...
    docker-compose down >nul 2>&1
    if not errorlevel 1 (
        echo ✅ Docker容器已停止
    ) else (
        echo ⚠️  自动停止失败，请手动运行: docker-compose down
    )
) else (
    echo ✅ 没有运行中的Docker容器
)
echo.

REM 检查依赖是否安装
echo 🔍 检查依赖...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo ⚠️  依赖未安装，正在安装...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 依赖安装失败
        pause
        exit /b 1
    )
    echo ✅ 依赖安装完成
) else (
    echo ✅ 依赖已安装
)

echo.
echo ========================================
echo   🚀 启动开发服务器
echo ========================================
echo.
echo 💡 使用提示:
echo    - 服务地址: http://127.0.0.1:18500
echo    - 修改 index.html 后刷新浏览器 (Ctrl+Shift+R)
echo    - 修改 Python 代码会自动重启服务器
echo    - 按 Ctrl+C 停止服务器
echo.
echo ⚠️  重要提示:
echo    - 请使用 Ctrl+Shift+R 硬刷新浏览器
echo    - 或按F12打开开发者工具，禁用缓存
echo    - 确保访问的是 127.0.0.1:18500 而非Docker容器
echo.
echo ========================================
echo.

REM 启动开发服务器
python dev_server.py

pause
