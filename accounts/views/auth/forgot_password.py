# =============================================================
# Django REST Framework
# =============================================================
from rest_framework import generics, status, permissions

# =============================================================
# Local App Serializer & Services
# =============================================================
from accounts.serializers.auth.auth import ForgotPasswordSerializer
from accounts.swagger.auth import register_schema
from accounts.services.auth import ForgotPasswordService

# =============================================================
# Core Utilities
# =============================================================
from core.utils.responses import api_response
from core.utils.helpers import get_client_ip

# =============================================================
# Forgot Password View
# =============================================================
@register_schema
class ForgotPasswordView(generics.GenericAPIView):
    """
    API endpoint to handle "forgot password" requests.

    Responsibilities:
    1. Accept email input for password reset request.
    2. Delegate token generation & email sending to ForgotPasswordService.
    3. Always return generic success message to prevent email enumeration.

    Design Notes:
    - Publicly accessible (AllowAny permission).
    - Business logic is fully handled in the service layer.
    """
    serializer_class = ForgotPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests for password reset.

        Steps:
        1. Validate email input using serializer.
        2. Call service layer to generate token and send reset email.
        3. Return generic success response regardless of user existence.

        Args:
            request: DRF request object.

        Returns:
            Response: DRF Response with generic success message.

        Raises:
            ValidationError: If serializer validation fails.
            InternalServerException: If service layer fails unexpectedly.
        """
        # 1. Validate input
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        # 2. Delegate password reset logic to service layer
        ForgotPasswordService.send_reset_email(email=email, request_ip=get_client_ip(request))

        # 3. Return generic success response
        return api_response(
            message="If the email exists, a reset link has been sent.",
            status_code=status.HTTP_200_OK,
        )
