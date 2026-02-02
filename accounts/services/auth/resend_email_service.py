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
# Core Utilities & Exceptions
# =============================================================
from core.logging.logger import get_logger
from core.email.services import send_email
from core.exception.base import ForbiddenException, InternalServerException

# =============================================================
# Logger
# =============================================================
logger = get_logger(__name__)

# =============================================================
# Resend Email Service
# =============================================================
class ResendEmailService:
    """
    Handles resending of email verification tokens.
    """

    @staticmethod
    def resend_verification_email(user, security):
        """
        Generate new email verification token and send email.

        Raises:
            ForbiddenException: If user account is inactive
            InternalServerException: If token generation or email sending fails
        """

        # ----------------------
        # Business rule check
        # ----------------------
        if not getattr(user, "is_active", True):
            logger.warning(
                "Inactive user attempted email resend",
                extra={"user_id": user.id, "email": user.email},
            )
            raise ForbiddenException("User account is inactive.")

        try:
            # ----------------------
            # Atomic token update
            # ----------------------
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

            # ----------------------
            # Send verification email
            # ----------------------
            verify_link = f"{settings.FRONTEND_URL}/verify-email/{raw_token}"

            send_email(
                to_email=user.email,
                template_id=settings.SENDGRID_EMAIL_VERIFICATION_TEMPLATE_ID,
                dynamic_data={
                    "username": user.username,
                    "verify_link": verify_link,
                },
            )

            logger.info(
                "Verification email resent successfully",
                extra={"user_id": user.id, "email": user.email},
            )

        except Exception as e:
            logger.error(
                "Failed to resend verification email",
                exc_info=True,
                extra={"user_id": user.id, "email": user.email},
            )
            raise InternalServerException(
                "Failed to resend verification email. Please try again later."
            ) from e
