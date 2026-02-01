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
from accounts.serializers.auth import VerifyEmailSerializer
# Local App Swagger Documentation
from accounts.swagger.auth.email_verification import verify_email_schema

# Core Utilities
from core.logging.logger import get_logger
from core.utils.responses import api_response

# =============================================================
# Logger
# =============================================================
logger = get_logger(__name__)

# ----------------------
# VerifyEmail View
# ----------------------
@verify_email_schema
class VerifyEmailView(generics.GenericAPIView):
    """
    Verify user email using token sent to their email.
    """
    serializer_class = VerifyEmailSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]
        
        # Hash token to match DB
        hashed_token = hashlib.sha256(token.encode()).hexdigest()
        
        try:
            with transaction.atomic():
                # Ensure UserSecurity exists
                security = UserSecurity.objects.select_related("user").filter(
                    email_verification_token=hashed_token
                ).first()
                
                if not security:
                    return api_response(
                        message="Invalid verification token.",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                    
                if security.email_verification_expiry < timezone.now():
                    return api_response(
                        message="Token has expired.",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                
                # Get user first
                user = security.user

                # Prevent re-verification
                if user.is_verified:
                    return api_response(
                        message="Email already verified.",
                        status_code=status.HTTP_409_CONFLICT
                    )

                # Mark user as verified
                user = security.user
                user.is_verified = True
                user.save(update_fields=["is_verified"])

                # Clear verification token
                security.email_verification_token = None
                security.email_verification_expiry = None
                security.save(
                    update_fields=[
                        "email_verification_token", 
                        "email_verification_expiry"
                    ]
                )
                
                logger.info(f"User {user.email} verified their email successfully.")

        except Exception as e:
            logger.error(f"Email verification failed: {str(e)}")
            return api_response(
                message="Verification failed. Please try again.", 
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # ----------------------
        # Return API response
        # ----------------------
        return api_response(
            message="Email verified successfully.", 
            data={"user": {"id": user.id, "email": user.email}},
            status_code=status.HTTP_200_OK
        )
