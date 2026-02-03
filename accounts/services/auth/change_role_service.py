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
from core.exceptions.base import (
    InactiveUserException,
    PermissionDeniedException,
    ResourceNotFoundException,
    OperationNotAllowedException,
    InternalServerException,
    ServiceException,
)

# =============================================================
# Base Service
# =============================================================
from accounts.services.base import BaseService

# =============================================================
# ChangeRole Service
# =============================================================
class ChangeRoleService(BaseService):
    """
    Service layer to handle changing a user's role within the system.

    Responsibilities:
    1. Validate actor permissions (e.g., prevent self-role change).
    2. Fetch target user from the database.
    3. Check user status and constraints (inactive, SUPERADMIN protection).
    4. Update user's role in a safe manner.
    5. Log all relevant actions for traceability.

    Design Notes:
    - Prevents privilege escalation or self-modification of roles.
    - Preserves known service exceptions; wraps unexpected errors in InternalServerException.
    """

    @classmethod
    def execute(cls, actor: User, user_id, new_role: str) -> dict:
        """
        Perform role change operation for a target user.

        Steps:
        1. Prevent actor from changing their own role.
        2. Retrieve target user; raise error if not found.
        3. Validate target user's status and role constraints.
        4. Update role and persist changes.
        5. Log success; handle unexpected exceptions.

        Args:
            actor (User): User performing the role change.
            user_id: ID of the target user whose role is to be changed.
            new_role (str): New role to assign to the target user.

        Returns:
            dict: Contains updated user object, success flag, and message.

        Raises:
            PermissionDeniedException: If actor tries to change their own role.
            ResourceNotFoundException: If target user does not exist.
            InactiveUserException: If target user is inactive.
            OperationNotAllowedException: If modifying a SUPERADMIN is attempted.
            InternalServerException: For unexpected errors during role update.
        """
        # 1. Prevent self-role change
        if str(actor.id) == str(user_id):
            raise PermissionDeniedException(
                "SuperAdmin cannot change their own role."
            )

        try:
            # 2. Fetch target user
            try:
                user = User.objects.get(id=user_id)
            except ObjectDoesNotExist:
                raise ResourceNotFoundException(
                    f"User with ID {user_id} not found."
                )

            # 3. Check user status
            if not user.is_active:
                raise InactiveUserException(
                    f"User {user.email} is inactive."
                )

            # 4. Prevent modifying another SUPERADMIN
            if user.role == "SUPERADMIN":
                raise OperationNotAllowedException(
                    "Cannot change role of another SuperAdmin."
                )

            # 5. Update role
            user.role = new_role
            user.save(update_fields=["role"])

            cls.logger().info(
                "User role changed successfully",
                extra={
                    "actor_id": actor.id,
                    "target_user_id": user.id,
                    "new_role": new_role,
                },
            )

            return {
                "user": user,
                "message": f"Role of {user.email} changed successfully.",
                "success": True,
            }

        except ServiceException:
            # Preserve known service errors
            raise

        except Exception as exc:
            cls.logger().error(
                "Failed to change user role",
                exc_info=True,
                extra={
                    "actor_id": actor.id,
                    "target_user_id": user_id,
                    "new_role": new_role,
                },
            )
            raise InternalServerException(
                "Failed to update role. Please try again later."
            ) from exc
