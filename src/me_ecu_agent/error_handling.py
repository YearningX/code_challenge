"""
Error Handling and Input Validation Module

OPTIMIZED (2026-03-31): Comprehensive error handling, validation,
and retry logic for production resilience.

Features:
- Input validation and sanitization
- Custom exception hierarchy
- Retry logic with exponential backoff
- Structured error responses
- Performance monitoring
"""

import logging
import time
from enum import Enum
from typing import Any, Dict, Optional, Union

from me_ecu_agent.config import PerformanceConfig


logger = logging.getLogger(__name__)


class ErrorCode(Enum):
    """Error code enumeration for categorization."""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RETRIEVAL_ERROR = "RETRIEVAL_ERROR"
    LLM_ERROR = "LLM_ERROR"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    MODEL_LOAD_ERROR = "MODEL_LOAD_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


class ECUAgentError(Exception):
    """Base exception for ECU Agent errors."""

    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize ECU Agent error.

        Args:
            message: Error message
            error_code: Error category code
            details: Additional error details
        """
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(ECUAgentError):
    """Raised when input validation fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.VALIDATION_ERROR, details)


class RetrievalError(ECUAgentError):
    """Raised when document retrieval fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.RETRIEVAL_ERROR, details)


class LLMError(ECUAgentError):
    """Raised when LLM inference fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.LLM_ERROR, details)


class TimeoutException(ECUAgentError):
    """Raised when operation times out."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.TIMEOUT_ERROR, details)


class ModelLoadError(ECUAgentError):
    """Raised when model loading fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.MODEL_LOAD_ERROR, details)


class InputValidator:
    """
    Validates and sanitizes user input queries.
    """

    def __init__(self, config: PerformanceConfig):
        """
        Initialize input validator.

        Args:
            config: Performance configuration
        """
        self.config = config

    def validate_query(self, query: Any) -> str:
        """
        Validate and sanitize input query.

        Args:
            query: Raw input query

        Returns:
            Sanitized query string

        Raises:
            ValidationError: If query is invalid
        """
        # Type check
        if not isinstance(query, str):
            raise ValidationError(
                f"Query must be a string, got {type(query).__name__}",
                {"query_type": str(type(query)), "query": str(query)}
            )

        # Strip whitespace
        sanitized = query.strip()

        # Empty check
        if not sanitized:
            raise ValidationError(
                "Query cannot be empty",
                {"original_query": query}
            )

        # Length check
        if len(sanitized) > self.config.max_query_length:
            raise ValidationError(
                f"Query exceeds maximum length of {self.config.max_query_length} characters",
                {
                    "query_length": len(sanitized),
                    "max_length": self.config.max_query_length,
                    "query_preview": sanitized[:100]
                }
            )

        # Content sanity check (remove potentially harmful content)
        # This is a basic implementation - extend based on requirements
        if self._contains_injection_patterns(sanitized):
            logger.warning(f"Potential injection pattern detected in query: {sanitized[:50]}...")
            # For now, just log but don't reject
            # In production, you might want to reject or sanitize further

        return sanitized

    def _contains_injection_patterns(self, query: str) -> bool:
        """
        Check for potential prompt injection patterns.

        Args:
            query: Query string

        Returns:
            True if suspicious patterns found
        """
        suspicious_patterns = [
            "ignore previous instructions",
            "disregard",
            "forget everything",
            "new instructions:",
            "system:",
        ]

        query_lower = query.lower()
        return any(pattern in query_lower for pattern in suspicious_patterns)


