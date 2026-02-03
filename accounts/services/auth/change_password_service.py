# =============================================================
# Django Utilities
# =============================================================
from django.db import transaction
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

# =============================================================
# Core Utilities & Exceptions
# =============================================================
from core.exceptions.base import (
    InactiveUserException,
    ValidationException,
    InternalServerException,
    ServiceException,
)

# =============================================================
# Base Service
# =============================================================
from accounts.services.base import BaseService

# =============================================================
# Change Password Service
# =============================================================
class ChangePasswordService(BaseService):
    """
    Service layer for changing user passwords.

    Responsibilities:
    1. Validate that the user is active.
    2. Validate new password strength according to Django rules.
    3. Atomically update the password in the database.
    4. Log all relevant events for traceability.

    Design Notes:
    - Uses transaction.atomic() for DB consistency.
    - Raises clear exceptions for inactive users, weak passwords, or internal errors.
    """

    @classmethod
    def change_password(cls, user, new_password: str) -> None:
        """
        Change the password for a given user.

        Args:
            user: Authenticated User instance
            new_password (str): New password to set

        Raises:
            InactiveUserException: If user account is inactive
            ValidationException: If new password fails complexity validation
            InternalServerException: For unexpected failures during update
        """
        # 1. Ensure user is active
        if not user.is_active:
            cls.logger().warning(
                "Inactive user attempted password change",
                extra={"user_id": user.id},
            )
            raise InactiveUserException("User account is inactive.")

        # 2. Validate password strength
        try:
            validate_password(new_password, user=user)
        except DjangoValidationError as exc:
            cls.logger().warning(
                "Password validation failed",
                extra={"user_id": user.id},
            )
            raise ValidationException(exc.messages[0]) from exc

        # 3. Atomically update password
        try:
            with transaction.atomic():
                user.set_password(new_password)
                user.save(update_fields=["password"])

            cls.logger().info(
                "User password changed successfully",
                extra={"user_id": user.id},
            )

        except Exception as exc:
            cls.logger().error(
                "Unexpected error during password change",
                exc_info=True,
                extra={"user_id": user.id},
            )
            raise InternalServerException(
                "Failed to update password. Please try again later."
            ) from exc
