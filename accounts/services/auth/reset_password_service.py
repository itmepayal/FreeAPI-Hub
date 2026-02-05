# =============================================================
# Django
# =============================================================
from django.db import transaction
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

# =============================================================
# Local App Models
# =============================================================
from accounts.models import UserSecurity
from accounts.models.user_security import hash_token

# =============================================================
# Core Exceptions
# =============================================================
from core.exceptions import (
    ValidationException,
    InvalidTokenException,
    InternalServerException,
)

# =============================================================
# Base Service
# =============================================================
from accounts.services import BaseService

# =============================================================
# Reset Password Service
# =============================================================
class ResetPasswordService(BaseService):
    
    @classmethod
    def reset_password(cls, token: str, new_password: str):
        try:
            
            # Step 1 — (Validate & Hash) token using shared helper
            if not token:
                raise InvalidTokenException("Invalid or expired reset token.")
            token_hash = hash_token(token)

            # Step 2 — Start atomic transaction + row lock
            with transaction.atomic():

                security = (
                    UserSecurity.objects
                    .select_for_update()
                    .select_related("user")
                    .filter(forgot_password_token=token_hash)
                    .first()
                )

                # Step 3 — Validate token via model helper
                if not security or not security.verify_forgot_password_token(token):
                    cls.logger().warning(
                        "Invalid or expired reset token attempted"
                    )
                    raise InvalidTokenException(
                        "Invalid or expired reset token."
                    )

                user = security.user

                # Step 4 — Check user is active
                if not user.is_active:
                    raise InvalidTokenException(
                        "Invalid or expired reset token."
                    )

                # Step 5 — Validate password strength
                try:
                    validate_password(new_password, user=user)
                except DjangoValidationError as exc:
                    cls.logger().warning(
                        "Password validation failed during reset",
                        extra={"user_id": user.id},
                    )
                    raise ValidationException(exc.messages)

                # Step 6 — Update password
                user.set_password(new_password)
                user.save(update_fields=["password"])

                # Step 7 — Invalidate token using model helper
                security.clear_forgot_password_token()

        except (InvalidTokenException, ValidationException):
            raise

        except Exception as exc:
            cls.logger().error(
                "Password reset failed",
                exc_info=True,
                extra={"token_hash": token_hash},
            )
            raise InternalServerException(
                "Failed to reset password. Please try again later."
            ) from exc

        # Step 8 — Log success
        cls.logger().info(
            "Password reset successfully",
            extra={"user_id": user.id, "email": user.email},
        )

        return user
