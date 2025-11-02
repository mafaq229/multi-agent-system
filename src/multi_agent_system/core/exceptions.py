"""
Custom exception classes for the multi-agent system.

This module defines a hierarchy of exceptions for different error scenarios,
making error handling more explicit and maintainable.
"""


class MultiAgentSystemError(Exception):
    """
    Base exception for all multi-agent system errors.

    All custom exceptions should inherit from this class for consistent
    error handling across the application.
    """

    def __init__(self, message: str, details: dict | None = None) -> None:
        """
        Initialize exception with message and optional details.

        Args:
            message: Human-readable error message
            details: Additional context about the error
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}


# TODO: Implement specific exception classes for different error scenarios
# Requirements:
# 1. Create exception hierarchy for different error types
# 2. Include error codes for API responses
# 3. Add detailed error context
# 4. Support error serialization for API responses

# Example Implementation:

# Database Exceptions
class DatabaseError(MultiAgentSystemError):
    """Base exception for database-related errors."""
    pass


class RecordNotFoundError(DatabaseError):
    """Raised when a database record is not found."""
    pass


class RecordAlreadyExistsError(DatabaseError):
    """Raised when trying to create a duplicate record."""
    pass


# Agent Exceptions
class AgentError(MultiAgentSystemError):
    """Base exception for agent-related errors."""
    pass


class AgentTimeoutError(AgentError):
    """Raised when an agent operation times out."""
    pass


class AgentCommunicationError(AgentError):
    """Raised when agents fail to communicate properly."""
    pass


class ToolExecutionError(AgentError):
    """Raised when an agent tool fails to execute."""
    pass


# Business Logic Exceptions
class BusinessLogicError(MultiAgentSystemError):
    """Base exception for business logic errors."""
    pass


class InsufficientInventoryError(BusinessLogicError):
    """Raised when inventory is insufficient for an order."""
    pass


class InvalidQuoteError(BusinessLogicError):
    """Raised when a quote is invalid or expired."""
    pass


class OrderFulfillmentError(BusinessLogicError):
    """Raised when an order cannot be fulfilled."""
    pass


# API Exceptions
class APIError(MultiAgentSystemError):
    """Base exception for API-related errors."""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: dict | None = None
    ) -> None:
        """
        Initialize API exception.

        Args:
            message: Error message
            status_code: HTTP status code
            details: Additional error details
        """
        super().__init__(message, details)
        self.status_code = status_code


class ValidationError(APIError):
    """Raised when request validation fails."""
    
    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message, status_code=422, details=details)


class AuthenticationError(APIError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message, status_code=401)


class AuthorizationError(APIError):
    """Raised when authorization fails."""
    
    def __init__(self, message: str = "Access denied") -> None:
        super().__init__(message, status_code=403)


class RateLimitError(APIError):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded") -> None:
        super().__init__(message, status_code=429)


# TODO: Add more specific exceptions as needed
# Examples:
# - InvalidItemError
# - PricingError
# - SupplierError
# - ConfigurationError
# - CacheError


# TODO: Implement error serialization for API responses
# Example:
# def serialize_error(error: MultiAgentSystemError) -> dict:
#     """Serialize exception for API response."""
#     return {
#         "error": error.__class__.__name__,
#         "message": error.message,
#         "details": error.details,
#     }

