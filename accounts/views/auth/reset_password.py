# =============================================================
# Django REST Framework
# =============================================================
from rest_framework import generics, status, permissions

# =============================================================
# Local App
# =============================================================
from accounts.serializers.auth.password import ResetPasswordSerializer
from accounts.services.auth import ResetPasswordService

# =============================================================
# Core Utilities
# =============================================================
from core.utils.responses import api_response


# =============================================================
# Reset Password View
# =============================================================
class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):

        # Step 1 — Validate incoming request data using serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Step 2 — Extract validated token and new password
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]

        # Step 3 — Delegate password reset logic to service layer
        ResetPasswordService.reset_password(
            token=token,
            new_password=new_password,
        )

        # Step 4 — Return standardized API response
        return api_response(
            message="Password reset successfully. You can now log in.",
            status_code=status.HTTP_200_OK,
        )
