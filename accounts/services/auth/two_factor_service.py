# =============================================================
# Django
# =============================================================
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken

# =============================================================
# Core Utilities & Exceptions
# =============================================================
from core.logging.logger import get_logger
from core.exception.base import (
    ValidationException,
    AuthenticationFailedException,
)

# =============================================================
# Logger
# =============================================================
logger = get_logger(__name__)

# =============================================================
# Two-Factor Authentication Service
# =============================================================
class TwoFactorService:
    """
    Handles Two-Factor Authentication (TOTP) setup, enable, disable, and verification.
    """

    @staticmethod
    def setup_2fa(user) -> dict:
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

        logger.info("2FA setup initiated", extra={"user_id": user.id})

        return {
            "totp_secret": secret,
            "totp_uri": uri,
        }

    @staticmethod
    def enable_2fa(user, token: str) -> dict:
        """
        Enable 2FA after validating TOTP token.
        """
        security = user.security

        if not security.verify_totp(token):
            logger.warning("Invalid OTP during 2FA enable", extra={"user_id": user.id})
            raise AuthenticationFailedException("Invalid OTP.")

        with transaction.atomic():
            security.is_2fa_enabled = True
            security.save(update_fields=["is_2fa_enabled"])

        logger.info("2FA enabled successfully", extra={"user_id": user.id})

        return {
            "success": True,
            "message": "2FA enabled successfully.",
        }

    @staticmethod
    def disable_2fa(user, token: str) -> dict:
        """
        Disable 2FA after validating TOTP token.
        """
        security = user.security

        if not security.verify_totp(token):
            logger.warning("Invalid OTP during 2FA disable", extra={"user_id": user.id})
            raise AuthenticationFailedException("Invalid OTP.")

        with transaction.atomic():
            security.is_2fa_enabled = False
            security.totp_secret = None
            security.save(update_fields=["is_2fa_enabled", "totp_secret"])

        logger.info("2FA disabled successfully", extra={"user_id": user.id})

        return {
            "success": True,
            "message": "2FA disabled successfully.",
        }

    @staticmethod
    def verify_2fa_and_issue_tokens(user, token: str) -> dict:
        """
        Verify TOTP token and issue JWT tokens.
        """
        security = user.security

        if not security.verify_totp(token):
            logger.warning("Invalid OTP during 2FA login", extra={"user_id": user.id})
            raise AuthenticationFailedException("Invalid OTP.")

        refresh = RefreshToken.for_user(user)

        logger.info("2FA verification successful", extra={"user_id": user.id})

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
