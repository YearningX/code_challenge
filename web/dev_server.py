"""
Local development server with frontend hot-reload support

Usage:
1. Ensure dependencies are installed: pip install -r requirements.txt
2. Run: python dev_server.py
3. Access: http://localhost:18500
4. Modify index.html and refresh browser to see changes immediately

Benefits:
✅ No need to rebuild Docker images
✅ Real-time frontend updates
✅ Hot-reload and auto-restart support
✅ Full production environment functionality
"""

import logging
import os
import sys
from pathlib import Path

import uvicorn

# Development environment specific configuration
DEV_CONFIG = {
    "host": "127.0.0.1",  # Local access
    "port": 18500,
    "reload": True,  # Enable hot-reload
    "reload_dirs": [str(Path(__file__).parent)],  # Monitor current directory
    "log_level": "info",
    "access_log": True
}

def enhance_root_route():
    """
    Enhance root route, add development mode prompt
    Note: This function needs to be injected into api_server.py
    Due to technical limitations, we will provide instructions at startup
    """
    pass


def add_dev_endpoints():
    """
    Add development-specific endpoints
    Note: These endpoints need to be added to the app in api_server.py
    Due to technical limitations, we will provide instructions at startup
    """
    pass


def main():
    """Start development server"""
    print("\n" + "="*70)
    print("🚀 ME ECU Assistant - Local Development Server")
    print("="*70)
    print(f"\n✅ Development mode enabled")
    print(f"✅ Frontend hot-reload: Enabled")
    print(f"✅ Service URL: http://{DEV_CONFIG['host']}:{DEV_CONFIG['port']}")
    print(f"\n💡 Usage tips:")
    print(f"   - Modify index.html and refresh browser (F5) to see changes")
    print(f"   - Server auto-restarts on Python code changes")
    print(f"   - All production features available")
    print(f"\n📝 Development tips:")
    print(f"   - Full API documentation: http://localhost:18500/docs")
    print(f"   - Health check: http://localhost:18500/api/health")
    print(f"\n⚠️  Note: This is development environment, use Docker for production")
    print("="*70 + "\n")

    try:
        # Run api_server directly, using module path to support hot-reload
        # api_server.py already has complete lifespan management, will auto-load model
        uvicorn.run(
            "api_server:app",
            host=DEV_CONFIG["host"],
            port=DEV_CONFIG["port"],
            reload=DEV_CONFIG["reload"],
            reload_dirs=DEV_CONFIG["reload_dirs"],
            log_level=DEV_CONFIG["log_level"],
            access_log=DEV_CONFIG["access_log"]
        )
    except KeyboardInterrupt:
        print("\n\n✅ Development server stopped")
    except Exception as e:
        print(f"\n❌ Startup failed: {e}")
        print("\n💡 Solutions:")
        print("   1. Check dependencies: pip install -r requirements.txt")
        print("   2. Check MLflow model availability")
        print("   3. Check if port 18500 is available")
        print("   4. Review error logs above")


if __name__ == "__main__":
    main()
