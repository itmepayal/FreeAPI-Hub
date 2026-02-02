# =============================================================
# Python Standard Library
# =============================================================
import hashlib

# =============================================================
# Django
# =============================================================
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.password_validation import validate_password

# =============================================================
# Local App Models
# =============================================================
from accounts.models import UserSecurity

# =============================================================
# Core Utilities & Exceptions
# =============================================================
from core.logging.logger import get_logger
from core.exception.base import (
    ValidationException,
    InvalidTokenException,
    InternalServerException,
)

# =============================================================
# Logger
# =============================================================
logger = get_logger(__name__)

# =============================================================
# Reset Password Service
# =============================================================
class ResetPasswordService:
    """
    Handles resetting user passwords using a valid token.
    """

    @staticmethod
    def reset_password(token: str, new_password: str):
        """
        Reset a user's password using the given reset token.

        Raises:
            InvalidTokenException: If token is invalid or expired
            ValidationException: If password does not meet security rules
            InternalServerException: If password update fails
        """

        # ----------------------
        # Hash incoming token
        # ----------------------
        hashed_token = hashlib.sha256(token.encode()).hexdigest()

        # ----------------------
        # Validate token
        # ----------------------
        security = UserSecurity.objects.select_related("user").filter(
            forgot_password_token=hashed_token,
            forgot_password_expiry__gt=timezone.now(),
        ).first()

        if not security:
            logger.warning("Invalid or expired reset token attempted")
            raise InvalidTokenException("Invalid or expired reset token.")

        user = security.user

        # ----------------------
        # Validate password strength
        # ----------------------
        try:
            validate_password(new_password, user=user)
        except Exception as e:
            logger.warning(
                "Password validation failed during reset",
                extra={"user_id": user.id},
            )
            raise ValidationException(str(e))

        try:
            # ----------------------
            # Atomic password update
            # ----------------------
            with transaction.atomic():
                user.set_password(new_password)
                user.save(update_fields=["password"])

                # Invalidate reset token
                security.forgot_password_token = None
                security.forgot_password_expiry = None
                security.save(
                    update_fields=[
                        "forgot_password_token",
                        "forgot_password_expiry",
                    ]
                )

            logger.info(
                "Password reset successfully",
                extra={"user_id": user.id, "email": user.email},
            )

            return user

        except Exception as e:
            logger.error(
                "Password reset failed",
                exc_info=True,
                extra={"user_id": user.id, "email": user.email},
            )
            raise InternalServerException(
                "Failed to reset password. Please try again later."
            ) from e
