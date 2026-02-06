# =============================================================
# Django REST Framework
# =============================================================
from rest_framework import generics, status, permissions

# =============================================================
# Local App Serializers & Services
# =============================================================
from accounts.serializers.auth import LoginSerializer, UserSerializer
from accounts.services.auth import LoginService

# =============================================================
# Core Utilities
# =============================================================
from core.utils.responses import api_response
from core.utils.helpers import get_client_ip

# =============================================================
# Login View
# =============================================================
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):

        # Step 1 — Validate incoming request data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        # Step 2 — Extract client IP address
        request_ip = get_client_ip(request)

        # Step 3 — Delegate authentication to service layer
        result = LoginService.login_user(
            email=email,
            password=password,
            request_ip=request_ip,
        )

        # Step 4 — Handle 2FA required scenario
        if result.get("requires_2fa"):
            return api_response(
                message="OTP required to complete login.",
                data={
                    "requires_2fa": True,
                    "temp_token": result["temp_token"],
                },
                status_code=status.HTTP_200_OK,
            )

        # Step 5 — Return successful login response
        return api_response(
            message="Login successful.",
            data={
                "user": UserSerializer(result["user"]).data,
                "tokens": result["tokens"],
            },
            status_code=status.HTTP_200_OK,
        )
