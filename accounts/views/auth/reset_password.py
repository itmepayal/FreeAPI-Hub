# Python Standard Library
import hashlib
from datetime import timedelta

# Django Utilities
from django.utils import timezone
from django.db import transaction

# Django REST Framework
from rest_framework import generics, status, permissions

# Local App Models
from accounts.models import UserSecurity
# Local App Serializers
from accounts.serializers.auth import ResetPasswordSerializer
# Local App Swagger Documentation
from accounts.swagger.auth.register import register_schema

# Core Utilities
from core.logging.logger import get_logger
from core.utils.responses import api_response

# =============================================================
# Logger
# =============================================================
logger = get_logger(__name__)

# ----------------------
# Forgot Password View
# ----------------------
@register_schema
class ResetPasswordView(generics.GenericAPIView):
    """
    Resets user password using a valid reset token
    """
    serializer_class = ResetPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Validate Token & New Password
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]
        
        # Hash the token
        hashed_token = hashlib.sha256(token.encode()).hexdigest()
        
        # Find valid token in DB
        security = UserSecurity.objects.select_related("user").filter(
            forgot_password_token=hashed_token,
            forgot_password_expiry__gt=timezone.now()
        ).first()

        if not security:
            return api_response(
                message="Invalid or expired reset token.",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Atomic password update
            with transaction.atomic():
                user = security.user
                user.set_password(new_password)
                user.save(update_fields=["password"])

            # Invalidate token
            security.forgot_password_token = None   
            security.forgot_password_expiry = None
            security.save(update_fields=[
                    "forgot_password_token",
                    "forgot_password_expiry"
                ])
        except Exception as e:
            logger.error(f"Password reset failed: {str(e)}")
            return api_response(
                message="Unable to reset password. Try again later.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # ----------------------
        # Return API response
        # ----------------------
        return api_response(
            message="Password reset successfully. You can now log in.",
            status_code=status.HTTP_200_OK
        )
        
