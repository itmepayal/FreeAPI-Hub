# =============================================================
# Django
# =============================================================
from django.core.exceptions import ObjectDoesNotExist

# =============================================================
# Local App Models
# =============================================================
from accounts.models import User

# =============================================================
# Core Utilities & Exceptions
# =============================================================
from core.exception.base import (
    InactiveUserException,
    ValidationException,
    UnauthorizedActionException,
    ResourceNotFoundException,
    OperationNotAllowedException
)
from core.logging.logger import get_logger

# =============================================================
# Logger
# =============================================================
logger = get_logger(__name__)

# =============================================================
# ChangeRole Service
# =============================================================
class ChangeRoleService:
    """
    Service to handle changing a user's role within the system.
    """

    @staticmethod
    def execute(actor, user_id, new_role):
        """
        Execute the role change operation.

        Args:
            actor (User): The user performing the role change.
            user_id (str | UUID): The ID of the target user.
            new_role (str): The new role to assign.

        Returns:
            dict: {
                "user": User instance,
                "message": Success message,
                "success": True
            }

        Raises:
            UnauthorizedActionException: If actor tries to change their own role
            InactiveUserException: If the target user is inactive
            ResourceNotFoundException: If target user does not exist
            OperationNotAllowedException: If attempting to modify another SuperAdmin
        """
        # ----------------------
        # Prevent self-role change by SuperAdmin
        # ----------------------
        if str(actor.id) == str(user_id):
            raise UnauthorizedActionException("SuperAdmin cannot change their own role.")

        # ----------------------
        # Fetch the target user safely
        # ----------------------
        try:
            user = User.objects.get(id=user_id)
        except ObjectDoesNotExist:
            raise ResourceNotFoundException(f"User with ID {user_id} not found.")

        # ----------------------
        # Check if user is active
        # ----------------------
        if not user.is_active:
            raise InactiveUserException(f"User {user.email} is inactive.")

        # ----------------------
        # Prevent modifying another SuperAdmin
        # ----------------------
        if user.role == "SUPERADMIN":
            raise OperationNotAllowedException("Cannot change role of another SuperAdmin.")

        # ----------------------
        # Update user's role in the database
        # ----------------------
        try:
            user.role = new_role
            user.save(update_fields=["role"])
            logger.info(f"Role of user {user.email} changed to {new_role} by {actor.email}")
        except Exception as e:
            logger.error(f"Failed to change role for user {user.id}: {str(e)}", exc_info=True)
            raise ValidationException("Failed to update role. Please try again later.")

        # ----------------------
        # Return structured Python dict for the view
        # ----------------------
        return {
            "user": user,
            "message": f"Role of {user.email} changed successfully.",
            "success": True
        }
