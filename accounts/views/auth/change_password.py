# =============================================================
# Django REST Framework
# =============================================================
from rest_framework import generics, status, permissions

# =============================================================
# Local App
# =============================================================
from accounts.serializers.auth.password import ChangePasswordSerializer
from accounts.services.auth import ChangePasswordService

# =============================================================
# Core Utilities
# =============================================================
from core.utils.responses import api_response

# =============================================================
# Change Password View
# =============================================================
class ChangePasswordView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):

        # Step 1 — Validate incoming request data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_password = serializer.validated_data["new_password"]

        # Step 2 — Delegate password change to service layer
        ChangePasswordService.change_password(
            user=request.user,
            new_password=new_password,
        )

        # Step 3 — Return standardized API response
        return api_response(
            message="Password changed successfully.",
            status_code=status.HTTP_200_OK,
        )
