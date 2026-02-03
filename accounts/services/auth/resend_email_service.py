# =============================================================
# Python Standard Library
# =============================================================
import secrets
import hashlib
from datetime import timedelta

# =============================================================
# Django Utilities
# =============================================================
from django.utils import timezone
from django.db import transaction
from django.conf import settings

# =============================================================
# Core Exceptions
# =============================================================
from core.exceptions.base import (
    PermissionDeniedException,
    InternalServerException,
)

# =============================================================
# Email Service
# =============================================================
from core.email.services import send_email

# =============================================================
# Base Service
# =============================================================
from accounts.services.base import BaseService

# =============================================================
# Resend Email Service
# =============================================================
class ResendEmailService(BaseService):
    """
    Service layer to handle resending email verification tokens.

    Responsibilities:
    1. Generate a new secure email verification token.
    2. Update the token and expiry in the UserSecurity model.
    3. Send verification email to the user.
    4. Log all relevant actions for traceability.

    Design Notes:
    - Uses transaction.atomic() to ensure DB consistency.
    - Any unexpected errors are wrapped in InternalServerException.
    - Inactive users are not allowed to resend verification emails.
    """

    @classmethod
    def resend_verification_email(cls, user, security):
        """
        Generate a new email verification token and send it to the user.

        Steps:
        1. Check business rules (e.g., user must be active).
        2. Generate secure token and save hash & expiry.
        3. Send verification email.
        4. Log actions and handle exceptions.

        Args:
            user (User): User instance to resend verification email to.
            security (UserSecurity): Related security record for the user.

        Raises:
            PermissionDeniedException: If the user is inactive.
            InternalServerException: If token update or email sending fails.
        """
        # Business rule check
        if not getattr(user, "is_active", True):
            cls.logger().warning(
                "Inactive user attempted email verification resend",
                extra={"user_id": user.id, "email": user.email},
            )
            raise PermissionDeniedException("User account is inactive.")

        try:
            # Atomic token generation & update
            with transaction.atomic():
                raw_token = secrets.token_urlsafe(32)
                hashed_token = hashlib.sha256(raw_token.encode()).hexdigest()
                expiry = timezone.now() + timedelta(
                    hours=settings.EMAIL_VERIFICATION_EXPIRY_HOURS
                )

                security.email_verification_token = hashed_token
                security.email_verification_expiry = expiry
                security.save(
                    update_fields=[
                        "email_verification_token",
                        "email_verification_expiry",
                    ]
                )

            # Send verification email
            verify_link = f"{settings.FRONTEND_URL}/verify-email/{raw_token}"

            send_email(
                to_email=user.email,
                template_id=settings.SENDGRID_EMAIL_VERIFICATION_TEMPLATE_ID,
                dynamic_data={
                    "username": user.username,
                    "verify_link": verify_link,
                },
            )

            cls.logger().info(
                "Verification email resent successfully",
                extra={"user_id": user.id, "email": user.email},
            )

        except Exception as exc:
            cls.logger().error(
                "Failed to resend verification email",
                exc_info=True,
                extra={"user_id": user.id, "email": user.email},
            )
            raise InternalServerException(
                "Failed to resend verification email. Please try again later."
            ) from exc
