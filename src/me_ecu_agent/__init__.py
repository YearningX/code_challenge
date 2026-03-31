"""
ME ECU Engineering Assistant Agent Package

Epic 2 Complete: Production Model Serving
- MLflow PyFunc model wrapper
- Comprehensive error handling
- Input validation and sanitization
- REST API serving capability
"""

__version__ = "0.2.0"

# Core components
from me_ecu_agent.config import (
    ChunkingConfig,
    LLMConfig,
    PerformanceConfig,
    RetrievalConfig
)

# MLflow model
from me_ecu_agent.mlflow_model import ECUAgentMLflowModel, create_mlflow_model

# Error handling
from me_ecu_agent.error_handling import (
    ECUAgentError,
    ValidationError,
    RetrievalError,
    LLMError,
    TimeoutError,
    ModelLoadError,
    InputValidator,
    RetryHandler,
    ErrorHandler,
    create_input_validator,
    create_retry_handler,
    create_error_handler
)

__all__ = [
    # Version
    "__version__",

    # Config
    "ChunkingConfig",
    "LLMConfig",
    "PerformanceConfig",
    "RetrievalConfig",

    # MLflow
    "ECUAgentMLflowModel",
    "create_mlflow_model",

    # Error handling
    "ECUAgentError",
    "ValidationError",
    "RetrievalError",
    "LLMError",
    "TimeoutError",
    "ModelLoadError",
    "InputValidator",
    "RetryHandler",
    "ErrorHandler",
    "create_input_validator",
    "create_retry_handler",
    "create_error_handler",
]
