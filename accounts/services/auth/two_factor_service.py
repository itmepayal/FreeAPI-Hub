# =============================================================
# Django
# =============================================================
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken

# =============================================================
# Core Exceptions
# =============================================================
from core.exceptions import (
    ValidationException,
    AuthenticationFailedException,
)

# =============================================================
# Base Service
# =============================================================
from accounts.services import BaseService


# =============================================================
# Two-Factor Authentication Service
# =============================================================
class TwoFactorService(BaseService):

    @classmethod
    def setup_2fa(cls, user) -> dict:
        # Step 1 — Fetch user security profile
        security = user.security

        # Step 2 — Prevent re-enabling 2FA if already enabled
        if security.is_2fa_enabled:
            raise ValidationException("2FA is already enabled.")

        # Step 3 — Generate and persist TOTP secret atomically
        with transaction.atomic():
            secret = security.generate_totp_secret()
            security.save(update_fields=["totp_secret"])

        # Step 4 — Build TOTP provisioning URI
        uri = security.get_totp_uri()

        # Step 5 — Log 2FA setup initiation
        cls.logger().info(
            "2FA setup initiated",
            extra={"user_id": user.id},
        )

        # Step 6 — Return secret and URI for QR generation
        return {
            "totp_secret": secret,
            "totp_uri": uri,
        }

    @classmethod
    def enable_2fa(cls, user, token: str) -> dict:
        # Step 1 — Fetch user security profile
        security = user.security

        # Step 2 — Prevent enabling 2FA if already enabled
        if security.is_2fa_enabled:
            raise ValidationException("2FA is already enabled.")

        # Step 3 — Validate provided TOTP token
        if not security.verify_totp(token):
            cls.logger().warning(
                "Invalid OTP during 2FA enable",
                extra={"user_id": user.id},
            )
            raise AuthenticationFailedException("Invalid OTP.")

        # Step 4 — Enable 2FA atomically
        with transaction.atomic():
            security.is_2fa_enabled = True
            security.save(update_fields=["is_2fa_enabled"])

        # Step 5 — Log successful 2FA enablement
        cls.logger().info(
            "2FA enabled successfully",
            extra={"user_id": user.id},
        )

        # Step 6 — Return success response
        return {
            "success": True,
            "message": "2FA enabled successfully.",
        }

    @classmethod
    def disable_2fa(cls, user, token: str) -> dict:
        # Step 1 — Fetch user security profile
        security = user.security

        # Step 2 — Ensure 2FA is currently enabled
        if not security.is_2fa_enabled:
            raise ValidationException("2FA is not enabled.")

        # Step 3 — Validate provided TOTP token
        if not security.verify_totp(token):
            cls.logger().warning(
                "Invalid OTP during 2FA disable",
                extra={"user_id": user.id},
            )
            raise AuthenticationFailedException("Invalid OTP.")

        # Step 4 — Disable 2FA and clear TOTP secret atomically
        with transaction.atomic():
            security.is_2fa_enabled = False
            security.totp_secret = None
            security.save(update_fields=["is_2fa_enabled", "totp_secret"])

        # Step 5 — Log successful 2FA disablement
        cls.logger().info(
            "2FA disabled successfully",
            extra={"user_id": user.id},
        )

        # Step 6 — Return success response
        return {
            "success": True,
            "message": "2FA disabled successfully.",
        }

    @classmethod
    def verify_2fa_and_issue_tokens(cls, user, token: str) -> dict:
        # Step 1 — Fetch user security profile
        security = user.security

        # Step 2 — Ensure 2FA is enabled for the account
        if not security.is_2fa_enabled:
            raise ValidationException("2FA is not enabled for this account.")

        # Step 3 — Validate provided TOTP token
        if not security.verify_totp(token):
            cls.logger().warning(
                "Invalid OTP during 2FA login",
                extra={"user_id": user.id},
            )
            raise AuthenticationFailedException("Invalid OTP.")

        # Step 4 — Issue JWT refresh and access tokens
        refresh = RefreshToken.for_user(user)

        # Step 5 — Log successful 2FA verification
        cls.logger().info(
            "2FA verification successful",
            extra={"user_id": user.id},
        )

        # Step 6 — Return issued tokens
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
