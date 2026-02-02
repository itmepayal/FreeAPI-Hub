# =============================================================
# Django REST Framework
# =============================================================
from rest_framework import generics, status, permissions

# =============================================================
# Local App
# =============================================================
from accounts.serializers.auth.password import ResetPasswordSerializer
from accounts.swagger.auth import register_schema
from accounts.services.auth import ResetPasswordService

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
# Reset Password View
# =============================================================
@register_schema
class ResetPasswordView(generics.GenericAPIView):
    """
    Endpoint to reset a user's password using a valid reset token.

    Key Points:
    - Accessible by anyone (`AllowAny`) because user may not be logged in.
    - Accepts a password reset token and new password.
    - Delegates actual password reset logic to `ResetPasswordService`.
    - Handles invalid token and unexpected errors gracefully.
    - Returns a generic success message to prevent token abuse information leaks.
    """
    serializer_class = ResetPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests to reset a user's password.

        Steps:
        1. Validate input using `ResetPasswordSerializer`.
        2. Extract `token` and `new_password` from validated data.
        3. Call `ResetPasswordService.reset_password` to perform the reset.
        4. Handle specific (`ValueError`) and generic exceptions.
        5. Return a standardized API response.
        """
        # Validate incoming data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]

        try:
            # Delegate password reset logic to service layer
            user = ResetPasswordService.reset_password(token, new_password)

        except ValueError as ve:
            # Handle known errors such as invalid or expired token
            return api_response(
                message=str(ve),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            # Log unexpected errors for debugging while returning generic message
            logger.error(f"Password reset error: {str(e)}", exc_info=True)
            return api_response(
                message="Unable to reset password. Try again later.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # API Response
        return api_response(
            message="Password reset successfully. You can now log in.",
            status_code=status.HTTP_200_OK
        )
