# =============================================================
# Django
# =============================================================
from django.contrib.auth import authenticate

# =============================================================
# Django REST Framework
# =============================================================
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

# =============================================================
# Local App
# =============================================================
from accounts.models.user import User
from accounts.serializers.auth import UserSerializer, LoginSerializer
from accounts.swagger.auth import login_schema
from accounts.services.auth import LoginService

# =============================================================
# Core Utilities
# =============================================================
from core.utils.responses import api_response
from core.logging.logger import get_logger
from core.utils.helpers import get_client_ip

# =============================================================
# Logger
# =============================================================
logger = get_logger(__name__)

# =============================================================
# Login View
# =============================================================
@login_schema
class LoginView(generics.GenericAPIView):
    """
    Login user using email & password and return JWT tokens.

    Features:
    - Validates email and password via serializer.
    - Checks if user is active and email is verified.
    - Handles 2FA (returns temp token if required).
    - Uses service layer for authentication logic.
    - Provides structured API responses for success and errors.
    """
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        # Validate input
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        try:
            # Delegate login logic to service
            result = LoginService.login_user(
                email=email,
                password=password,
                request_ip=get_client_ip(request)
            )

            # Handle 2FA scenario
            if result.get("requires_2fa"):
                return api_response(
                    message="OTP required to complete login.",
                    data={
                        "requires_2fa": True,
                        "temp_token": result["temp_token"],
                    },
                    status_code=status.HTTP_200_OK,
                )

        except ValueError as ve:
            # Known login errors (invalid credentials, unverified email)
            logger.warning(f"Login failed for {email}: {str(ve)}")
            return api_response(
                message=str(ve),
                status_code=status.HTTP_401_UNAUTHORIZED,
                code="login_failed"
            )

        except Exception as e:
            # Unexpected errors (DB, JWT, etc.)
            logger.error(f"Login failed for {email}: {str(e)}", exc_info=True)
            return api_response(
                message="Login failed. Please try again later.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                code="internal_error"
            )

        # API Response
        return api_response(
            message="Login successful.",
            data={
                "user": UserSerializer(result["user"]).data,
                "tokens": result["tokens"],
            },
            status_code=status.HTTP_200_OK,
        )
