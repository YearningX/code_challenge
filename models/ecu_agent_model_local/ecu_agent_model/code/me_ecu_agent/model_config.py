"""
Model Configuration with Fallback Support

Supports OpenAI and Qwen (Alibaba Cloud) as fallback for China deployment.
Automatically switches based on environment variable availability.

Features:
- Separate configuration for LLM and Embeddings
- Provider selection via environment variables (LLM_PROVIDER, EMBEDDINGS_PROVIDER)
- Automatic fallback when preferred provider is unavailable
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class EmbeddingsConfig:
    """
    Configuration for embeddings models.

    Supports OpenAI and Qwen embeddings with automatic provider selection.
    """

    model_name: str
    api_key: str
    base_url: Optional[str] = None
    provider: str = "openai"  # 'openai' or 'qwen'

    @classmethod
    def from_env(cls) -> 'EmbeddingsConfig':
        """
        Create embeddings configuration from environment variables.

        Environment Variables:
            EMBEDDINGS_PROVIDER: Explicit provider choice ('openai', 'qwen', or 'auto')
            OPENAI_API_KEY: OpenAI API key (for OpenAI embeddings)
            QWEN_API_KEY: Qwen/DashScope API key (for Qwen embeddings)
            QWEN_BASE_URL: Qwen base URL

        Returns:
            EmbeddingsConfig: Configured embeddings instance
        """
        provider_preference = os.getenv("EMBEDDINGS_PROVIDER", "auto").lower()
        openai_key = os.getenv("OPENAI_API_KEY", "").strip('"').strip("'")
        qwen_key = os.getenv("QWEN_API_KEY", "").strip('"').strip("'")
        qwen_base_url = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

        def create_openai_embeddings():
            if not openai_key or openai_key in ["", "sk-xxx", "sk-your-openai-api-key-here"]:
                raise ValueError("OpenAI API key not configured")
            return cls(
                model_name="text-embedding-ada-002",
                api_key=openai_key,
                base_url="https://api.openai.com/v1",
                provider="openai"
            )

        def create_qwen_embeddings():
            if not qwen_key or qwen_key in ["", "sk-xxx", "sk-your-qwen-api-key-here"]:
                raise ValueError("Qwen API key not configured")
            # For Qwen embeddings with LangChain's OpenAIEmbeddings,
            # we need to use OpenAI's format but with Qwen's endpoint
            return cls(
                model_name="text-embedding-v2",
                api_key=qwen_key,
                base_url=qwen_base_url,
                provider="qwen"
            )

        # Provider selection logic
        if provider_preference == "openai":
            try:
                return create_openai_embeddings()
            except ValueError as e:
                raise ValueError(f"EMBEDDINGS_PROVIDER is 'openai' but: {str(e)}")

        elif provider_preference == "qwen":
            try:
                return create_qwen_embeddings()
            except ValueError as e:
                raise ValueError(f"EMBEDDINGS_PROVIDER is 'qwen' but: {str(e)}")

        else:  # auto mode
            # Try OpenAI first, fallback to Qwen
            try:
                return create_openai_embeddings()
            except ValueError:
                try:
                    return create_qwen_embeddings()
                except ValueError:
                    raise ValueError(
                        "No embeddings API key found! Please configure either OPENAI_API_KEY "
                        "or QWEN_API_KEY in .env file."
                    )

    def is_openai(self) -> bool:
        """Check if using OpenAI provider."""
        return self.provider == "openai"

    def is_qwen(self) -> bool:
        """Check if using Qwen provider."""
        return self.provider == "qwen"

    def __repr__(self) -> str:
        """String representation with provider info."""
        return (
            f"EmbeddingsConfig(provider={self.provider}, "
            f"model={self.model_name})"
        )


@dataclass
class ModelConfig:
    """
    Unified model configuration supporting OpenAI and Qwen as fallback.

    Priority:
    1. If OPENAI_API_KEY is available -> Use OpenAI (gpt-3.5-turbo)
    2. Else if QWEN_API_KEY is available -> Use Qwen (qwen-plus)
    3. Else -> Raise error

    Usage:
        >>> config = ModelConfig.from_env()
        >>> print(f"Using model: {config.model_name}")
        >>> print(f"Base URL: {config.base_url}")
    """

    # Model configuration
    model_name: str
    api_key: str
    base_url: Optional[str] = None
    embedding_model: str = "text-embedding-ada-002"  # OpenAI default

    # LLM parameters
    temperature: float = 0.0
    max_tokens: int = 1000

    # Provider info
    provider: str = "openai"  # 'openai' or 'qwen'

    @classmethod
    def from_env(cls) -> 'ModelConfig':
        """
        Create configuration from environment variables.

        Supports explicit provider selection via LLM_PROVIDER env variable.
        If not specified, automatically detects available API keys.

        Environment Variables:
            LLM_PROVIDER: Explicit provider choice ('openai', 'qwen', or 'auto')
            OPENAI_API_KEY: OpenAI API key
            QWEN_API_KEY: Qwen/DashScope API key
            OPENAI_BASE_URL: Optional custom base URL

        Returns:
            ModelConfig: Configured model instance

        Raises:
            ValueError: If no API key is available or provider is not usable
        """
        # Get provider preference from .env file
        provider_preference = os.getenv("LLM_PROVIDER", "auto").lower()
        openai_key = os.getenv("OPENAI_API_KEY", "")
        qwen_key = os.getenv("QWEN_API_KEY", "")

        # Clean up keys (remove quotes if present)
        openai_key = openai_key.strip('"').strip("'")
        qwen_key = qwen_key.strip('"').strip("'")

        # Helper function to create OpenAI config
        def create_openai_config():
            if not openai_key or openai_key in ["", "sk-xxx", "sk-your-openai-api-key-here"]:
                raise ValueError("OpenAI API key not configured")
            return cls(
                model_name="gpt-3.5-turbo",
                api_key=openai_key,
                base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
                embedding_model="text-embedding-ada-002",
                temperature=0.0,
                max_tokens=1000,
                provider="openai"
            )

        # Helper function to create Qwen config
        def create_qwen_config():
            if not qwen_key or qwen_key in ["", "sk-xxx", "sk-your-openai-api-key-here"]:
                raise ValueError("Qwen API key not configured")
            return cls(
                model_name="qwen-plus",
                api_key=qwen_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                embedding_model="text-embedding-v2",
                temperature=0.0,
                max_tokens=1000,
                provider="qwen"
            )

        # Provider selection logic based on LLM_PROVIDER env variable
        if provider_preference == "openai":
            # Force use OpenAI
            try:
                return create_openai_config()
            except ValueError as e:
                raise ValueError(f"LLM_PROVIDER is set to 'openai' but: {str(e)}")

        elif provider_preference == "qwen":
            # Force use Qwen
            try:
                return create_qwen_config()
            except ValueError as e:
                raise ValueError(f"LLM_PROVIDER is set to 'qwen' but: {str(e)}")

        else:  # auto mode
            # Automatic selection: try OpenAI first, fallback to Qwen
            try:
                return create_openai_config()
            except ValueError:
                try:
                    return create_qwen_config()
                except ValueError:
                    raise ValueError(
                        "No API key found! Please configure either OPENAI_API_KEY or QWEN_API_KEY in .env file.\n"
                        "See .env.example for configuration examples."
                    )

    def is_openai(self) -> bool:
        """Check if using OpenAI provider."""
        return self.provider == "openai"

    def is_qwen(self) -> bool:
        """Check if using Qwen provider."""
        return self.provider == "qwen"

    def get_chat_init_params(self) -> dict:
        """Get initialization parameters for ChatOpenAI."""
        params = {
            "model": self.model_name,
            "api_key": self.api_key,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        # Add base_url for Qwen
        if self.base_url:
            params["base_url"] = self.base_url

        return params

    def __repr__(self) -> str:
        """String representation with provider info."""
        return (
            f"ModelConfig(provider={self.provider}, "
            f"model={self.model_name}, "
            f"embedding={self.embedding_model})"
        )


# Singleton instance for easy access
_model_config: Optional[ModelConfig] = None


def get_model_config() -> ModelConfig:
    """
    Get or create global model configuration instance.

    Returns:
        ModelConfig: Cached or newly created configuration
    """
    global _model_config
    if _model_config is None:
        _model_config = ModelConfig.from_env()
    return _model_config


def reset_model_config():
    """Reset global model configuration (useful for testing)."""
    global _model_config
    _model_config = None


# Singleton instance for embeddings config
_embeddings_config: Optional[EmbeddingsConfig] = None


def get_embeddings_config() -> EmbeddingsConfig:
    """
    Get or create global embeddings configuration instance.

    Returns:
        EmbeddingsConfig: Cached or newly created configuration
    """
    global _embeddings_config
    if _embeddings_config is None:
        _embeddings_config = EmbeddingsConfig.from_env()
    return _embeddings_config


def reset_embeddings_config():
    """Reset global embeddings configuration (useful for testing)."""
    global _embeddings_config
    _embeddings_config = None
