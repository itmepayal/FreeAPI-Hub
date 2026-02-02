# =============================================================
# Django REST Framework
# =============================================================
from rest_framework import generics, status, permissions

# =============================================================
# Local App Serializer & Services
# =============================================================
from accounts.serializers.auth.auth import RefreshTokenSerializer
from accounts.swagger.auth import refresh_token_schema
from accounts.services.auth import RefreshTokenService

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
# Refresh Token View
# =============================================================
@refresh_token_schema
class RefreshTokenView(generics.GenericAPIView):
    """
    API endpoint to generate a new access token using a valid refresh token.

    Responsibilities:
    - Validate the incoming refresh token.
    - Use the RefreshTokenService to generate a new access token.
    - Return the new access token or an error response if invalid.
    """
    serializer_class = RefreshTokenSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        """
        POST method to refresh access token.

        Steps:
        1. Deserialize and validate the refresh token.
        2. Call service to refresh access token.
        3. Handle known errors like invalid or expired token.
        4. Return the new access token in a structured API response.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Extract validated refresh token
        refresh_token = serializer.validated_data["refresh_token"]

        try:
            # Generate new access token using service
            new_access_token = RefreshTokenService.refresh_access_token(refresh_token)
            logger.info("Access token refreshed successfully.")

        except ValueError as ve:
            # Invalid or expired refresh token
            logger.warning(f"Failed to refresh access token: {str(ve)}")
            return api_response(
                message=str(ve),
                status_code=status.HTTP_401_UNAUTHORIZED
            )

        # API Response
        return api_response(
            message="Access token refreshed successfully.",
            data={"access": new_access_token},
            status_code=status.HTTP_200_OK
        )
