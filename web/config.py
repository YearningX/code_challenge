"""
Configuration for ME ECU Assistant Web Server
"""

import os
from pathlib import Path

# Model Configuration
# Default to local model path (works both inside and outside Docker)
local_model_path = Path(__file__).parent.parent / "models" / "ecu_agent_model_local" / "ecu_agent_model"
MODEL_URI = os.getenv("MLFLOW_MODEL_URI", str(local_model_path))

# Alternative: Load from MLflow run (requires Databricks credentials)
# MODEL_URI = os.getenv("MLFLOW_MODEL_URI", "runs:/20f8fa846aea4dd183fa8bbe3739efb6/ecu_agent_model")

# Alternative: Load from local MLflow registry
# MODEL_URI = os.getenv("MLFLOW_MODEL_URI", "models:/ecu_agent_model/Production")

# Server Configuration
HOST = os.getenv("API_HOST", "0.0.0.0")
PORT = int(os.getenv("API_PORT", "18500"))
RELOAD = os.getenv("API_RELOAD", "true").lower() == "true"

# Langfuse Tracing Configuration
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_BASE_URL = os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
WEB_DIR = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"

# Print configuration on import
print("=" * 60)
print("ME ECU Assistant - Configuration")
print("=" * 60)
print(f"Model URI: {MODEL_URI}")
print(f"Server: {HOST}:{PORT}")
print(f"Reload: {RELOAD}")
print(f"Langfuse Tracing: {bool(LANGFUSE_SECRET_KEY and LANGFUSE_PUBLIC_KEY)}")
if LANGFUSE_SECRET_KEY and LANGFUSE_PUBLIC_KEY:
    print(f"Langfuse Base URL: {LANGFUSE_BASE_URL}")
    print(f"Langfuse Public Key: {LANGFUSE_PUBLIC_KEY[:20]}...")
print("=" * 60)
