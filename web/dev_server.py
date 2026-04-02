"""
本地开发服务器 - 支持前端热重载

使用方法：
1. 确保已安装依赖：pip install -r requirements.txt
2. 运行：python dev_server.py
3. 访问：http://localhost:18500
4. 修改 index.html 后直接刷新浏览器即可看到效果

优势：
✅ 无需重新构建Docker镜像
✅ 前端修改实时生效
✅ 支持热重载和自动重启
✅ 保留完整的生产环境功能
"""

import logging
import os
import sys
from pathlib import Path

import uvicorn

# 开发环境特定配置
DEV_CONFIG = {
    "host": "127.0.0.1",  # 本地访问
    "port": 18500,
    "reload": True,  # 启用热重载
    "reload_dirs": [str(Path(__file__).parent)],  # 监控当前目录
    "log_level": "info",
    "access_log": True
}

def enhance_root_route():
    """
    增强根路由，添加开发模式提示
    注意：这个功能需要注入到 api_server.py 中
    由于技术限制，我们将在启动时提供说明
    """
    pass


def add_dev_endpoints():
    """
    添加开发环境专用的端点
    注意：这些端点需要添加到 api_server.py 的 app 中
    由于技术限制，我们将在启动时提供说明
    """
    pass


def main():
    """启动开发服务器"""
    print("\n" + "="*70)
    print("🚀 ME ECU Assistant - 本地开发服务器")
    print("="*70)
    print(f"\n✅ 开发模式已启用")
    print(f"✅ 前端热重载：已开启")
    print(f"✅ 服务地址：http://{DEV_CONFIG['host']}:{DEV_CONFIG['port']}")
    print(f"\n💡 使用提示：")
    print(f"   - 修改 index.html 后直接刷新浏览器 (F5) 即可")
    print(f"   - 修改 Python 代码会自动重启服务器")
    print(f"   - 所有生产环境功能均保留")
    print(f"\n📝 开发提示：")
    print(f"   - 查看完整API文档：http://localhost:18500/docs")
    print(f"   - 健康检查：http://localhost:18500/api/health")
    print(f"\n⚠️  注意：这是开发环境，生产环境请使用 Docker")
    print("="*70 + "\n")

    try:
        # 直接运行 api_server，使用模块路径以支持热重载
        # api_server.py 中已有完整的 lifespan 管理，会自动加载模型
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
        print("\n\n✅ 开发服务器已停止")
    except Exception as e:
        print(f"\n❌ 启动失败：{e}")
        print("\n💡 解决方案：")
        print("   1. 检查依赖是否安装：pip install -r requirements.txt")
        print("   2. 检查MLflow模型是否可用")
        print("   3. 检查端口18500是否被占用")
        print("   4. 查看上方错误日志")


if __name__ == "__main__":
    main()

