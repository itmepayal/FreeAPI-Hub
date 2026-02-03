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
from accounts.serializers.auth import Enable2FASerializer, Disable2FASerializer, Verify2FASerializer
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
    API endpoint to generate TOTP secret for 2FA setup.

    Responsibilities:
    1. Generate a TOTP secret for the authenticated user.
    2. Provide a QR code/URI for authenticator app setup.
    3. Do NOT enable 2FA yet; user must scan QR in their app first.

    Design Notes:
    - Requires authentication (`IsAuthenticated` permission).
    - Delegates secret generation to `TwoFactorService.setup_2fa`.
    - Returns structured API response with TOTP setup data.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Handle GET request to generate TOTP setup info.

        Steps:
        1. Ensure the request is from an authenticated user.
        2. Call `TwoFactorService.setup_2fa` to generate TOTP secret and QR URI.
        3. Return structured API response with setup information.

        Args:
            request: DRF request object with authenticated user.

        Returns:
            Response: DRF Response containing TOTP secret and QR code URI.

        Raises:
            ServiceException: If TOTP generation fails (propagated via global exception handler).
        
        # 3. Return structured API response        """
        result = TwoFactorService.setup_2fa(request.user)
        return api_response(
            message="TOTP setup generated successfully.",
            data=result,
            status_code=status.HTTP_200_OK
        )


class Enable2FAView(GenericAPIView):
    """
    API endpoint to enable 2FA for a user after verifying TOTP token.

    Responsibilities:
    1. Validate TOTP token provided by the user.
    2. Enable 2FA on the user's account using `TwoFactorService`.
    3. Return a success message once 2FA is enabled.

    Design Notes:
    - Requires authentication.
    - Uses `Enable2FASerializer` for input validation.
    - Delegates business logic to `TwoFactorService.enable_2fa`.
    """
    serializer_class = Enable2FASerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Handle POST request to enable 2FA.

        Steps:
        1. Validate incoming TOTP token using `Enable2FASerializer`.
        2. Call `TwoFactorService.enable_2fa` to enable 2FA on the user account.
        3. Return structured API response confirming success.

        Args:
            request: DRF request object with authenticated user and TOTP token.

        Returns:
            Response: DRF Response with success message.

        Raises:
            ValidationError: If serializer validation fails.
            ServiceException: If enabling 2FA fails (propagated from service layer).
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        TwoFactorService.enable_2fa(
            user=request.user,
            token=serializer.validated_data["token"]
        )

        # Return structured API response
        return api_response(
            message="2FA enabled successfully.",
            status_code=status.HTTP_200_OK
        )


class Disable2FAView(GenericAPIView):
    """
    API endpoint to disable 2FA for a user after verifying TOTP token.

    Responsibilities:
    1. Validate TOTP token provided by the user.
    2. Disable 2FA on the user's account and clear TOTP secret.
    3. Return a success message once 2FA is disabled.

    Design Notes:
    - Requires authentication.
    - Uses `Disable2FASerializer` for input validation.
    - Delegates business logic to `TwoFactorService.disable_2fa`.
    """
    serializer_class = Disable2FASerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Handle POST request to disable 2FA.

        Steps:
        1. Validate incoming TOTP token using `Disable2FASerializer`.
        2. Call `TwoFactorService.disable_2fa` to disable 2FA and clear TOTP secret.
        3. Return structured API response confirming success.

        Args:
            request: DRF request object with authenticated user and TOTP token.

        Returns:
            Response: DRF Response with success message.

        Raises:
            ValidationError: If serializer validation fails.
            ServiceException: If disabling 2FA fails (propagated from service layer).
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        TwoFactorService.disable_2fa(
            user=request.user,
            token=serializer.validated_data["token"]
        )

        # Return structured API response
        return api_response(
            message="2FA disabled successfully.",
            status_code=status.HTTP_200_OK
        )


class Verify2FAView(GenericAPIView):
    """
    API endpoint to verify a temporary 2FA token (OTP) and issue real JWT tokens.

    Responsibilities:
    1. Validate OTP submitted by the user during login or sensitive operation.
    2. Verify the OTP and generate `access` and `refresh` tokens.
    3. Return structured API response containing JWT tokens.

    Design Notes:
    - Requires `Is2FAToken` permission to ensure only temporary 2FA token holders can access.
    - Uses `Verify2FASerializer` for input validation.
    - Delegates verification and token issuance to `TwoFactorService.verify_2fa_and_issue_tokens`.
    """
    serializer_class = Verify2FASerializer
    permission_classes = [Is2FAToken]

    def post(self, request, *args, **kwargs):
        """
        Handle POST request to verify 2FA OTP and issue JWT tokens.

        Steps:
        1. Validate incoming OTP using `Verify2FASerializer`.
        2. Call `TwoFactorService.verify_2fa_and_issue_tokens` to verify OTP and issue JWTs.
        3. Return structured API response with `access` and `refresh` tokens.

        Args:
            request: DRF request object with temporary 2FA token and OTP.

        Returns:
            Response: DRF Response with access and refresh JWT tokens.

        Raises:
            ValidationError: If serializer validation fails.
            AuthenticationFailedException: If OTP verification fails (propagated from service layer).
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tokens = TwoFactorService.verify_2fa_and_issue_tokens(
            user=request.user,
            token=serializer.validated_data["token"],
        )

        # Return structured API response
        return api_response(
            message="2FA verification successful.",
            data=tokens,
            status_code=status.HTTP_200_OK,
        )
