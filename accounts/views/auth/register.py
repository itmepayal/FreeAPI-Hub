# =============================================================
# Django REST Framework
# =============================================================
from rest_framework import generics, status, permissions

# =============================================================
# Local App
# =============================================================
from accounts.serializers.auth import RegisterSerializer, UserSerializer
from accounts.swagger.auth import register_schema
from accounts.services.auth.register_service import RegisterService

# =============================================================
# Core Utilities
# =============================================================
from core.utils.responses import api_response

# =============================================================
# Register View
# =============================================================
@register_schema
class RegisterView(generics.CreateAPIView):
    """
    API endpoint to handle user registration.

    Responsibilities:
    1. Accept registration requests with validated input.
    2. Delegate user creation and email verification logic to RegisterService.
    3. Return structured API response with newly created user data.
    
    Design Notes:
    - Uses serializer for input validation.
    - Service layer handles all business logic (user creation, token generation, email sending).
    - Returns generic success message; email sending failures do not block registration.
    - Suitable for public access (AllowAny permission).
    """
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to register a new user.

        Steps:
        1. Validate incoming request data using RegisterSerializer.
        2. Call RegisterService.register_user to create the user and trigger email verification.
        3. Return structured success response with serialized user data.

        Args:
            request: DRF request object.

        Returns:
            Response: DRF Response with success message and user data.

        Raises:
            ValidationError: If serializer validation fails (handled by DRF automatically).
            InternalServerException: If service layer fails to create user (propagated via global exception handler).
        """
        # 1. Validate incoming request data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 2. Delegate user creation to service layer
        user = RegisterService.register_user(
            validated_data=serializer.validated_data,
            request=request,
        )

        # 3. Return structured API response
        return api_response(
            message="User registered successfully. Please verify your email.",
            data={
                "user": UserSerializer(user).data,
            },
            status_code=status.HTTP_201_CREATED,
        )
