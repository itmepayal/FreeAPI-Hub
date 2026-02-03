# =============================================================
# Django REST Framework
# =============================================================
from rest_framework import generics, status, permissions

# =============================================================
# Local App
# =============================================================
from accounts.serializers.auth.password import ResetPasswordSerializer
from accounts.swagger.auth import register_schema
from accounts.services.auth import ResetPasswordService

# =============================================================
# Core Utilities
# =============================================================
from core.utils.responses import api_response

# =============================================================
# Reset Password View
# =============================================================
@register_schema
class ResetPasswordView(generics.GenericAPIView):
    """
    API endpoint to reset a user's password using a valid reset token.

    Responsibilities:
    1. Accept password reset token and new password from user.
    2. Delegate password validation and update to ResetPasswordService.
    3. Return structured API response upon success.

    Design Notes:
    - Publicly accessible (AllowAny permission).
    - Does not expose internal errors or token state.
    - Fully relies on service layer for business logic.
    """
    serializer_class = ResetPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Handle POST request to reset password.

        Steps:
        1. Validate incoming token and new password using serializer.
        2. Call ResetPasswordService.reset_password() to perform the update.
        3. Return success response if password updated successfully.

        Args:
            request: DRF request object.

        Returns:
            Response: DRF Response with success message.

        Raises:
            ValidationError: If serializer validation fails.
            InvalidTokenException / ValidationException / InternalServerException:
                If service layer raises an exception, propagated globally.
        """
        # 1. Validate input
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]

        # 2. Delegate password reset to service layer
        ResetPasswordService.reset_password(token=token, new_password=new_password)

        # 3. Return structured API response
        return api_response(
            message="Password reset successfully. You can now log in.",
            status_code=status.HTTP_200_OK,
        )
