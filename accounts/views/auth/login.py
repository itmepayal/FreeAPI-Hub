# Django Utilities
from django.contrib.auth import authenticate

# Django REST Framework
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

# Local App Models
from accounts.models.user import User
# Local App Serializer
from accounts.serializers.auth import UserSerializer, LoginSerializer
# Local App Swagger Documentation
from accounts.swagger.auth.login import login_schema

# Core Utilities
from core.utils.responses import api_response
from core.logging.logger import get_logger
from core.utils.helpers import get_client_ip

# =============================================================
# Logger
# =============================================================
logger = get_logger(__name__)

# ----------------------
# Helper: Generate JWT tokens
# ----------------------
def generate_jwt_tokens(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token), str(refresh)

# ----------------------
# Login View
# ----------------------
@login_schema
class LoginView(generics.GenericAPIView):
    """
    Login user with email & password and return JWT tokens.
    """
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Validate Email and Password
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        
        # Authenticate User
        user = authenticate(request, email=email, password=password)
        
        if not user:
            logger.warning(f"Failed login attempt for email: {email}")
            return api_response(
                message="Invalid credentials.",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.is_verified:
            return api_response(
                message="Email is not verified. Please verify your email first.",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        # Generate JWT tokens
        access_token, refresh_token = generate_jwt_tokens(user)

        logger.info(
            f"User logged in: {email} from IP: {get_client_ip(request)}"
        )
        
        # ----------------------
        # Return API response
        # ----------------------
        return api_response(
            message="Login successful.",
            data={
                "user": UserSerializer(user).data,
                "tokens": {
                    "access": access_token,
                    "refresh": refresh_token,
                },
            },
            status_code=status.HTTP_200_OK
        )
