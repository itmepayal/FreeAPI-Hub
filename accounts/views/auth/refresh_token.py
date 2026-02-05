# =============================================================
# Django REST Framework
# =============================================================
from rest_framework import generics, permissions, status

# =============================================================
# Local App
# =============================================================
from accounts.serializers.auth.auth import RefreshTokenSerializer
from accounts.services.auth import RefreshTokenService

# =============================================================
# Core Utilities
# =============================================================
from core.utils.responses import api_response

# =============================================================
# Refresh Access Token View
# =============================================================
class RefreshTokenView(generics.GenericAPIView):
    serializer_class = RefreshTokenSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):

        # Step 1 — Validate incoming request data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data["refresh_token"]

        # Step 2 — Generate new access token via service
        new_access_token = RefreshTokenService.refresh_access_token(
            refresh_token
        )

        # Step 3 — Return standardized API response
        return api_response(
            message="Access token refreshed successfully.",
            data={
                "access": new_access_token,
            },
            status_code=status.HTTP_200_OK,
        )
