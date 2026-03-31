"""
MLflow PyFunc Model Wrapper for ECU Agent

OPTIMIZED (2026-03-31): Production-ready MLflow model with comprehensive
error handling, input validation, and monitoring.

Features:
- Multi-format input support (DataFrame, list, string, dict)
- Input validation and sanitization
- Structured error handling with fallback
- Performance monitoring and logging
- Batch processing with error isolation
"""

import logging
import os
import time
from typing import Any, Dict, List, Union

import mlflow
import pandas as pd
from langchain_core.messages import HumanMessage
from mlflow.pyfunc import PythonModel

from me_ecu_agent.config import LLMConfig, PerformanceConfig, RetrievalConfig


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ECUAgentMLflowModel(PythonModel):
    """
    Production-ready MLflow PyFunc wrapper for the LangGraph ECU Agent.

    Features:
    - Flexible input format handling
    - Comprehensive error handling
    - Input validation and sanitization
    - Performance monitoring
    - Batch processing with error isolation
    """

    def __init__(self):
        """Initialize the model wrapper."""
        self.agent = None
        self.graph = None
        self.config = LLMConfig()
        self.perf_config = PerformanceConfig()
        self.retrieval_config = RetrievalConfig()

    def load_context(self, context) -> None:
        """
        Load the LangGraph agent and vector stores from model artifacts.

        Args:
            context: MLflow context containing artifacts and model configuration
        """
        try:
            logger.info("Loading ECU Agent model context...")

            # Setup LangSmith tracing if environment variables are set
            if os.getenv("LANGCHAIN_TRACING_V2") == "true":
                logger.info("LangSmith tracing is enabled via environment variables")
                logger.info(f"Project: {os.getenv('LANGCHAIN_PROJECT', 'default')}")
            else:
                logger.warning("LangSmith tracing not enabled (LANGCHAIN_TRACING_V2 not set to 'true')")

            # Import here to avoid serialization issues
            from me_ecu_agent.vectorstore import load_vector_stores
            from me_ecu_agent.graph import ECUQueryAgent

            # Load vector stores from artifacts
            vector_store_dir = context.artifacts.get("vector_stores")
            if not vector_store_dir:
                raise ValueError("Vector stores artifact not found in model context")

            # Fix cross-platform path separator issue (Windows paths on Linux)
            # Replace backslashes with forward slashes for Linux compatibility
            vector_store_dir = str(vector_store_dir).replace("\\", "/")

            logger.info(f"Loading vector stores from {vector_store_dir}")
            store_700, store_800 = load_vector_stores(vector_store_dir)

            # Create agent and register retrievers
            logger.info("Creating ECU Query Agent...")
            self.agent = ECUQueryAgent(config=self.config)

            if store_700:
                retriever_700 = store_700.as_retriever(
                    search_kwargs={"k": self.retrieval_config.ecu700_k}
                )
                self.agent.register_retriever("ECU-700", retriever_700)
                logger.info("Registered ECU-700 retriever")

            if store_800:
                retriever_800 = store_800.as_retriever(
                    search_kwargs={"k": self.retrieval_config.ecu800_k}
                )
                self.agent.register_retriever("ECU-800", retriever_800)
                logger.info("Registered ECU-800 retriever")

            # Create the graph
            logger.info("Creating LangGraph workflow...")
            self.graph = self.agent.create_graph()
            logger.info("LangGraph workflow created successfully")

            logger.info("Model context loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load model context: {e}")
            raise RuntimeError(f"Model loading failed: {str(e)}")

    def _validate_input(self, query: str) -> str:
        """
        Validate and sanitize input query.

        Args:
            query: Raw input query

        Returns:
            Sanitized query

        Raises:
            ValueError: If query is invalid
        """
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string")

        # Strip whitespace
        query = query.strip()

        # Check length
        if len(query) > self.perf_config.max_query_length:
            raise ValueError(
                f"Query too long (max {self.perf_config.max_query_length} characters)"
            )

        if len(query) == 0:
            raise ValueError("Query cannot be empty")

        return query

    def _normalize_input(self, model_input: Any) -> List[str]:
        """
        Normalize various input formats to a list of queries.

        Args:
            model_input: Input in various formats (DataFrame, list, string, dict)

        Returns:
            List of query strings

        Raises:
            ValueError: If input format is unsupported
        """
        queries = []

        if isinstance(model_input, pd.DataFrame):
            # DataFrame input
            if "query" in model_input.columns:
                queries = model_input["query"].tolist()
            elif "question" in model_input.columns:
                queries = model_input["question"].tolist()
            else:
                # Use first column
                queries = model_input.iloc[:, 0].tolist()

        elif isinstance(model_input, list):
            # List input
            if not all(isinstance(q, (str, dict)) for q in model_input):
                raise ValueError("All list items must be strings or dictionaries")

            for item in model_input:
                if isinstance(item, str):
                    queries.append(item)
                elif isinstance(item, dict):
                    queries.append(item.get("query", item.get("question", "")))

        elif isinstance(model_input, str):
            # Single string input
            queries = [model_input]

        elif isinstance(model_input, dict):
            # Single dictionary input
            query = model_input.get("query", model_input.get("question", ""))
            queries = [query]

        else:
            raise ValueError(
                f"Unsupported input type: {type(model_input)}. "
                "Supported types: DataFrame, list, string, dict"
            )

        # Validate we have queries
        if not queries:
            raise ValueError("No queries found in input")

        return queries

    def _execute_query(self, query: str) -> Dict[str, Any]:
        """
        Execute a single query through the LangGraph agent.

        Args:
            query: Validated query string

        Returns:
            Dictionary containing response and metadata
        """
        start_time = time.time()

        try:
            # Prepare initial state with all required fields
            initial_state = {
                "query": query,
                "detected_product_line": "unknown",
                "retrieved_context": "",
                "response": "",
                "messages": [HumanMessage(content=query)]
            }

            # Execute graph
            result = self.graph.invoke(initial_state)

            # Extract response
            last_message = result.get("messages", [])[-1]
            response = last_message.content if last_message else result.get("response", "")

            # Calculate latency
            latency = time.time() - start_time

            logger.info(f"Query executed successfully in {latency:.2f}s: {query[:50]}...")

            return {
                "response": response,
                "query": query,
                "rewritten_query": result.get("rewritten_query", ""),
                "detected_product_line": result.get("detected_product_line", "unknown"),
                "retrieved_docs": result.get("retrieved_docs", []),
                "status": "success",
                "latency_seconds": round(latency, 2),
                "error": None
            }

        except Exception as e:
            latency = time.time() - start_time
            error_msg = f"Query execution failed: {str(e)}"
            logger.error(f"{error_msg} - Query: {query[:50]}...")

            return {
                "response": f"I apologize, but I encountered an error processing your query: {str(e)}",
                "query": query,
                "status": "error",
                "latency_seconds": round(latency, 2),
                "error": str(e)
            }

    def predict(self, context, model_input: Any) -> Union[List[str], List[Dict[str, Any]]]:
        """
        Run prediction on input queries.

        Args:
            context: MLflow context
            model_input: Input in various formats (DataFrame, list, string, dict)

        Returns:
            List of responses (simple) or list of result dictionaries (detailed)
        """
        if self.graph is None:
            raise RuntimeError("Model not loaded. Call load_context() first.")

        logger.info(f"Processing {type(model_input).__name__} input...")

        try:
            # Normalize input to list of queries
            raw_queries = self._normalize_input(model_input)

            # Validate and sanitize queries
            validated_queries = []
            for i, query in enumerate(raw_queries):
                try:
                    validated_query = self._validate_input(query)
                    validated_queries.append(validated_query)
                except ValueError as e:
                    logger.warning(f"Query {i} validation failed: {e}")
                    # Add error response for invalid query
                    return [{
                        "response": f"Invalid query: {str(e)}",
                        "query": str(query),
                        "status": "validation_error",
                        "latency_seconds": 0,
                        "error": str(e)
                    }]

            # Execute queries (batch processing with error isolation)
            results = []
            for query in validated_queries:
                result = self._execute_query(query)
                results.append(result)

            # Always return the full detailed results to include metadata
            return results

        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise RuntimeError(f"Prediction error: {str(e)}")


def create_mlflow_model() -> ECUAgentMLflowModel:
    """
    Factory function to create MLflow model instance.

    Returns:
        ECUAgentMLflowModel instance
    """
    return ECUAgentMLflowModel()
