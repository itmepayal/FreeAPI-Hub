# =============================================================
# Django REST Framework
# =============================================================
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

# =============================================================
# Local App Services
# =============================================================
from accounts.services.auth import ChangeRoleService

# =============================================================
# Core Utilities
# =============================================================
from core.utils.responses import api_response
from core.logging.logger import get_logger

# =============================================================
# Logger
# =============================================================
logger = get_logger(__name__)

# =============================================================
# ChangeRole View
# =============================================================
class ChangeRoleView(APIView):
    """
    API endpoint to change a user's role.

    Features:
    - Only accessible to authenticated users (e.g., SuperAdmin/Admin)
    - Validates input (user_id and new_role required)
    - Uses ChangeRoleService to perform business logic
    - Handles errors such as:
        - Actor trying to change their own role
        - Target user not found
        - Attempt to modify another SuperAdmin
    - Returns structured API responses for both success and failure
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Step 1: Extract actor and request data
        actor = request.user
        user_id = request.data.get("user_id")
        new_role = request.data.get("role")

        # Step 2: Validate input
        if not user_id or not new_role:
            logger.warning(f"ChangeRole failed: Missing user_id or role by {actor.email}")
            return Response(
                {"success": False, "message": "user_id and role are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Step 3: Call the service layer for business logic
        try:
            result = ChangeRoleService.execute(actor, user_id, new_role)

        except ValueError as ve:
            # Known business validation errors
            logger.warning(f"ChangeRole failed for actor {actor.email}: {str(ve)}")
            return api_response(
                success=False,
                message=str(ve),
                status_code=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            # Unexpected errors
            logger.error(f"ChangeRole unexpected error by {actor.email}: {str(e)}", exc_info=True)
            return api_response(
                success=False,
                message="Failed to change role. Please try again later.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Step 4: Return success response
        return api_response(
            message=result["message"],
            data={
                "user_id": str(result["user"].id),
                "role": result["user"].role
            },
            status_code=status.HTTP_200_OK
        )