class RetryHandler:
    """
    Handles retry logic with exponential backoff for transient failures.
    """

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 10.0,
        backoff_factor: float = 2.0
    ):
        """
        Initialize retry handler.

        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Initial delay between retries (seconds)
            max_delay: Maximum delay between retries (seconds)
            backoff_factor: Multiplier for delay after each retry
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor

    def retry_with_backoff(
        self,
        func,
        *args,
        retry_on_exceptions: tuple = (Exception,),
        **kwargs
    ):
        """
        Execute function with retry logic.

        Args:
            func: Function to execute
            *args: Function arguments
            retry_on_exceptions: Exception types that trigger retry
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            Exception: If all retries exhausted
        """
        last_exception = None
        delay = self.base_delay

        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)

            except retry_on_exceptions as e:
                last_exception = e

                if attempt < self.max_retries:
                    logger.warning(
                        f"Attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    time.sleep(delay)
                    delay = min(delay * self.backoff_factor, self.max_delay)
                else:
                    logger.error(
                        f"All {self.max_retries + 1} attempts failed. "
                        f"Final error: {e}"
                    )

        raise last_exception


class ErrorHandler:
    """
    Centralized error handling and response formatting.
    """

    def __init__(self):
        """Initialize error handler."""
        self.error_counts = {code: 0 for code in ErrorCode}
        self.total_requests = 0

    def handle_error(
        self,
        error: Exception,
        query: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle error and create structured error response.

        Args:
            error: Caught exception
            query: Original query (if available)
            context: Additional context information

        Returns:
            Structured error response dictionary
        """
        self.total_requests += 1

        # Determine error code
        if isinstance(error, ECUAgentError):
            error_code = error.error_code
            message = error.message
            details = error.details
        else:
            error_code = ErrorCode.UNKNOWN_ERROR
            message = str(error)
            details = {"error_type": type(error).__name__}

        # Increment error counter
        self.error_counts[error_code] += 1

        # Log error
        logger.error(
            f"Error occurred: {error_code.value} - {message}",
            extra={
                "query": query,
                "context": context,
                "details": details
            }
        )

        # Create structured response
        error_response = {
            "response": self._create_user_friendly_message(error_code, message),
            "query": query or "",
            "status": "error",
            "error": {
                "code": error_code.value,
                "message": message,
                "details": details
            }
        }

        return error_response

    def _create_user_friendly_message(
        self,
        error_code: ErrorCode,
        technical_message: str
    ) -> str:
        """
        Create user-friendly error message.

        Args:
            error_code: Error code
            technical_message: Technical error message

        Returns:
            User-friendly error message
        """
        messages = {
            ErrorCode.VALIDATION_ERROR: (
                "I couldn't process your query. Please ensure it's a valid "
                "question about ECU products and try again."
            ),
            ErrorCode.RETRIEVAL_ERROR: (
                "I encountered an issue retrieving the relevant information. "
                "Please try rephrasing your question or contact support."
            ),
            ErrorCode.LLM_ERROR: (
                "I had trouble generating a response. Please try again later "
                "or contact support if the issue persists."
            ),
            ErrorCode.TIMEOUT_ERROR: (
                "The request took too long to process. Please try a more "
                "specific question or contact support."
            ),
            ErrorCode.MODEL_LOAD_ERROR: (
                "The system is currently unavailable. Please try again later "
                "or contact support."
            ),
            ErrorCode.UNKNOWN_ERROR: (
                "An unexpected error occurred. Please try again or contact support."
            )
        }

        base_message = messages.get(error_code, messages[ErrorCode.UNKNOWN_ERROR])

        # Add technical details in development mode
        # In production, you might want to hide these
        return f"{base_message}"

    def get_error_statistics(self) -> Dict[str, Any]:
        """
        Get error statistics.

        Returns:
            Dictionary with error statistics
        """
        if self.total_requests == 0:
            return {"total_requests": 0, "error_rate": 0.0, "errors_by_type": {}}

        return {
            "total_requests": self.total_requests,
            "error_rate": sum(self.error_counts.values()) / self.total_requests,
            "errors_by_type": {
                code.value: count
                for code, count in self.error_counts.items()
                if count > 0
            }
        }


def create_input_validator(config: PerformanceConfig) -> InputValidator:
    """
    Factory function to create input validator.

    Args:
        config: Performance configuration

    Returns:
        InputValidator instance
    """
    return InputValidator(config)


def create_retry_handler(
    max_retries: int = 3,
    base_delay: float = 1.0
) -> RetryHandler:
    """
    Factory function to create retry handler.

    Args:
        max_retries: Maximum retry attempts
        base_delay: Initial delay

    Returns:
        RetryHandler instance
    """
    return RetryHandler(max_retries=max_retries, base_delay=base_delay)


def create_error_handler() -> ErrorHandler:
    """
    Factory function to create error handler.

    Returns:
        ErrorHandler instance
    """
    return ErrorHandler()
