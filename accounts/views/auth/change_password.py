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

# =============================================================
# Change Password View
# =============================================================
class ChangePasswordView(generics.GenericAPIView):
    """
    Endpoint for authenticated users to change their password.

    Responsibilities:
    1. Accept new password input via serializer.
    2. Delegate business logic to ChangePasswordService.
    3. Return structured API response.

    Security Notes:
    - Only authenticated users can access this endpoint.
    - Service layer enforces password validation and active status.
    - Errors are handled by DRF/global exception handler.
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # 1. Validate input
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 2. Delegate password change to service
        ChangePasswordService.change_password(
            user=request.user,
            new_password=serializer.validated_data["new_password"],
        )

        # 3. Return structured API response
        return api_response(
            message="Password changed successfully.",
            status_code=status.HTTP_200_OK,
        )

