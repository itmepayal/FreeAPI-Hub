# =============================================================
# Django REST Framework
# =============================================================
from rest_framework import generics, status, permissions

# =============================================================
# Local App
# =============================================================
from accounts.serializers.auth import LoginSerializer, UserSerializer
from accounts.swagger.auth import login_schema
from accounts.services.auth import LoginService

# =============================================================
# Core Utilities
# =============================================================
from core.utils.responses import api_response
from core.utils.helpers import get_client_ip

# =============================================================
# Login View
# =============================================================
@login_schema
class LoginView(generics.GenericAPIView):
    """
    API endpoint to handle user login with email & password.

    Responsibilities:
    1. Accept login credentials and validate input.
    2. Delegate authentication, 2FA, and token generation to LoginService.
    3. Return structured API response with user info and tokens or 2FA instructions.

    Design Notes:
    - Uses serializer for input validation.
    - Service layer handles all business logic.
    - Returns generic success messages; 2FA requirement is clearly indicated.
    - Publicly accessible (AllowAny permission).
    """
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests for login.

        Steps:
        1. Validate input using LoginSerializer.
        2. Call LoginService.login_user with validated data.
        3. Return structured API response with user info & tokens, or 2FA instructions.

        Args:
            request: DRF request object.

        Returns:
            Response: DRF Response containing login result.

        Raises:
            ValidationError: If serializer validation fails.
            Service-layer exceptions: Propagated to global exception handler.
        """
        # 1. Validate input
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        # 2. Delegate authentication & token generation to service layer
        result = LoginService.login_user(
            email=email,
            password=password,
            request_ip=get_client_ip(request)
        )

        # 3. Handle 2FA scenario
        if result.get("requires_2fa"):
            return api_response(
                message="OTP required to complete login.",
                data={
                    "requires_2fa": True,
                    "temp_token": result["temp_token"],
                },
                status_code=status.HTTP_200_OK,
            )

        # 4. Return structured API response
        return api_response(
            message="Login successful.",
            data={
                "user": UserSerializer(result["user"]).data,
                "tokens": result["tokens"],
            },
            status_code=status.HTTP_200_OK,
        )
