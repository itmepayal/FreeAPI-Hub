# =============================================================
# Django
# =============================================================
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken

# =============================================================
# Core Exceptions
# =============================================================
from core.exceptions.base import (
    ValidationException,
    AuthenticationFailedException,
)

# =============================================================
# Base Service
# =============================================================
from accounts.services.base import BaseService

# =============================================================
# Two-Factor Authentication Service
# =============================================================
class TwoFactorService(BaseService):
    """
    Handles Two-Factor Authentication (TOTP) setup, enable, disable, and verification.
    """

    @classmethod
    def setup_2fa(cls, user) -> dict:
        """
        Generate a TOTP secret and URI for QR code scanning.
        """
        security = user.security

        if security.is_2fa_enabled:
            raise ValidationException("2FA is already enabled.")

        with transaction.atomic():
            secret = security.generate_totp_secret()
            security.save(update_fields=["totp_secret"])

        uri = security.get_totp_uri()

        cls.logger().info(
            "2FA setup initiated",
            extra={"user_id": user.id},
        )

        return {
            "totp_secret": secret,
            "totp_uri": uri,
        }

    @classmethod
    def enable_2fa(cls, user, token: str) -> dict:
        """
        Enable 2FA after validating TOTP token.
        """
        security = user.security

        if security.is_2fa_enabled:
            raise ValidationException("2FA is already enabled.")

        if not security.verify_totp(token):
            cls.logger().warning(
                "Invalid OTP during 2FA enable",
                extra={"user_id": user.id},
            )
            raise AuthenticationFailedException("Invalid OTP.")

        with transaction.atomic():
            security.is_2fa_enabled = True
            security.save(update_fields=["is_2fa_enabled"])

        cls.logger().info(
            "2FA enabled successfully",
            extra={"user_id": user.id},
        )

        return {
            "success": True,
            "message": "2FA enabled successfully.",
        }

    @classmethod
    def disable_2fa(cls, user, token: str) -> dict:
        """
        Disable 2FA after validating TOTP token.
        """
        security = user.security

        if not security.is_2fa_enabled:
            raise ValidationException("2FA is not enabled.")

        if not security.verify_totp(token):
            cls.logger().warning(
                "Invalid OTP during 2FA disable",
                extra={"user_id": user.id},
            )
            raise AuthenticationFailedException("Invalid OTP.")

        with transaction.atomic():
            security.is_2fa_enabled = False
            security.totp_secret = None
            security.save(update_fields=["is_2fa_enabled", "totp_secret"])

        cls.logger().info(
            "2FA disabled successfully",
            extra={"user_id": user.id},
        )

        return {
            "success": True,
            "message": "2FA disabled successfully.",
        }

    @classmethod
    def verify_2fa_and_issue_tokens(cls, user, token: str) -> dict:
        """
        Verify TOTP token and issue JWT tokens.
        """
        security = user.security

        if not security.is_2fa_enabled:
            raise ValidationException("2FA is not enabled for this account.")

        if not security.verify_totp(token):
            cls.logger().warning(
                "Invalid OTP during 2FA login",
                extra={"user_id": user.id},
            )
            raise AuthenticationFailedException("Invalid OTP.")

        refresh = RefreshToken.for_user(user)

        cls.logger().info(
            "2FA verification successful",
            extra={"user_id": user.id},
        )

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
