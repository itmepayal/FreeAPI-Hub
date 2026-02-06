# =============================================================
# Django REST Framework
# =============================================================
from rest_framework import generics, status, permissions

# =============================================================
# Local App
# =============================================================
from accounts.serializers.auth import RegisterSerializer, UserSerializer
from accounts.services.auth import RegisterService

# =============================================================
# Core Utilities
# =============================================================
from core.utils.responses import api_response

# =============================================================
# Register View
# =============================================================
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):

        # Step 1 — Validate incoming request data using serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Step 2 — Delegate registration logic to service layer
        user = RegisterService.register_user(
            validated_data=serializer.validated_data,
            request=request,
        )

        # Step 3 — Serialize created user for response payload
        user_data = UserSerializer(user).data

        # Step 4 — Return standardized API response
        return api_response(
            message="User registered successfully. Please verify your email.",
            data={
                "user": user_data,
            },
            status_code=status.HTTP_201_CREATED,
        )
