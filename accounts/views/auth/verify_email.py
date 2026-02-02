# =============================================================
# Django
# =============================================================
from django.db import transaction

# =============================================================
# Django REST Framework
# =============================================================
from rest_framework import generics, status, permissions

# =============================================================
# Local App
# =============================================================
from accounts.models import UserSecurity
from accounts.serializers.auth import VerifyEmailSerializer
from accounts.swagger.auth import verify_email_schema
from accounts.services.auth import VerifyEmailService

# =============================================================
# Core Utilities
# =============================================================
from core.logging.logger import get_logger
from core.utils.responses import api_response

# =============================================================
# Logger
# =============================================================
logger = get_logger(__name__)

# =============================================================
# VerifyEmail View
# =============================================================
@verify_email_schema
class VerifyEmailView(generics.GenericAPIView):
    """
    Endpoint to verify a user's email using a token sent to their email.

    Flow:
    1. Validate incoming token payload
    2. Hash the token to match stored value
    3. Verify token exists and is not expired
    4. Mark user as verified
    5. Clear verification token
    6. Return verified user info

    Design Notes:
    - Atomic transaction ensures DB consistency
    - Detailed logging for observability
    - Returns descriptive API responses for each failure case
    """
    serializer_class = VerifyEmailSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Handle email verification request.
        """
        # Validate request payload
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]

        try:
            # Use service to verify email
            security = VerifyEmailService.verify_email(token)
            user = security.user
            
        except ValueError as ve:
            # Handle known errors from service
            return api_response(
                message=str(ve),
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            logger.error(f"Email verification failed: {str(e)}")
            return api_response(
                message="Verification failed. Please try again.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # API response
        return api_response(
            message="Email verified successfully.",
            data={"user": {"id": user.id, "email": user.email}},
            status_code=status.HTTP_200_OK
        )