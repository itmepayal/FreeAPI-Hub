from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from core.exceptions.base import ServiceException
import logging

logger = logging.getLogger(__name__)

def extract_error_message(data):
    """
    Always return a single readable string for frontend.
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


def global_exception_handler(exc, context):

    # ----------------------------
    # Custom service exceptions
    # ----------------------------
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

    # ----------------------------
    # DRF-handled exceptions
    # ----------------------------
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

    # ----------------------------
    # Unhandled exceptions
    # ----------------------------
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
