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

# =============================================================
# RefreshToken View
# =============================================================
@refresh_token_schema
class RefreshTokenView(generics.GenericAPIView):
    """
    API endpoint to refresh JWT access tokens using a valid refresh token.

    Responsibilities:
    1. Accept a refresh token from the request body.
    2. Validate input using RefreshTokenSerializer.
    3. Call RefreshTokenService to generate a new access token.
    4. Return a standardized API response with the new access token.

    Design Notes:
    - Uses serializer for input validation.
    - Service layer handles all business logic, logging, and exception handling.
    - Publicly accessible endpoint (AllowAny) since refresh tokens are used for re-authentication.
    """
    serializer_class = RefreshTokenSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to refresh an access token.

        Steps:
        1. Validate incoming request data using serializer.
        2. Delegate token refresh to RefreshTokenService.
        3. Return standardized API response.

        Args:
            request: DRF request object

        Returns:
            Response: DRF Response with success message and new access token.

        Raises:
            ValidationError: If serializer validation fails (handled by DRF automatically).
            InternalServerException: If token refresh fails (propagated via global exception handler).
        """
        # 1. Validate input
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data["refresh_token"]

        # 2. Delegate token refresh to service layer
        access_token = RefreshTokenService.refresh_access_token(refresh_token)

        # 3. Return structured API response
        return api_response(
            message="Access token refreshed successfully.",
            data={"access": access_token},
            status_code=status.HTTP_200_OK,
        )
