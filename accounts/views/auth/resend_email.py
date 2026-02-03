# =============================================================
# Django REST Framework
# =============================================================
from rest_framework import generics, status, permissions

# =============================================================
# Local App
# =============================================================
from accounts.serializers.auth.auth import ResendEmailSerializer
from accounts.services.auth import ResendEmailService

# =============================================================
# Core Utilities
# =============================================================
from core.utils.responses import api_response

# =============================================================
# Resend Email View
# =============================================================
class ResendEmailView(generics.GenericAPIView):
    """
    API endpoint to resend email verification tokens.

    Responsibilities:
    1. Accept a request to resend email verification.
    2. Validate input using ResendEmailSerializer.
    3. Delegate token regeneration & email sending to ResendEmailService.
    4. Return standardized API response.

    Design Notes:
    - Publicly accessible endpoint (AllowAny) since users may need to verify email again.
    - Does not reveal if email exists for security reasons.
    """
    serializer_class = ResendEmailSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to resend email verification token.

        Steps:
        1. Validate incoming request data.
        2. Delegate token regeneration & email sending to the service layer.
        3. Return generic success message.

        Args:
            request: DRF request object.

        Returns:
            Response: DRF Response with generic success message.

        Raises:
            ValidationError: If serializer validation fails (handled by DRF automatically).
            InternalServerException: If service layer fails to resend email.
        """
        # 1. Validate input
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 2. Delegate to service layer
        ResendEmailService.resend_verification_email(
            user=serializer.validated_data["user"],
            security=serializer.validated_data["security"],
        )

        # 3. Return standardized API response
        return api_response(
            message="If the account exists, a verification email has been sent.",
            status_code=status.HTTP_200_OK,
        )
