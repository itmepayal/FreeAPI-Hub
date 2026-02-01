# Django REST Framework
from rest_framework import generics, status, permissions
from rest_framework_simplejwt.tokens import RefreshToken

# Local App Serializer
from accounts.serializers.auth import RefreshTokenSerializer
# Local App Swagger Documentation
from accounts.swagger.auth.logout import logout_schema

# Core Utilities
from core.utils.responses import api_response
from core.logging.logger import get_logger

# =============================================================
# Logger
# =============================================================
logger = get_logger(__name__)

# ----------------------
# Logout View
# ----------------------
@logout_schema
class LogoutView(generics.GenericAPIView):
    """
    Logout user by blacklisting their refresh token
    """
    serializer_class = RefreshTokenSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Validate Refresh Token
        refresh_token = serializer.validated_data["refresh_token"]
        
        try:
            # Token verification & parsing
            token = RefreshToken(refresh_token)
            
            # Blacklist the token
            token.blacklist()
            
            logger.info(f"User logged out: {request.user.email}")
            
            # ----------------------
            # Return API response
            # ----------------------
            return api_response(
                message="Logout successful.",
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Logout failed: {str(e)}")
            return api_response(
                message="Invalid or expired refresh token.",
                status_code=status.HTTP_400_BAD_REQUEST
            )