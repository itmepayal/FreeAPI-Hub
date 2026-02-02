# =============================================================
# Django REST Framework
# =============================================================
from rest_framework import generics, status, permissions

# =============================================================
# Local App Serializers
# =============================================================
from accounts.serializers.auth import ChangePasswordSerializer

# =============================================================
# Local App Services
# =============================================================
from accounts.services.auth import ChangePasswordService

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
# Change Password View
# =============================================================
class ChangePasswordView(generics.GenericAPIView):
    """
    Allows authenticated users to change their password securely.

    Security Notes:
    - Only authenticated users can access this endpoint.
    - The service checks if the user is active before updating password.
    - All exceptions are logged internally; clients get generic messages.
    - Uses a dedicated service layer to separate business logic.
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Validate input
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_password = serializer.validated_data["new_password"]
        user = request.user

        try:
            # Delegate password change to service
            ChangePasswordService.change_password(user, new_password)

        except ValueError as ve:
            # User inactive or similar business validation failed
            return api_response(
                message=str(ve),
                status_code=status.HTTP_403_FORBIDDEN,
                code="user_inactive"
            )
        except Exception as e:
            # Internal errors (DB, hashing, etc.)
            logger.error(f"Password change failed for user {user.id}: {str(e)}", exc_info=True)
            return api_response(
                message="Unable to change password. Try again later.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                code="password_change_failed"
            )

        # API Response
        return api_response(
            message="Password changed successfully.",
            status_code=status.HTTP_200_OK,
            code="password_change_success"
        )
