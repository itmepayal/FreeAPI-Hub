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

# =============================================================
# Change Role View
# =============================================================
class ChangeRoleView(generics.GenericAPIView):
    serializer_class = ChangeRoleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):

        # Step 1 — Validate incoming request data using serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Step 2 — Extract validated data
        actor = request.user
        user_id = serializer.validated_data["user_id"]
        new_role = serializer.validated_data["role"]

        # Step 3 — Delegate role-change logic to service layer
        result = ChangeRoleService.execute(actor, user_id, new_role)

        # Step 4 — Return standardized API response
        return api_response(
            message=result["message"],
            data={
                "user_id": str(result["user"].id),
                "role": result["user"].role,
            },
            status_code=status.HTTP_200_OK,
        )
