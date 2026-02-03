# =============================================================
# Django REST Framework
# =============================================================
from rest_framework import generics, status, permissions

# =============================================================
# Local App Serializer & Services
# =============================================================
from accounts.serializers.auth import ChangeRoleSerializer
from accounts.services.auth import ChangeRoleService

# =============================================================
# Core Utilities
# =============================================================
from core.utils.responses import api_response
from core.logging.logger import get_logger

# =============================================================
# ChangeRole View
# =============================================================
class ChangeRoleView(generics.GenericAPIView):
    """
    API endpoint to change a user's role.

    Responsibilities:
    1. Accept requests with target user ID and new role.
    2. Validate input using ChangeRoleSerializer.
    3. Delegate all role-change logic to ChangeRoleService.
    4. Return structured API responses for success or failure.

    Design Notes:
    - Only accessible to authenticated users (SuperAdmin/Admin).
    - Service layer handles all business rules (e.g., self-role protection, SUPERADMIN protection).
    - Returns structured success response with updated role info.
    """
    serializer_class = ChangeRoleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to change a user's role.

        Steps:
        1. Validate request data via serializer.
        2. Extract actor (request user), target user ID, and new role.
        3. Delegate role-change logic to ChangeRoleService.
        4. Return structured success response with updated role info.

        Args:
            request: DRF request object.

        Returns:
            Response: DRF Response with success flag, message, and updated user role.

        Raises:
            ValidationError: If serializer validation fails (handled automatically by DRF).
            InternalServerException: If service layer encounters unexpected errors.
        """
        # 1. Validate input
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 2. Extract data
        actor = request.user
        user_id = serializer.validated_data["user_id"]
        new_role = serializer.validated_data["role"]

        # 3. Execute role change via service layer
        result = ChangeRoleService.execute(actor, user_id, new_role)

        # 4. Return structured API response
        return api_response(
            message=result["message"],
            data={
                "user_id": str(result["user"].id),
                "role": result["user"].role,
            },
            status_code=status.HTTP_200_OK
        )
