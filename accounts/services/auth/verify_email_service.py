# =============================================================
# Django
# =============================================================
from django.utils import timezone
from django.db import transaction

# =============================================================
# Local Models
# =============================================================
from accounts.models import UserSecurity
from accounts.models.user_security import hash_token

# =============================================================
# Core Exceptions
# =============================================================
from core.exceptions import (
    InvalidTokenException,
    OperationNotAllowedException,
)

# =============================================================
# Base Service
# =============================================================
from accounts.services import BaseService

# =============================================================
# VerifyEmail Service
# =============================================================
class VerifyEmailService(BaseService):

    @classmethod
    def verify_email(cls, token: str) -> UserSecurity:

        # Step 1 — Hash incoming token
        hashed_token = hash_token(token)

        # Step 2 — Find matching record
        security = (
            UserSecurity.objects
            .select_related("user")
            .filter(
                email_verification_token=hashed_token,
                email_verification_expiry__gt=timezone.now(),
            )
            .first()
        )

        # Step 3 — Validate token exists
        if not security:
            cls.logger().warning("Invalid or expired verification token")
            raise InvalidTokenException("Invalid or expired verification token.")

        user = security.user

        # Step 4 — Already verified check
        if user.is_verified:
            raise OperationNotAllowedException("Email already verified.")

        # Step 5 — Atomic update
        with transaction.atomic():
            user.is_verified = True
            user.save(update_fields=["is_verified"])

            security.clear_email_verification_token()

        # Step 6 — Logging
        cls.logger().info(
            "Email verified successfully",
            extra={
                "user_id": user.id,
                "email": user.email,
            },
        )

        return security
