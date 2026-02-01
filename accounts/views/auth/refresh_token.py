# Django REST Framework
from rest_framework import generics, status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

# Local App Serializer
from accounts.serializers.auth import RefreshTokenSerializer
# Local App Swagger Documentation
from accounts.swagger.auth.refresh_token import refresh_token_schema

# Core Utilities
from core.utils.responses import api_response
from core.logging.logger import get_logger

# =============================================================
# Logger
# =============================================================
logger = get_logger(__name__)

# ----------------------
# RefreshTokenView View
# ----------------------
@refresh_token_schema
class RefreshTokenView(generics.GenericAPIView):
    """
    Generate a new access token using a valid refresh token.
    """
    serializer_class = RefreshTokenSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Validate Refresh Token
        refresh_token = serializer.validated_data["refresh_token"]
        
        try:
            # Token verification & parsing
            token = RefreshToken(refresh_token)
            
            # Generate new access token
            new_access_token = str(token.access_token)
            
            logger.info("Access token refreshed successfully")
            
            # ----------------------
            # Return API response
            # ----------------------
            return api_response(
                message="Access token refreshed successfully.",
                data={
                    "access": new_access_token
                },
                status_code=status.HTTP_200_OK
            )

        except TokenError as e:
            logger.warning(f"Refresh token invalid: {str(e)}")
            return api_response(
                message="Invalid or expired refresh token.",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
            