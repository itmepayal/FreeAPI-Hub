# =============================================================
# Django REST Framework
# =============================================================
from rest_framework import generics, status, permissions

# =============================================================
# Local App Serializers & Services
# =============================================================
from accounts.serializers.auth.auth import ForgotPasswordSerializer
from accounts.services.auth import ForgotPasswordService

# =============================================================
# Core Utilities
# =============================================================
from core.utils.responses import api_response

# =============================================================
# Forgot Password View
# =============================================================
class ForgotPasswordView(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):

        # Step 1 — Validate request data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        # Step 2 — Call service with request object
        ForgotPasswordService.send_reset_email(
            email=email,
            request=request,
        )

        # Step 3 — Return standardized API response
        return api_response(
            message="If the email exists, a reset link has been sent.",
            status_code=status.HTTP_200_OK,
        )