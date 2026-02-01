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
from accounts.serializers.auth import RegisterSerializer, UserSerializer
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
# Register View
# ----------------------
@register_schema
class RegisterView(generics.CreateAPIView):
    """
    Registers a new user, sends an email verification link,
    and returns the newly created user.
    """
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # ----------------------
            # DB transaction for safe creation
            # ----------------------
            with transaction.atomic():
                user = serializer.save()
                logger.info(
                    f"New user registered: {user.email} (ID: {user.id}) "
                    f"from IP: {get_client_ip(request)}"
                )

                # Ensure UserSecurity exists
                security, _ = UserSecurity.objects.get_or_create(user=user)

                # Generate email verification token
                un_hashed = secrets.token_hex(20)
                hashed = hashlib.sha256(un_hashed.encode()).hexdigest()
                expiry = timezone.now() + timedelta(hours=24)

                security.email_verification_token = hashed
                security.email_verification_expiry = expiry
                security.save(update_fields=[
                    "email_verification_token",
                    "email_verification_expiry"
                ])

        except Exception as e:
            logger.error(
                f"Registration failed for email {request.data.get('email')}: {str(e)}"
            )
            return api_response(
                message="Registration failed. Please try again.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # ----------------------
        # Send verification email AFTER successful DB transaction
        # ----------------------
        try:
            verify_link = f"{settings.FRONTEND_URL}/verify-email/{un_hashed}"
            send_email(
                to_email=user.email,
                template_id=settings.SENDGRID_VERIFY_TEMPLATE_ID,
                dynamic_data={
                    "username": user.username,
                    "verification_code": un_hashed,
                },
            )
            logger.info(f"Verification email sent to {user.email}")
        except Exception as e:
            logger.warning(f"Failed to send verification email to {user.email}: {str(e)}")

        # ----------------------
        # Return API response
        # ----------------------
        return api_response(
            message="User registered successfully. Please verify your email.",
            data={
                "user": UserSerializer(user).data,
            },
            status_code=status.HTTP_201_CREATED
        )
