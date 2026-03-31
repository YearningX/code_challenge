#!/usr/bin/env python3
"""
Quick Start Script for ME ECU Assistant Web Interface

Usage:
    python start_server.py
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path

def main():
    """Start the API server and open the web interface."""

    print("=" * 60)
    print("🚀 ME ECU Engineering Assistant - Web Interface")
    print("=" * 60)
    print()

    # Check if we're in the right directory
    if not Path("api_server.py").exists():
        print("❌ Error: api_server.py not found")
        print("   Please run this script from the 'web/' directory")
        sys.exit(1)

    # Check if requirements are installed
    print("📦 Checking dependencies...")
    try:
        import fastapi
        import uvicorn
        import mlflow
        print("✅ All dependencies installed")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print()
        response = input("Install dependencies now? (y/n): ").strip().lower()
        if response == 'y':
            print("📥 Installing dependencies...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Dependencies installed")
        else:
            print("❌ Cannot start without dependencies")
            sys.exit(1)

    print()
    print("🌟 Starting API Server...")
    print("   - URL: http://localhost:8000")
    print("   - API Docs: http://localhost:8000/api/docs")
    print()

    # Get the absolute path to index.html
    web_dir = Path.cwd()
    index_path = web_dir / "index.html"

    if not index_path.exists():
        print("❌ Error: index.html not found")
        sys.exit(1)

    print(f"📂 Web Interface: {index_path}")
    print()
    print("⚠️  Press Ctrl+C to stop the server")
    print("=" * 60)
    print()

    # Ask if user wants to open browser
    response = input("Open web interface in browser? (y/n): ").strip().lower()
    if response == 'y':
        print("🌐 Opening browser...")
        webbrowser.open(f"file:///{index_path.as_posix()}")

    print()
    print("🎯 Server starting...")
    print("-" * 60)
    print()

    # Start the server
    try:
        subprocess.run([sys.executable, "api_server.py"])
    except KeyboardInterrupt:
        print()
        print("=" * 60)
        print("🛑 Server stopped by user")
        print("=" * 60)

if __name__ == "__main__":
    main()
