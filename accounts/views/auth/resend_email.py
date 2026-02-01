# Python Standard Library
import secrets
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
from accounts.serializers.auth import ResendEmailSerializer
# Local App Swagger Documentation
from accounts.swagger.auth.email_verification import verify_email_schema

# Core Utilities
from core.email.services import send_email 
from core.logging.logger import get_logger
from core.utils.responses import api_response

# =============================================================
# Logger
# =============================================================
logger = get_logger(__name__)

# ----------------------
# ResendEmail View
# ----------------------
class ResendEmailView(generics.GenericAPIView):
    """
    Resend email verification token to user.
    """
    serializer_class = ResendEmailSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # User and Security Validate
        user = serializer.validated_data["user"]
        security = serializer.validated_data["security"]
        
        if not getattr(user, "is_active", True):
            return api_response(
                message="User account is inactive.",
                status_code=status.HTTP_403_FORBIDDEN,
            )
            
        try:
            with transaction.atomic():
                # Generate Token
                token = secrets.token_urlsafe(32)
                hashed_token = hashlib.sha256(token.encode()).hexdigest()
                expiry = timezone.now() + timedelta(minutes=30)
                
                # Update Security Object
                security.email_verification_token = hashed_token
                security.email_verification_expiry = expiry
                security.save(update_fields=["email_verification_token", "email_verification_expiry"])

                # ----------------------
                # Send verification email AFTER successful DB transaction
                # ----------------------
                send_email(
                    to_email=user.email,
                    subject="Verify your email",
                    template_name="email_verification",
                    context={
                        "username": user.username,
                        "verification_code": token,
                    }
                )
                logger.info(f"Resent verification email to {user.email}")
        except Exception as e:
            logger.error(f"Failed to resend verification email to {user.email}: {str(e)}", exc_info=True)
            return api_response(
                message="Failed to send verification email. Try again later.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # ----------------------
        # Return API response
        # ----------------------
        return api_response(
            message="Verification email resent successfully.",
            status_code=status.HTTP_200_OK
        )
