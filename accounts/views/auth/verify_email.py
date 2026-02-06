# =============================================================
# Django REST Framework
# =============================================================
from rest_framework import generics, status, permissions

# =============================================================
# Local App
# =============================================================
from accounts.serializers.auth import VerifyEmailSerializer
from accounts.services.auth import VerifyEmailService

# =============================================================
# Core Utilities
# =============================================================
from core.utils.responses import api_response

# =============================================================
# VerifyEmail View
# =============================================================
class VerifyEmailView(generics.GenericAPIView):
    serializer_class = VerifyEmailSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        # Step 1 — Validate incoming request payload
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Step 2 — Extract validated token
        token = serializer.validated_data["token"]

        # Step 3 — Delegate verification to service layer
        security = VerifyEmailService.verify_email(token)
        user = security.user

        # Step 4 — Build structured success response
        return api_response(
            message="Email verified successfully.",
            data={
                "user": {
                    "id": user.id,
                    "email": user.email,
                }
            },
            status_code=status.HTTP_200_OK,
        )
