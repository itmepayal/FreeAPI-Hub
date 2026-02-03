# =============================================================
# Django REST Framework
# =============================================================
from rest_framework import generics, status, permissions

# =============================================================
# Local App
# =============================================================
from accounts.serializers.auth import VerifyEmailSerializer
from accounts.swagger.auth import verify_email_schema
from accounts.services.auth.verify_email_service import VerifyEmailService

# =============================================================
# Core Utilities
# =============================================================
from core.utils.responses import api_response

# =============================================================
# VerifyEmail View
# =============================================================
@verify_email_schema
class VerifyEmailView(generics.GenericAPIView):
    """
    API endpoint to verify a user's email using a token sent via email.

    Responsibilities:
    1. Accept email verification token from client.
    2. Delegate verification logic to VerifyEmailService.
    3. Return success response with verified user info.

    Design Notes:
    - Service layer handles all business logic.
    - Errors propagate to global exception handler.

    Permission Notes:
    - Uses `AllowAny` because this endpoint must be publicly accessible.
      Users may not be authenticated yet, as email verification often occurs
      right after registration before login is allowed.
    """
    serializer_class = VerifyEmailSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Handle POST request to verify user's email.

        Steps:
        1. Validate incoming token using VerifyEmailSerializer.
        2. Call VerifyEmailService.verify_email to perform verification.
        3. Return structured API response with verified user details.

        Args:
            request: DRF request object.

        Returns:
            Response: DRF Response with success message and user info.

        Raises:
            ValidationError: If serializer validation fails.
            InvalidTokenException / OperationNotAllowedException: If verification fails.
        """
        # 1. Validate incoming request payload
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["token"]

        # 2. Delegate verification to service layer
        security = VerifyEmailService.verify_email(token)
        user = security.user

        # 3. Return structured API response
        return api_response(
            message="Email verified successfully.",
            data={
                "user": {
                    "id": user.id,
                    "email": user.email,
                }
            },
            status_code=status.HTTP_200_OK,
        )
