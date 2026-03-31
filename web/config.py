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

# LangSmith Tracing Configuration
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "true").lower() == "true"
LANGCHAIN_API_KEY = os.getenv(
    "LANGCHAIN_API_KEY",
    "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"
)
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "me-ecu-assistant-production")
LANGCHAIN_ENDPOINT = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")

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
print(f"LangSmith Tracing: {LANGCHAIN_TRACING_V2}")
if LANGCHAIN_TRACING_V2:
    print(f"LangSmith Project: {LANGCHAIN_PROJECT}")
    print(f"LangSmith API Key: {LANGCHAIN_API_KEY[:20]}...")
print("=" * 60)
