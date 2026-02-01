# Django Utilities
from django.db import transaction

# Django REST Framework
from rest_framework import generics, status, permissions

# Local App Serializers
from accounts.serializers.auth import ChangePasswordSerializer

# Core Utilities
from core.logging.logger import get_logger
from core.utils.responses import api_response

# =============================================================
# Logger
# =============================================================
logger = get_logger(__name__)

# ----------------------
# Change Password View
# ----------------------
class ChangePasswordView(generics.GenericAPIView):
    """
    Allows authenticated users to change their password.
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Fetch User
        user = request.user

        # Ensure user is active
        if not getattr(user, "is_active", True):
            return api_response(
                message="User account is inactive.",
                status_code=status.HTTP_403_FORBIDDEN,
                code="user_inactive"
            )

        # Validate & Set Password
        new_password = serializer.validated_data["new_password"]

        try:
            with transaction.atomic():
                user.set_password(new_password)
                user.save(update_fields=["password"])
        except Exception as e:
            logger.error(f"Change password failed for user {user.id}: {str(e)}", exc_info=True)
            return api_response(
                message="Unable to change password. Try again later.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                code="password_change_failed"
            )

        # Log success (audit)
        logger.info(f"User {user.id} changed password successfully.")

        # ----------------------
        # Return API response
        # ----------------------
        return api_response(
            message="Password changed successfully.",
            status_code=status.HTTP_200_OK,
        )
