"""
Langfuse Integration Module for ME ECU Agent

Provides Langfuse tracing and observability for LangGraph agent execution.
Includes automatic instrumentation for LangChain callbacks and custom span tracking.
"""

import os
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from contextlib import contextmanager

try:
    from langfuse import Langfuse
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    print("Warning: Langfuse not available. Tracing disabled.")


class LangfuseIntegration:
    """
    Manages Langfuse tracing and observability for the ECU agent.

    Features:
    - Manual trace creation for custom tracking
    - Observation scoring and feedback
    - Trace URL generation for UI integration
    """

    def __init__(self, secret_key: str = None, public_key: str = None, base_url: str = None):
        """
        Initialize Langfuse integration.

        Args:
            secret_key: Langfuse secret key (from env or param)
            public_key: Langfuse public key (from env or param)
            base_url: Langfuse base URL (default: https://cloud.langfuse.com)
        """
        if not LANGFUSE_AVAILABLE:
            self.client = None
            self.enabled = False
            return

        # Get credentials from params or environment
        secret_key = secret_key or os.getenv("LANGFUSE_SECRET_KEY")
        public_key = public_key or os.getenv("LANGFUSE_PUBLIC_KEY")
        # Standard Langfuse 2.0 uses LANGFUSE_HOST; we support both
        base_url = base_url or os.getenv("LANGFUSE_HOST") or os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")
        
        # Ensure HOST is set for the @observe decorator to pick up the correct server
        if os.getenv("LANGFUSE_HOST") is None:
            os.environ["LANGFUSE_HOST"] = base_url

        if not secret_key or not public_key:
            print("Warning: Langfuse credentials not provided. Tracing disabled.")
            self.client = None
            self.enabled = False
            return

        try:
            # Initialize Langfuse client (Langfuse 2.x uses 'host' parameter)
            self.client = Langfuse(
                secret_key=secret_key,
                public_key=public_key,
                host=base_url
            )

            # Verify authentication
            if self.client.auth_check():
                self.enabled = True
                print("Langfuse tracing enabled successfully")
            else:
                print("Warning: Langfuse authentication failed. Tracing disabled.")
                self.enabled = False

        except Exception as e:
            print(f"Error initializing Langfuse: {e}")
            import traceback
            traceback.print_exc()
            self.client = None
            self.enabled = False

    @contextmanager
    def create_trace(self, name: str, user_id: str = None, session_id: str = None,
                     metadata: Dict[str, Any] = None):
        """
        Context manager for creating a Langfuse trace.

        Args:
            name: Trace name
            user_id: Optional user identifier
            session_id: Optional session identifier
            metadata: Optional metadata dictionary

        Yields:
            Langfuse Trace object or None

        Example:
            >>> with langfuse.create_trace("query_execution", user_id="user123") as trace:
            ...     # Your code here
            ...     if trace:
            ...         trace.update(output="Success")
        """
        trace = None
        if self.enabled and self.client:
            try:
                trace = self.client.trace(
                    name=name,
                    user_id=user_id,
                    session_id=session_id,
                    metadata=metadata or {}
                )
            except Exception as e:
                print(f"Error creating trace: {e}")

        try:
            yield trace
        finally:
            # Trace is automatically finalized by Langfuse
            pass

    def score_trace(self, trace_id: str, score_name: str, value: float,
                   comment: str = None) -> bool:
        """
        Add a score to an existing trace.

        Args:
            trace_id: The trace ID to score
            score_name: Name of the score metric
            value: Score value (typically 0-1 or 0-100)
            comment: Optional comment explaining the score

        Returns:
            True if scoring succeeded, False otherwise
        """
        if not self.enabled or not self.client:
            return False

        try:
            self.client.score(
                trace_id=trace_id,
                name=score_name,
                value=value,
                comment=comment
            )
            return True
        except Exception as e:
            print(f"Error scoring trace: {e}")
            return False

    def get_trace_url(self, trace_id: str) -> Optional[str]:
        """
        Generate a URL to view the trace in Langfuse UI.

        Args:
            trace_id: The trace ID

        Returns:
            URL string or None if not available
        """
        if not self.enabled:
            return None

        base_url = os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")
        return f"{base_url}/trace/{trace_id}"

    def get_public_trace_url(self, trace_id: str) -> Optional[str]:
        """
        Generate a publicly shareable trace URL.

        Args:
            trace_id: The trace ID

        Returns:
            Public URL string or None if not available
        """
        if not self.enabled:
            return None

        try:
            # Langfuse can generate public shareable URLs
            return self.client.get_public_url(trace_id)
        except Exception as e:
            print(f"Error generating public URL: {e}")
            return None

    def create_custom_span(self, trace_id: str, name: str,
                          start_time: float = None, end_time: float = None,
                          metadata: Dict[str, Any] = None) -> Optional[str]:
        """
        Create a custom span within a trace.

        Args:
            trace_id: Parent trace ID
            name: Span name
            start_time: Optional start time (default: now)
            end_time: Optional end time (default: now)
            metadata: Optional span metadata

        Returns:
            Span ID or None if failed
        """
        if not self.enabled or not self.client:
            return None

        try:
            span = self.client.span(
                trace_id=trace_id,
                name=name,
                start_time=start_time,
                end_time=end_time,
                metadata=metadata or {}
            )
            return span.observation_id
        except Exception as e:
            print(f"Error creating span: {e}")
            return None

    def flush(self) -> None:
        """
        Flush any pending events to Langfuse server.

        Call this to ensure all traces are sent before program exit.
        """
        if self.enabled and self.client:
            try:
                self.client.flush()
            except Exception as e:
                print(f"Error flushing Langfuse: {e}")


# Global Langfuse instance
_langfuse_instance: Optional[LangfuseIntegration] = None


def initialize_langfuse(secret_key: str = None, public_key: str = None,
                       base_url: str = None) -> LangfuseIntegration:
    """
    Initialize or get the global Langfuse integration instance.

    Args:
        secret_key: Langfuse secret key
        public_key: Langfuse public key
        base_url: Langfuse base URL

    Returns:
        LangfuseIntegration instance
    """
    global _langfuse_instance

    if _langfuse_instance is None:
        _langfuse_instance = LangfuseIntegration(
            secret_key=secret_key,
            public_key=public_key,
            base_url=base_url
        )

    return _langfuse_instance


def get_langfuse() -> Optional[LangfuseIntegration]:
    """
    Get the global Langfuse integration instance.

    Returns:
        LangfuseIntegration instance or None if not initialized
    """
    return _langfuse_instance
