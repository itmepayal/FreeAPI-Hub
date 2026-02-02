# =============================================================
# Base Exception for all service layer errors
# =============================================================
from rest_framework.exceptions import APIException
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

# =============================================================
# Base Exception
# =============================================================
class ServiceException(APIException):
    """
    Base exception class for all service-layer errors.

    This class provides:
    - Standardized status codes for DRF responses
    - Default messages for consistent frontend display
    - Optional logging for server errors (status >= 500)
    
    Args:
        detail (str, optional): Custom error message. Defaults to `default_detail`.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "A service error occurred."
    default_code = "service_error"

    def __init__(self, detail=None):
        # Use custom detail if provided, else default
        if detail:
            self.detail = detail
        else:
            self.detail = self.default_detail

        # Optional: log critical server errors
        if self.status_code >= 500:
            logger.error(f"{self.__class__.__name__}: {self.detail}")


# =============================================================
# Authentication & Authorization Exceptions
# =============================================================
class InvalidTokenException(ServiceException):
    """Raised when a provided authentication token is invalid or expired."""
    default_detail = "Token is invalid or expired."
    status_code = status.HTTP_401_UNAUTHORIZED

class AuthenticationRequiredException(ServiceException):
    """Raised when a user must be authenticated to access a resource."""
    default_detail = "Authentication is required to access this resource."
    status_code = status.HTTP_401_UNAUTHORIZED

class UnauthorizedActionException(ServiceException):
    """Raised when a user attempts an action they are not allowed to perform."""
    default_detail = "You are not authorized to perform this action."
    status_code = status.HTTP_403_FORBIDDEN

class PermissionDeniedException(ServiceException):
    """Raised when a user lacks specific permissions for an action."""
    default_detail = "You do not have permission to perform this action."
    status_code = status.HTTP_403_FORBIDDEN

class InactiveUserException(ServiceException):
    """Raised when an inactive user attempts an operation."""
    default_detail = "User account is inactive."
    status_code = status.HTTP_403_FORBIDDEN


# =============================================================
# Resource Errors
# =============================================================
class ResourceNotFoundException(ServiceException):
    """Raised when a requested resource does not exist."""
    default_detail = "Resource not found."
    status_code = status.HTTP_404_NOT_FOUND

class ResourceAlreadyExistsException(ServiceException):
    """Raised when attempting to create a resource that already exists."""
    default_detail = "Resource already exists."
    status_code = status.HTTP_409_CONFLICT

class DuplicateRequestException(ServiceException):
    """Raised when the same request is submitted multiple times."""
    default_detail = "Duplicate request detected."
    status_code = status.HTTP_409_CONFLICT

class OperationNotAllowedException(ServiceException):
    """Raised when an operation is not allowed in the current state."""
    default_detail = "This operation is not allowed in the current state."
    status_code = status.HTTP_409_CONFLICT


# =============================================================
# Validation Errors
# =============================================================
class ValidationException(ServiceException):
    """Raised for general invalid input data."""
    default_detail = "Invalid input data."
    status_code = status.HTTP_400_BAD_REQUEST

class MissingRequiredFieldException(ServiceException):
    """Raised when a required field is missing from input."""
    default_detail = "A required field is missing."
    status_code = status.HTTP_400_BAD_REQUEST

class InvalidFormatException(ServiceException):
    """Raised when input data is in an invalid format."""
    default_detail = "Invalid data format."
    status_code = status.HTTP_400_BAD_REQUEST


# =============================================================
# Rate Limiting & Quotas
# =============================================================
class RateLimitExceededException(ServiceException):
    """Raised when a user exceeds allowed rate limits."""
    default_detail = "Rate limit exceeded. Try again later."
    status_code = status.HTTP_429_TOO_MANY_REQUESTS


# =============================================================
# Server & Dependency Errors
# =============================================================
class ExternalServiceException(ServiceException):
    """Raised when an external service or dependency fails."""
    default_detail = "An external service error occurred."
    status_code = status.HTTP_502_BAD_GATEWAY

class ServiceUnavailableException(ServiceException):
    """Raised when the service is temporarily unavailable."""
    default_detail = "Service is temporarily unavailable."
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE

class DatabaseException(ServiceException):
    """Raised when a database operation fails."""
    default_detail = "A database error occurred."
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

class InternalServerException(ServiceException):
    """Raised for generic internal server errors."""
    default_detail = "An internal server error occurred."
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


# =============================================================
# HTTP Method & Media Errors
# =============================================================
class MethodNotAllowedException(ServiceException):
    """Raised when a request uses an unsupported HTTP method."""
    default_detail = "HTTP method not allowed."
    status_code = status.HTTP_405_METHOD_NOT_ALLOWED

class UnsupportedMediaTypeException(ServiceException):
    """Raised when a request contains an unsupported media type."""
    default_detail = "Unsupported media type."
    status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
