# =============================================================
# Django
# =============================================================
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

# =============================================================
# Local App Models
# =============================================================
from accounts.models import User

# =============================================================
# Core Exceptions
# =============================================================
from core.constants import ROLE_SUPERADMIN
from core.exceptions import (
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
from accounts.services import BaseService


# =============================================================
# Change Role Service
# =============================================================
class ChangeRoleService(BaseService):

    @classmethod
    def execute(cls, actor: User, user_id, new_role: str) -> dict:
        try:
            # Step 1 — Prevent self role modification
            if str(actor.id) == str(user_id):
                raise PermissionDeniedException(
                    "You cannot change your own role."
                )

            # Step 2 — Execute role change atomically
            with transaction.atomic():

                # Step 3 — Fetch target user
                try:
                    user = User.objects.get(id=user_id)
                except ObjectDoesNotExist:
                    raise ResourceNotFoundException(
                        f"User with ID {user_id} not found."
                    )

                # Step 4 — Validate user status
                if not user.is_active:
                    raise InactiveUserException(
                        f"User {user.email} is inactive."
                    )

                # Step 5 — Prevent modifying another SUPERADMIN
                if user.role == ROLE_SUPERADMIN:
                    raise OperationNotAllowedException(
                        "Cannot change role of another SuperAdmin."
                    )

                # Step 6 — Update role
                user.role = new_role
                user.save(update_fields=["role"])

                # Step 7 — Log success
                cls.logger().info(
                    "User role updated successfully",
                    extra={
                        "actor_id": actor.id,
                        "target_user_id": user.id,
                        "new_role": new_role,
                    },
                )

            # Step 8 — Return standardized response
            return {
                "success": True,
                "message": f"Role of {user.email} changed successfully.",
                "user": user,
            }

        except ServiceException:
            # Step 9 — Re-raise known business exceptions
            raise

        except Exception as exc:
            # Step 10 — Log unexpected failures
            cls.logger().error(
                "Unexpected error while changing user role",
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
