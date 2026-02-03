# =============================================================
# Django REST Framework
# =============================================================
from rest_framework import generics, permissions

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

# =============================================================
# Logout View
# =============================================================
@logout_schema
class LogoutView(generics.GenericAPIView):
    """
    API endpoint to securely log out a user.

    Responsibilities:
    1. Accept and validate refresh token from the request.
    2. Delegate token blacklisting to LogoutService.
    3. Return standardized success response.
    
    Design Notes:
    - Uses serializer for input validation.
    - Service layer handles all business logic, logging, and exceptions.
    - Suitable for authenticated users only (permissions.IsAuthenticated).
    """
    serializer_class = RefreshTokenSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to log out the user.

        Steps:
        1. Validate incoming refresh token using serializer.
        2. Call LogoutService to blacklist the token.
        3. Return generic success message.

        Args:
            request: DRF request object.

        Returns:
            Response: DRF Response with generic success message.
        """
        # 1. Validate input
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data["refresh_token"]

        # 2. Delegate logout to service layer
        LogoutService.logout_user(
            user=request.user,
            refresh_token=refresh_token,
        )

        # 3. Return standardized API response
        return api_response(
            message="Logout successful.",
            status_code=200,
        )
