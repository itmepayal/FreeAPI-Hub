# =============================================================
# Django REST Framework
# =============================================================
from rest_framework import generics, status, permissions
from rest_framework_simplejwt.tokens import RefreshToken

# =============================================================
# Local App
# =============================================================
from accounts.serializers.auth.auth import RefreshTokenSerializer
from accounts.swagger.auth import logout_schema
from accounts.services.auth import LogoutService

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
# Logout View
# =============================================================
@logout_schema
class LogoutView(generics.GenericAPIView):
    """
    API endpoint to log out a user by blacklisting their refresh token.

    Responsibilities:
    - Validate the provided refresh token
    - Blacklist the token using LogoutService
    - Return appropriate API response
    """
    serializer_class = RefreshTokenSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        POST method to log out the user.

        Steps:
        1. Deserialize and validate the refresh token.
        2. Blacklist the token using the LogoutService.
        3. Handle known errors (invalid or expired token).
        4. Log unexpected errors and return 500 if needed.
        5. Return a success message on completion.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Extract validated refresh token
        refresh_token = serializer.validated_data["refresh_token"]

        try:
            # Attempt to blacklist the token via service layer
            LogoutService.logout_user(user=request.user, refresh_token=refresh_token)

        except ValueError as ve:
            # Known error: token invalid or expired
            return api_response(
                message=str(ve),
                status_code=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            # Unknown error: log for debugging and return generic 500
            logger.error(f"Logout failed for user {request.user.email}: {str(e)}", exc_info=True)
            return api_response(
                message="Something went wrong while logging out.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # API Response
        logger.info(f"User {request.user.email} logged out successfully.")
        return api_response(
            message="Logout successful.",
            status_code=status.HTTP_200_OK
        )
