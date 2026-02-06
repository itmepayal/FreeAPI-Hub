# =============================================================
# Django REST Framework
# =============================================================
from rest_framework import generics, status, permissions

# =============================================================
# Local App
# =============================================================
from accounts.serializers.auth import ResendEmailSerializer
from accounts.services.auth import ResendEmailService

# =============================================================
# Core Utilities
# =============================================================
from core.utils.responses import api_response

# =============================================================
# Resend Email View
# =============================================================
class ResendEmailView(generics.GenericAPIView):
    serializer_class = ResendEmailSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):

        # Step 1 — Validate incoming request data using serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Step 2 — Delegate resend logic to service layer
        ResendEmailService.resend_verification_email(
            email=serializer.validated_data["email"],
            request=request,
        )

        # Step 3 — Return standardized API response
        return api_response(
            message="If the account exists, a verification email has been sent.",
            status_code=status.HTTP_200_OK,
        )
