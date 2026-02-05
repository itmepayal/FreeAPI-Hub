# =============================================================
# Django Utilities
# =============================================================
from django.db import transaction
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

# =============================================================
# Core Exceptions
# =============================================================
from core.exceptions import (
    InactiveUserException,
    ValidationException,
    InternalServerException,
)

# =============================================================
# Base Service
# =============================================================
from accounts.services import BaseService

# =============================================================
# Change Password Service
# =============================================================
class ChangePasswordService(BaseService):

    @classmethod
    def change_password(cls, user, new_password: str) -> None:
        try:
            # Step 1 — Ensure user account is active
            if not user.is_active:
                cls.logger().warning(
                    "Inactive user attempted password change",
                    extra={"user_id": user.id},
                )
                raise InactiveUserException("User account is inactive.")

            # Step 2 — Validate password strength
            try:
                validate_password(new_password, user=user)
            except DjangoValidationError as exc:
                cls.logger().warning(
                    "Password validation failed during change",
                    extra={"user_id": user.id},
                )
                raise ValidationException(exc.messages)

            # Step 3 — Atomically update password
            with transaction.atomic():
                user.set_password(new_password)
                user.save(update_fields=["password"])

            # Step 4 — Log success
            cls.logger().info(
                "Password changed successfully",
                extra={"user_id": user.id},
            )

        except (InactiveUserException, ValidationException):
            # Step 5 — Re-raise known business exceptions
            raise

        except Exception as exc:
            # Step 6 — Log unexpected failure
            cls.logger().error(
                "Password change failed",
                exc_info=True,
                extra={"user_id": user.id},
            )
            raise InternalServerException(
                "Failed to update password. Please try again later."
            ) from exc
