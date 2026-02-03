from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from core.exceptions.base import ServiceException

import logging

logger = logging.getLogger(__name__)


def global_exception_handler(exc, context):
    """
    Centralized exception handler for the entire API.
    """
    # ----------------------------
    # Handle custom service exceptions
    # ----------------------------
    if isinstance(exc, ServiceException):
        return Response(
            {
                "success":False,
                "error":{
                    "code": exc.default_code,
                    "message": exc.detail
                },
            },
            status=exc.status_code,
        )
        
    # ----------------------------
    # Let DRF handle known exceptions
    # ----------------------------
    response = exception_handler(exc, context)
    
    if response is not None:
        return Response(
            {
                "success": False,
                "error": {
                    "code": response.status_code,
                    "message": response.data,
                },
            },
            status=response.status_code,
        )
    
    # ----------------------------
    # Catch-all for unhandled exceptions
    # ----------------------------
    request = context.get("request")
    
    logger.critical(
        "Unhandled exception occurred",
        exc_info=True,
        extra={
            "view": context.get("view").__class__.__name__ if context.get("view") else None,
            "path": request.path if request else None,
            "method": request.method if request else None,
        },
    )
    
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
    