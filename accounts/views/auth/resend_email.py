# =============================================================
# Django REST Framework
# =============================================================
from rest_framework import generics, status, permissions

# =============================================================
# Local App
# =============================================================
from accounts.serializers.auth.auth import ResendEmailSerializer
from accounts.services.auth import ResendEmailService

# =============================================================
# Core Utilities
# =============================================================
from core.utils.responses import api_response
from core.logging.logger import get_logger

# =============================================================
# Logger
# =============================================================
logger = get_logger(__name__)

# =============================================================
# Resend Email View
# =============================================================
class ResendEmailView(generics.GenericAPIView):
    """
    Endpoint to resend email verification tokens to users.
    
    Key Points:
    - Accessible by anyone (`AllowAny`) because user may not be verified yet.
    - Accepts user identification via serializer (e.g., email or user object).
    - Delegates the actual sending logic to `ResendEmailService`.
    - Handles errors gracefully without exposing sensitive information.
    - Returns a generic success message to prevent information leaks.
    """
    serializer_class = ResendEmailSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests to resend email verification.

        Steps:
        1. Validate input using `ResendEmailSerializer`.
        2. Extract `user` and associated `security` instance from validated data.
        3. Call the `ResendEmailService` to send the verification email.
        4. Handle specific (`ValueError`) and generic exceptions.
        5. Return a standardized API response.
        """
        # Validate incoming data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Extract validated objects
        user = serializer.validated_data["user"]
        security = serializer.validated_data["security"]

        try:
            # Delegate email sending to service
            ResendEmailService.resend_verification_email(user, security)

        except ValueError as ve:
            # Handle known errors (e.g., user inactive or already verified)
            return api_response(
                message=str(ve),
                status_code=status.HTTP_403_FORBIDDEN,
            )
        except Exception:
            # Handle unexpected errors gracefully
            return api_response(
                message="Failed to send verification email. Try again later.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # API Response
        return api_response(
            message="Verification email resent successfully.",
            status_code=status.HTTP_200_OK,
        )
