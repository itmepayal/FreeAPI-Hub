# =============================================================
# Django REST Framework
# =============================================================
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

# =============================================================
# Local App Services & Serializers
# =============================================================
from accounts.services.auth import TwoFactorService
from accounts.serializers.auth import (
    Enable2FASerializer,
    Disable2FASerializer,
    Verify2FASerializer,
)
from accounts.permissions import Is2FAToken

# =============================================================
# Core Utilities
# =============================================================
from core.utils.responses import api_response


# =============================================================
# Setup 2FA View
# =============================================================
class Setup2FAView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):

        # Step 1 — Call service layer to generate TOTP secret & URI
        result = TwoFactorService.setup_2fa(request.user)

        # Step 2 — Return standardized API response
        return api_response(
            message="TOTP setup generated successfully.",
            data=result,
            status_code=status.HTTP_200_OK,
        )


# =============================================================
# Enable 2FA View
# =============================================================
class Enable2FAView(GenericAPIView):
    serializer_class = Enable2FASerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        # Step 1 — Validate incoming request data using serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Step 2 — Delegate enable logic to service layer
        TwoFactorService.enable_2fa(
            user=request.user,
            token=serializer.validated_data["token"],
        )

        # Step 3 — Return standardized API response
        return api_response(
            message="2FA enabled successfully.",
            status_code=status.HTTP_200_OK,
        )


# =============================================================
# Disable 2FA View
# =============================================================
class Disable2FAView(GenericAPIView):
    serializer_class = Disable2FASerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        # Step 1 — Validate incoming request data using serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Step 2 — Delegate disable logic to service layer
        TwoFactorService.disable_2fa(
            user=request.user,
            token=serializer.validated_data["token"],
        )

        # Step 3 — Return standardized API response
        return api_response(
            message="2FA disabled successfully.",
            status_code=status.HTTP_200_OK,
        )


# =============================================================
# Verify 2FA View
# =============================================================
class Verify2FAView(GenericAPIView):
    serializer_class = Verify2FASerializer
    permission_classes = [Is2FAToken]

    def post(self, request, *args, **kwargs):

        # Step 1 — Validate incoming request data using serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Step 2 — Delegate verification & token issue to service layer
        tokens = TwoFactorService.verify_2fa_and_issue_tokens(
            user=request.user,
            token=serializer.validated_data["token"],
        )

        # Step 3 — Return standardized API response
        return api_response(
            message="2FA verification successful.",
            data=tokens,
            status_code=status.HTTP_200_OK,
        )
