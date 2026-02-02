# =============================================================
# Django REST Framework
# =============================================================
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status

# =============================================================
# Local App Services
# =============================================================
from accounts.services.auth import TwoFactorService
from accounts.serializers.auth import (
    Enable2FASerializer,
    Disable2FASerializer,
    Verify2FASerializer
)
from accounts.permissions import Is2FAToken

# =============================================================
# Core Utilities
# =============================================================
from core.utils.responses import api_response

# =============================================================
# Two-Factor Authentication Views
# =============================================================

class Setup2FAView(APIView):
    """
    Generate TOTP secret and provide URI/QR code for authenticator app setup.

    Key Points:
    - Accessible only by authenticated users.
    - Calls `TwoFactorService.setup_2fa` to generate a new TOTP secret.
    - Returns TOTP secret and QR code URI in the response.
    - Does not enable 2FA yet; enables user to scan QR in their app first.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Handles GET request to generate TOTP setup information.
        """
        result = TwoFactorService.setup_2fa(request.user)

        # API Response
        return api_response(
            message="TOTP setup generated successfully.",
            data=result,
            status_code=status.HTTP_200_OK
        )


class Enable2FAView(GenericAPIView):
    """
    Enable 2FA for user after verifying TOTP token.

    Key Points:
    - Requires authentication.
    - Validates submitted TOTP token via `Enable2FASerializer`.
    - Calls `TwoFactorService.enable_2fa` to enable 2FA on user's account.
    - Returns success message once 2FA is enabled.
    """
    serializer_class = Enable2FASerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        TwoFactorService.enable_2fa(
            user=request.user,
            token=serializer.validated_data["token"]
        )

        # API Response
        return api_response(
            message="2FA enabled successfully.",
            status_code=status.HTTP_200_OK
        )


class Disable2FAView(GenericAPIView):
    """
    Disable 2FA for user after verifying TOTP token.

    Key Points:
    - Requires authentication.
    - Validates submitted TOTP token via `Disable2FASerializer`.
    - Calls `TwoFactorService.disable_2fa` to disable 2FA on user's account.
    - Clears TOTP secret to prevent reuse.
    - Returns success message once 2FA is disabled.
    """
    serializer_class = Disable2FASerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        TwoFactorService.disable_2fa(
            user=request.user,
            token=serializer.validated_data["token"]
        )

        # API Response
        return api_response(
            message="2FA disabled successfully.",
            status_code=status.HTTP_200_OK
        )


class Verify2FAView(GenericAPIView):
    """
    Verify OTP using temporary 2FA token and issue real JWT tokens.

    Key Points:
    - Requires `Is2FAToken` permission to ensure only temporary 2FA token holders access.
    - Validates submitted OTP via `Verify2FASerializer`.
    - Calls `TwoFactorService.verify_2fa_and_issue_tokens` to verify OTP and generate JWTs.
    - Returns `access` and `refresh` tokens upon successful verification.
    - Used during login flow when user has 2FA enabled.
    """
    serializer_class = Verify2FASerializer
    permission_classes = [Is2FAToken]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tokens = TwoFactorService.verify_2fa_and_issue_tokens(
            user=request.user,
            token=serializer.validated_data["token"],
        )

        # API Response
        return api_response(
            message="2FA verification successful.",
            data=tokens,
            status_code=status.HTTP_200_OK,
        )
    