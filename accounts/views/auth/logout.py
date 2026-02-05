# =============================================================
# Django REST Framework
# =============================================================
from rest_framework import generics, permissions, status

# =============================================================
# Local App Serializers & Services
# =============================================================
from accounts.serializers.auth.auth import RefreshTokenSerializer
from accounts.swagger.auth import logout_schema
from accounts.services.auth import LogoutService

# =============================================================
# Core Utilities
# =============================================================
from core.utils.responses import api_response


# =============================================================
# Logout View
# =============================================================
@logout_schema
class LogoutView(generics.GenericAPIView):
    serializer_class = RefreshTokenSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):

        # Step 1 — Validate incoming request data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data["refresh_token"]

        # Step 2 — Delegate logout operation to service layer
        LogoutService.logout_user(
            user=request.user,
            refresh_token=refresh_token,
        )

        # Step 3 — Return standardized API success response
        return api_response(
            message="Logout successful.",
            status_code=status.HTTP_200_OK,
        )
