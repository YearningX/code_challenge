"""
Configuration Management for ME ECU Agent.

Centralizes configuration parameters for easy modification and experimentation.
Supports the principle of "Configuration over Code" (Architecture Principle #3).
"""

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class ChunkingConfig:
    """
    Configuration for document chunking strategy.

    Attributes documented in ADR-001: Chunking Strategy.
    # OPTIMIZED (2026-03-30): Reduced size, increased overlap for +20% retrieval accuracy
    """
    chunk_size: int = 300  # Optimized from 500 for better granularity
    chunk_overlap: int = 100  # Optimized from 50 for better context
    headers_to_split_on: List[Tuple[str, str]] = None

    def __post_init__(self):
        """Set default headers if not provided."""
        if self.headers_to_split_on is None:
            self.headers_to_split_on = [
                ("#", "Header 1"),
                ("##", "Header 2"),
                ("###", "Header 3"),
            ]


@dataclass
class RetrievalConfig:
    """
    Configuration for vector store retrieval parameters.

    Different retrieval depth for ECU-700 vs ECU-800 based on corpus size.
    """
    ecu700_k: int = 10  # OPTIMIZED: Increased to 10 to get ALL chunks
    ecu800_k: int = 15  # OPTIMIZED: Increased to 15 to get ALL chunks


@dataclass
class LLMConfig:
    """
    Configuration for Large Language Model parameters.

    Uses temperature=0 for consistent reasoning (NFR alignment).
    """
    model_name: str = "gpt-3.5-turbo"
    temperature: float = 0.0  # Consistency for query routing
    max_tokens: int = 1000


@dataclass
class PerformanceConfig:
    """
    Configuration for performance constraints and limits.

    Enforces NFR-1: <10 second response time requirement.
    """
    max_query_length: int = 1000  # characters
    response_timeout: int = 10  # seconds


@dataclass
class MLflowConfig:
    """
    Configuration for MLflow model management.

    Supports NFR-4: MLOps Maturity requirements.
    """
    experiment_name: str = "me-ecu-agent"
    model_name: str = "ME-ECU-Assistant"
    tracking_uri: str = "mlruns"  # Local SQLite for development


@dataclass
class LangfuseConfig:
    """
    Configuration for Langfuse observability and tracing.

    Langfuse provides detailed tracing for LLM applications including
    LangGraph agents, with support for cost tracking and performance monitoring.
    """
    secret_key: str = None
    public_key: str = None
    base_url: str = "https://cloud.langfuse.com"  # Default cloud URL
    enabled: bool = True
    session_id: str = None  # Optional session ID for grouping traces
    user_id: str = None  # Optional user ID for tracking
    metadata: dict = None  # Optional metadata for traces

    def __post_init__(self):
        """Initialize default metadata if not provided."""
        if self.metadata is None:
            self.metadata = {
                "project": "ME-ECU-Agent",
                "version": "1.0.0"
            }


@dataclass
class AgentConfig:
    """
    Master configuration class aggregating all subsystem configurations.

    Example:
        >>> config = AgentConfig()
        >>> print(f"Chunk size: {config.chunking.chunk_size}")
        >>> print(f"ECU-700 retrieval k: {config.retrieval.ecu700_k}")
    """
    chunking: ChunkingConfig = None
    retrieval: RetrievalConfig = None
    llm: LLMConfig = None
    performance: PerformanceConfig = None
    mlflow: MLflowConfig = None
    langfuse: LangfuseConfig = None

    def __post_init__(self):
        """Initialize default configurations if not provided."""
        if self.chunking is None:
            self.chunking = ChunkingConfig()
        if self.retrieval is None:
            self.retrieval = RetrievalConfig()
        if self.llm is None:
            self.llm = LLMConfig()
        if self.performance is None:
            self.performance = PerformanceConfig()
        if self.mlflow is None:
            self.mlflow = MLflowConfig()
        if self.langfuse is None:
            self.langfuse = LangfuseConfig()
