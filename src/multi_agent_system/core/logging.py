"""
Structured logging configuration using structlog.

This module sets up structured logging for the entire application,
providing consistent log formatting, context injection, and log levels.
"""

import logging
import sys
from typing import Any

import structlog


def setup_logging(log_level: str = "INFO", json_logs: bool = False) -> None:
    """
    Configure structured logging for the application.

    Requirements:
    1. Use structlog for structured logging
    2. Support both development (console) and production (JSON) formats
    3. Add processors for timestamps, log levels, and context
    4. Configure standard library logging integration
    5. Add request ID tracking for API requests
    6. Support different log levels per environment

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: If True, output logs in JSON format for production

    Example Implementation:
    ```python
    import structlog
    from structlog.processors import JSONRenderer, add_log_level, TimeStamper

    # Configure processors
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if json_logs:
        # Production: JSON output
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Development: Pretty console output
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(log_level)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )
    ```

    Expected Input: log_level="INFO", json_logs=False
    Expected Output: Configured logging system
    """
    # Define the processing pipeline for log events in order of execution
    processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    # Add appropriate renderer based on environment
    if json_logs:
        processors.append(structlog.processors.JSONRenderer()) # Production: JSON output
    else:
        processors.append(structlog.dev.ConsoleRenderer()) # Development: Pretty console output

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger( # Filter log messages based on level
            logging.getLevelName(log_level)
        ),
        context_class=dict, # Uses Python dicts to store log context
        logger_factory=structlog.PrintLoggerFactory(), # Prints log messages to stdout
        cache_logger_on_first_use=True, # Cache logger instances to improve performance
    )

    # Configure standard library logging to integrate with structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )


def get_logger(name: str) -> Any:
    """
    Get a logger instance for a specific module.

    Args:
        name: Logger name (typically __name__ of the module)

    Returns:
        Logger instance with structured logging capabilities

    TODO: Implement logger factory
    Example Usage:
    ```python
    logger = get_logger(__name__)

    # Basic logging
    logger.info("Processing order", order_id="ORD-123", customer="CUST-456")

    # With context
    logger = logger.bind(request_id="req-789", user_id="user-123")
    logger.info("Order processed successfully")

    # Error logging
    try:
        process_order()
    except Exception as e:
        logger.exception("Order processing failed", order_id="ORD-123")
    ```

    Expected Input: Module name string
    Expected Output: Structured logger instance
    """
    return structlog.get_logger(name)


# TODO: Add utility functions for logging context management
# Example:
# def set_request_id(request_id: str) -> None:
#     """Set request ID in logging context."""
#     structlog.contextvars.bind_contextvars(request_id=request_id)
#
# def clear_request_context() -> None:
#     """Clear request-specific context."""
#     structlog.contextvars.clear_contextvars()

