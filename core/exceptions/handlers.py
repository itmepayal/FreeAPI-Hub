# =============================================================
# Global Exception Handler
# =============================================================
# Provides a centralized mechanism to handle exceptions across the API.
# Supports:
#   - Custom service exceptions
#   - DRF validation exceptions
#   - Unhandled/internal exceptions
# =============================================================

# =============================================================
# Standard Library
# =============================================================
import logging

# =============================================================
# Third-Party
# =============================================================
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ErrorDetail

# =============================================================
# Local App
# =============================================================
from core.exceptions.base import ServiceException

# =============================================================
# Logger
# =============================================================
logger = logging.getLogger(__name__)

# =============================================================
# Helper: Extract Readable Error Message
# =============================================================
def extract_error_message(data):
    """
    Always return a single readable string for the frontend.
    Handles dicts, lists, tuples, and DRF ErrorDetail objects.
    """
    if isinstance(data, dict):
        # {"detail": "..."}
        if "detail" in data:
            return str(data["detail"])

        # {"password": ["error message"]}
        for _, errors in data.items():
            if isinstance(errors, (list, tuple)) and errors:
                return str(errors[0])
            return str(errors)

    if isinstance(data, (list, tuple)) and data:
        return str(data[0])
    
    if isinstance(data, ErrorDetail):
        return str(data)

    return str(data)

# =============================================================
# Global Exception Handler Function
# =============================================================
def global_exception_handler(exc, context):
    # Step 1 — Handle Custom Service Exceptions
    if isinstance(exc, ServiceException):
        return Response(
            {
                "success": False,
                "error": {
                    "code": exc.default_code,
                    "message": str(exc.detail),
                },
            },
            status=exc.status_code,
        )

    # Step 2 — Handle DRF Validation/Framework Exceptions
    response = exception_handler(exc, context)

    if response is not None:
        message = extract_error_message(response.data)

        return Response(
            {
                "success": False,
                "error": {
                    "code": "validation_error",
                    "message": message,
                },
            },
            status=response.status_code,
        )

    # Step 3 — Handle Unhandled / Internal Exceptions
    logger.critical("Unhandled exception occurred", exc_info=True)

    return Response(
        {
            "success": False,
            "error": {
                "code": "internal_server_error",
                "message": "Something went wrong. Please try again later.",
            },
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
