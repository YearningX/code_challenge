@echo off
REM Local development environment startup script - Windows
REM For frontend development with real-time hot-reload

echo.
echo ========================================
echo   ME ECU Assistant - Local Development Mode
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python not found, please install Python 3.11+
    pause
    exit /b 1
)

echo ✅ Python environment check passed
echo.

REM Check if in correct directory
if not exist "index.html" (
    echo ❌ Error: Please run this script in the web directory
    pause
    exit /b 1
)

echo ✅ Working directory: %CD%
echo.

REM Check and stop Docker containers
echo 🔍 Checking Docker containers...
docker ps --format "{{.Names}}" | findstr "ecu-assistant" >nul 2>&1
if not errorlevel 1 (
    echo ⚠️  Running Docker containers found, stopping...
    docker-compose down >nul 2>&1
    if not errorlevel 1 (
        echo ✅ Docker containers stopped
    ) else (
        echo ⚠️  Auto-stop failed, please run manually: docker-compose down
    )
) else (
    echo ✅ No running Docker containers
)
echo.

REM Check if dependencies are installed
echo 🔍 Checking dependencies...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Dependencies not installed, installing...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Dependency installation failed
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed
) else (
    echo ✅ Dependencies already installed
)

echo.
echo ========================================
echo   🚀 Starting Development Server
echo ========================================
echo.
echo 💡 Usage tips:
echo    - Service URL: http://127.0.0.1:18500
echo    - Refresh browser (Ctrl+Shift+R) after modifying index.html
echo    - Server auto-restarts on Python code changes
echo    - Press Ctrl+C to stop the server
echo.
echo ⚠️  Important notes:
echo    - Please use Ctrl+Shift+R for hard refresh
echo    - Or press F12 to open DevTools and disable cache
echo    - Ensure accessing 127.0.0.1:18500 not Docker container
echo.
echo ========================================
echo.

REM Start development server
python dev_server.py

pause
