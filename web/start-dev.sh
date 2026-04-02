#!/bin/bash
# Local development environment startup script - Linux/Mac
# For frontend development with real-time hot-reload

set -e

echo ""
echo "========================================"
echo "  ME ECU Assistant - Local Development Mode"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python3 not found, please install Python 3.11+"
    exit 1
fi

echo "✅ Python environment check passed"
python3 --version
echo ""

# Check if in correct directory
if [ ! -f "index.html" ]; then
    echo "❌ Error: Please run this script in the web directory"
    exit 1
fi

echo "✅ Working directory: $(pwd)"
echo ""

# Check if dependencies are installed
echo "🔍 Checking dependencies..."
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "⚠️  Dependencies not installed, installing..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Dependency installation failed"
        exit 1
    fi
    echo "✅ Dependencies installed"
else
    echo "✅ Dependencies already installed"
fi

echo ""
echo "========================================"
echo "  🚀 Starting Development Server"
echo "========================================"
echo ""
echo "💡 Usage tips:"
echo "   - Service URL: http://localhost:18500"
echo "   - Refresh browser (Cmd+R) after modifying index.html"
echo "   - Server auto-restarts on Python code changes"
echo "   - Press Ctrl+C to stop the server"
echo ""
echo "========================================"
echo ""

# Start development server
python3 dev_server.py
