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
from django.core.exceptions import ValidationError as DjangoValidationError

# =============================================================
# Local App Models
# =============================================================
from accounts.models import UserSecurity

# =============================================================
# Core Exceptions
# =============================================================
from core.exceptions.base import (
    ValidationException,
    InvalidTokenException,
    InternalServerException,
)

# =============================================================
# Base Service
# =============================================================
from accounts.services.base import BaseService

# =============================================================
# Reset Password Service
# =============================================================
class ResetPasswordService(BaseService):
    """
    Service layer to handle password resets using a valid token.

    Responsibilities:
    1. Validate the password reset token.
    2. Validate the new password strength.
    3. Atomically update the user's password.
    4. Invalidate the reset token after successful update.
    5. Log all actions for audit and traceability.

    Design Notes:
    - Uses transaction.atomic() for DB consistency.
    - Uses Django's validate_password to enforce password policies.
    - Raises clear exceptions for invalid token, weak password, or internal errors.
    """

    @classmethod
    def reset_password(cls, token: str, new_password: str):
        """
        Reset a user's password using the provided reset token.

        Steps:
        1. Hash the incoming token for secure comparison.
        2. Fetch UserSecurity and validate token expiry.
        3. Validate new password against Django's password rules.
        4. Atomically set new password and invalidate the token.
        5. Log successful reset.

        Args:
            token (str): Raw password reset token from the user.
            new_password (str): New password provided by the user.

        Returns:
            User: Updated user instance.

        Raises:
            InvalidTokenException: If token is invalid or expired.
            ValidationException: If new password fails validation.
            InternalServerException: For unexpected failures during update.
        """
        # 1. Hash token
        hashed_token = hashlib.sha256(token.encode()).hexdigest()

        # 2. Validate token
        security = (
            UserSecurity.objects
            .select_related("user")
            .filter(
                forgot_password_token=hashed_token,
                forgot_password_expiry__gt=timezone.now(),
            )
            .first()
        )

        if not security:
            cls.logger().warning("Invalid or expired reset token attempted")
            raise InvalidTokenException("Invalid or expired reset token.")

        user = security.user

        # 3. Validate password strength
        try:
            validate_password(new_password, user=user)
        except DjangoValidationError as exc:
            cls.logger().warning(
                "Password validation failed during reset",
                extra={"user_id": user.id},
            )
            raise ValidationException(exc.messages)

        # 4. Atomic update
        try:
            with transaction.atomic():
                # Update password
                user.set_password(new_password)
                user.save(update_fields=["password"])

                # Invalidate reset token
                security.forgot_password_token = None
                security.forgot_password_expiry = None
                security.save(update_fields=["forgot_password_token", "forgot_password_expiry"])

        except Exception as exc:
            cls.logger().error(
                "Password reset failed",
                exc_info=True,
                extra={"user_id": user.id, "email": user.email},
            )
            raise InternalServerException(
                "Failed to reset password. Please try again later."
            ) from exc

        # 5. Log success
        cls.logger().info(
            "Password reset successfully",
            extra={"user_id": user.id, "email": user.email},
        )

        return user
