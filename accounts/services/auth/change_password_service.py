# =============================================================
# Django Utilities
# =============================================================
from django.db import transaction
from django.contrib.auth.password_validation import validate_password 

# =============================================================
# Core Utilities
# =============================================================
from core.exception.base import (
    InactiveUserException,
    ValidationException,
    InternalServerException
)
from core.logging.logger import get_logger

# =============================================================
# Logger
# =============================================================
logger = get_logger(__name__)

# =============================================================
# Change Password Service
# =============================================================
class ChangePasswordService:
    """
    Handles changing user passwords.
    """
    @staticmethod
    def change_password(user, new_password: str):
        """
        Change the password of a given user.

        Args:
            user: Authenticated User instance
            new_password (str): New password to set

        Raises:
            ValueError: If the user is inactive
            ValidationError: If password does not meet complexity rules
            Exception: If password update fails
        """
        # ----------------------
        # Check if user is active
        # ----------------------
        if not user.is_active:
            logger.warning(f"Inactive user {user.id} attempted password change.")
            raise InactiveUserException("User account is inactive.")
        
        # ----------------------
        # Validate password strength
        # ----------------------
        try:
            validate_password(new_password, user=user)
        except Exception as e:
            logger.warning(f"Password validation failed for user {user.id}: {str(e)}")
            raise ValidationException(str(e))

        try:
            # ----------------------
            # Atomic password update
            # ----------------------
            with transaction.atomic():
                user.set_password(new_password)
                user.save(update_fields=["password"])

            logger.info(f"User {user.id} changed password successfully.")

        except Exception as e:
            logger.error(f"Change password failed for user {user.id}: {str(e)}", exc_info=True)
            raise InternalServerException("Failed to update password. Please try again later.")