# Python Standard Library
import secrets
import hashlib
from datetime import timedelta

# Django Utilities
from django.utils import timezone
from django.conf import settings
from django.db import transaction

# Django REST Framework
from rest_framework import generics, status, permissions

# Local App Models
from accounts.models import User, UserSecurity
# Local App Serializers
from accounts.serializers.auth import ForgotPasswordSerializer
# Local App Swagger Documentation
from accounts.swagger.auth.register import register_schema

# Core Utilities
from core.logging.logger import get_logger
from core.email.services import send_email
from core.utils.helpers import get_client_ip
from core.utils.responses import api_response

# =============================================================
# Logger
# =============================================================
logger = get_logger(__name__)

# ----------------------
# Forgot Password View
# ----------------------
@register_schema
class ForgotPasswordView(generics.GenericAPIView):
    """
    Sends a password reset link to the user's email
    if the account exists. Does not reveal user existence.
    """
    serializer_class = ForgotPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Validate Email
        email = serializer.validated_data["email"]
        
        # Access IP Address
        ip_address = get_client_ip(request)
    
        # Fetch user        
        user = User.objects.filter(email=email).first()
        
        print(user)

        # Do NOT reveal whether the user exists
        if not user:
            logger.warning(
                f"Forgot password requested for non-existing email: {email} "
                f"from IP: {ip_address}"
            )
            return api_response(
                message="If the email exists, a reset link has been sent.",
                status_code=status.HTTP_200_OK,
            )

        try:
            with transaction.atomic():
                security, _ = UserSecurity.objects.get_or_create(user=user)
                
                raw_token = secrets.token_urlsafe(32)
                hashed_token = hashlib.sha256(raw_token.encode()).hexdigest()
                
                security.forgot_password_token = hashed_token
                security.forgot_password_expiry = timezone.now() + timedelta(minutes=30)
                security.save(update_fields=[
                    "forgot_password_token",
                    "forgot_password_expiry"
                ])

        except Exception as e:
            logger.error(
                f"Failed to generate forgot password token for {email}: {str(e)}"
            )
            return api_response(
                message="Unable to process request. Please try again later.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
        # ----------------------
        # Send verification email AFTER successful DB transaction
        # ----------------------
        try:
            reset_link = f"{settings.FRONTEND_URL}/reset-password/{raw_token}"
            send_email(
                to_email=user.email,
                subject="Reset your password",
                template_name="reset_password",
                context={
                    "username": user.username,
                    "reset_link": reset_link,
                    "message": "You requested a password reset. This link will expire in 30 minutes."
                }
            )
            logger.info(
                f"Password reset email sent to {email} "
                f"from IP: {ip_address}"
            )
        except Exception as e:
            logger.warning(
                f"Failed to send password reset email to {email}: {str(e)}"
            )

        # ----------------------
        # Return API response
        # ----------------------
        return api_response(
            message="If the email exists, a reset link has been sent.",
            status_code=status.HTTP_200_OK,
        )
        
