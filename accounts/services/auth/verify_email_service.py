# =============================================================
# Python Standard Library
# =============================================================
import hashlib

# =============================================================
# Django
# =============================================================
from django.utils import timezone
from django.db import transaction

# =============================================================
# Local Models
# =============================================================
from accounts.models import UserSecurity

# =============================================================
# Core Exceptions
# =============================================================
from core.exceptions.base import (
    InvalidTokenException,
    OperationNotAllowedException,
)

# =============================================================
# Base Service
# =============================================================
from accounts.services.base import BaseService


# =============================================================
# VerifyEmail Service
# =============================================================
class VerifyEmailService(BaseService):
    """
    Service layer for handling user email verification.

    Responsibilities:
    1. Validate email verification token.
    2. Mark user as verified in the database.
    3. Clear token and expiry fields after successful verification.
    4. Log all relevant actions for traceability.

    Design Notes:
    - Token is stored hashed (SHA-256) for security.
    - Uses transaction.atomic() to ensure DB consistency.
    - Raises meaningful custom exceptions for invalid, expired, or already verified tokens.
    """

    @classmethod
    def verify_email(cls, token: str) -> UserSecurity:
        """
        Verify the user's email using the provided token.

        Steps:
        1. Hash the incoming token for secure lookup.
        2. Retrieve the UserSecurity record matching the hashed token and ensure it is not expired.
        3. Check if user is already verified; if yes, raise OperationNotAllowedException.
        4. Atomically mark user as verified and clear the token and expiry fields.
        5. Log success and return the updated UserSecurity object.

        Args:
            token (str): Email verification token sent to the user's email.

        Returns:
            UserSecurity: The UserSecurity record for the verified user.

        Raises:
            InvalidTokenException: If the token is invalid or expired.
            OperationNotAllowedException: If the user is already verified.
        """
        # 1. Hash token
        hashed_token = hashlib.sha256(token.encode()).hexdigest()

        # 2. Fetch & validate token
        security = (
            UserSecurity.objects
            .select_related("user")
            .filter(
                email_verification_token=hashed_token,
                email_verification_expiry__gt=timezone.now(),
            )
            .first()
        )

        if not security:
            cls.logger().warning("Invalid or expired email verification token")
            raise InvalidTokenException("Invalid or expired verification token.")

        user = security.user

        # 3. Check if already verified
        if user.is_verified:
            raise OperationNotAllowedException("Email already verified.")

        # 4. Atomic state mutation
        with transaction.atomic():
            user.is_verified = True
            user.save(update_fields=["is_verified"])

            security.email_verification_token = None
            security.email_verification_expiry = None
            security.save(update_fields=["email_verification_token", "email_verification_expiry"])

        # 5. Logging
        cls.logger().info(
            "Email verified successfully",
            extra={"user_id": user.id, "email": user.email},
        )

        return security
