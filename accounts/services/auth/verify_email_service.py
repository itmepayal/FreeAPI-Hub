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
# Core Utilities
# =============================================================
from core.logging.logger import get_logger
from core.exception.base import (
    InvalidTokenException,
    OperationNotAllowedException,
    DatabaseException,
)

# =============================================================
# Logger
# =============================================================
logger = get_logger(__name__)

# =============================================================
# Verify Email Service
# =============================================================
class VerifyEmailService:
    """
    Handles email verification logic for a user.
    """

    @staticmethod
    def verify_email(token: str) -> UserSecurity:
        """
        Verify email based on the token.

        Args:
            token (str): Raw email verification token

        Returns:
            UserSecurity: Verified UserSecurity instance
        """
        hashed_token = hashlib.sha256(token.encode()).hexdigest()

        try:
            with transaction.atomic():
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
                    logger.warning("Invalid or expired email verification token")
                    raise InvalidTokenException(
                        "Invalid or expired verification token."
                    )

                user = security.user

                if user.is_verified:
                    logger.info(
                        "Email verification attempted on already verified account",
                        extra={"user_id": user.id},
                    )
                    raise OperationNotAllowedException(
                        "Email is already verified."
                    )

                # Mark user as verified
                user.is_verified = True
                user.save(update_fields=["is_verified"])

                # Clear verification token
                security.email_verification_token = None
                security.email_verification_expiry = None
                security.save(
                    update_fields=[
                        "email_verification_token",
                        "email_verification_expiry",
                    ]
                )

                logger.info(
                    "Email verified successfully",
                    extra={"user_id": user.id, "email": user.email},
                )

                return security

        except (InvalidTokenException, OperationNotAllowedException):
            # Let known service exceptions bubble up
            raise

        except Exception as e:
            logger.error(
                "Email verification failed due to internal error",
                exc_info=True,
            )
            raise DatabaseException(
                "Failed to verify email. Please try again later."
            ) from e
