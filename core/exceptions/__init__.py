# =============================================================
# Service Exceptions — Public Package Exports
# =============================================================

from .base import (
    ServiceException,

    # Auth
    InvalidTokenException,
    AuthenticationRequiredException,
    AuthenticationFailedException,
    PermissionDeniedException,
    InactiveUserException,

    # Resource
    ResourceNotFoundException,
    ResourceAlreadyExistsException,
    DuplicateRequestException,
    OperationNotAllowedException,
    InternalServerException,

    # Validation
    ValidationException,
    MissingRequiredFieldException,
    InvalidFormatException,

    # Rate Limit
    RateLimitExceededException,

    # Server / Dependency
    ExternalServiceException,
    ServiceUnavailableException,
    DatabaseException,

    # HTTP
    MethodNotAllowedException,
    UnsupportedMediaTypeException,
)

__all__ = [
    # Base
    "ServiceException",

    # Auth
    "InvalidTokenException",
    "AuthenticationRequiredException",
    "AuthenticationFailedException",
    "PermissionDeniedException",
    "InactiveUserException",

    # Resource
    "ResourceNotFoundException",
    "ResourceAlreadyExistsException",
    "DuplicateRequestException",
    "OperationNotAllowedException",
    "InternalServerException",

    # Validation
    "ValidationException",
    "MissingRequiredFieldException",
    "InvalidFormatException",

    # Rate Limit
    "RateLimitExceededException",

    # Server
    "ExternalServiceException",
    "ServiceUnavailableException",
    "DatabaseException",

    # HTTP
    "MethodNotAllowedException",
    "UnsupportedMediaTypeException",
]
