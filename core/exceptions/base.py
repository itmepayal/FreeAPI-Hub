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
    """

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "A service error occurred."
    default_code = "service_error"

    def __init__(self, detail=None, code=None, status_code=None):
        if code is not None:
            self.default_code = code
        super().__init__(detail or self.default_detail)

        if self.status_code >= 500:
            logger.error(
                f"{self.__class__.__name__}: {self.detail}",
                exc_info=True,
            )
            
# =============================================================
# Authentication & Authorization Exceptions
# =============================================================
class InvalidTokenException(ServiceException):
    default_detail = "Token is invalid or expired."
    default_code = "invalid_token"
    status_code = status.HTTP_401_UNAUTHORIZED

class AuthenticationRequiredException(ServiceException):
    default_detail = "Authentication is required to access this resource."
    default_code = "authentication_required"
    status_code = status.HTTP_401_UNAUTHORIZED
    
class AuthenticationFailedException(ServiceException):
    default_detail = "Invalid credentials."
    default_code = "authentication_failed"
    status_code = status.HTTP_401_UNAUTHORIZED

class PermissionDeniedException(ServiceException):
    default_detail = "You do not have permission to perform this action."
    default_code = "permission_denied"
    status_code = status.HTTP_403_FORBIDDEN


class InactiveUserException(ServiceException):
    default_detail = "User account is inactive."
    default_code = "inactive_user"
    status_code = status.HTTP_403_FORBIDDEN


# =============================================================
# Resource Errors
# =============================================================
class ResourceNotFoundException(ServiceException):
    default_detail = "Resource not found."
    default_code = "resource_not_found"
    status_code = status.HTTP_404_NOT_FOUND


class ResourceAlreadyExistsException(ServiceException):
    default_detail = "Resource already exists."
    default_code = "resource_already_exists"
    status_code = status.HTTP_409_CONFLICT


class DuplicateRequestException(ServiceException):
    default_detail = "Duplicate request detected."
    default_code = "duplicate_request"
    status_code = status.HTTP_409_CONFLICT


class OperationNotAllowedException(ServiceException):
    default_detail = "This operation is not allowed in the current state."
    default_code = "operation_not_allowed"
    status_code = status.HTTP_409_CONFLICT
    
class InternalServerException(ServiceException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Internal server error."
    default_code = "internal_server_error"


# =============================================================
# Validation Errors
# =============================================================
class ValidationException(ServiceException):
    default_detail = "Invalid input data."
    default_code = "validation_error"
    status_code = status.HTTP_400_BAD_REQUEST


class MissingRequiredFieldException(ServiceException):
    default_detail = "A required field is missing."
    default_code = "missing_required_field"
    status_code = status.HTTP_400_BAD_REQUEST


class InvalidFormatException(ServiceException):
    default_detail = "Invalid data format."
    default_code = "invalid_format"
    status_code = status.HTTP_400_BAD_REQUEST


# =============================================================
# Rate Limiting & Quotas
# =============================================================
class RateLimitExceededException(ServiceException):
    default_detail = "Rate limit exceeded. Try again later."
    default_code = "rate_limit_exceeded"
    status_code = status.HTTP_429_TOO_MANY_REQUESTS


# =============================================================
# Server & Dependency Errors
# =============================================================
class ExternalServiceException(ServiceException):
    default_detail = "An external service error occurred."
    default_code = "external_service_error"
    status_code = status.HTTP_502_BAD_GATEWAY

class ServiceUnavailableException(ServiceException):
    default_detail = "Service is temporarily unavailable."
    default_code = "service_unavailable"
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE

class DatabaseException(ServiceException):
    default_detail = "A database error occurred."
    default_code = "database_error"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

# =============================================================
# HTTP Method & Media Errors
# =============================================================
class MethodNotAllowedException(ServiceException):
    default_detail = "HTTP method not allowed."
    default_code = "method_not_allowed"
    status_code = status.HTTP_405_METHOD_NOT_ALLOWED

class UnsupportedMediaTypeException(ServiceException):
    default_detail = "Unsupported media type."
    default_code = "unsupported_media_type"
    status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
