"""
Custom exceptions for FinRisk application.
"""


class FinRiskException(Exception):
    """Base exception for FinRisk application."""
    
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class ValidationError(FinRiskException):
    """Raised when input validation fails."""
    pass


class ModelNotFoundError(FinRiskException):
    """Raised when a required ML model is not found."""
    pass


class DataProcessingError(FinRiskException):
    """Raised when data processing fails."""
    pass


class ServiceUnavailableError(FinRiskException):
    """Raised when an external service is unavailable."""
    pass


class AuthenticationError(FinRiskException):
    """Raised when authentication fails."""
    pass


class AuthorizationError(FinRiskException):
    """Raised when authorization fails."""
    pass
