# =============================================================
# Python Standard Library
# =============================================================
import secrets
import hashlib
from datetime import timedelta

# =============================================================
# Django
# =============================================================
from django.utils import timezone
from django.db import transaction
from django.conf import settings

# =============================================================
# Local App Models
# =============================================================
from accounts.models import User, UserSecurity

# =============================================================
# Core Utilities & Exceptions
# =============================================================
from core.logging.logger import get_logger
from core.email.services import send_email
from core.exception.base import (
    ResourceNotFoundException,
    InternalServerException
)

# =============================================================
# Logger
# =============================================================
logger = get_logger(__name__)

# =============================================================
# Forgot Password Service
# =============================================================
class ForgotPasswordService:
    """
    Handles generating forgot password tokens and sending reset emails.
    """

    @staticmethod
    def send_reset_email(user: User, request_ip: str):
        """
        Generate a secure token, store it, and send password reset email.

        Args:
            user (User): User instance requesting password reset
            request_ip (str): IP address for logging

        Raises:
            ResourceNotFoundException: If the user or UserSecurity object cannot be found
            InternalServerException: If DB operation or email sending fails
        """
        if not user:
            raise ResourceNotFoundException("User does not exist.")

        try:
            # ----------------------
            # Atomic transaction to ensure DB consistency
            # ----------------------
            with transaction.atomic():
                # Lock row for update to avoid race conditions
                security, _ = UserSecurity.objects.select_for_update().get_or_create(user=user)
                
                # Generate secure token and hash it
                raw_token = secrets.token_urlsafe(32)
                hashed_token = hashlib.sha256(raw_token.encode()).hexdigest()
                
                # Save token and expiry
                security.forgot_password_token = hashed_token
                security.forgot_password_expiry = timezone.now() + timedelta(
                    hours=settings.PASSWORD_RESET_EXPIRY_HOURS
                )
                security.save(update_fields=[
                    "forgot_password_token",
                    "forgot_password_expiry"
                ])
            
            # ----------------------
            # Build reset link and send email
            # ----------------------
            reset_link = f"{settings.FRONTEND_URL}/reset-password/{raw_token}"
            send_email(
                to_email=user.email,
                template_id=settings.SENDGRID_PASSWORD_RESET_TEMPLATE_ID,
                dynamic_data={
                    "username": user.username,
                    "reset_link": reset_link,
                }
            )

            logger.info(f"Password reset email sent to {user.email} from IP: {request_ip}")

        except Exception as e:
            logger.error(f"Failed to generate/send password reset for {user.email}: {str(e)}", exc_info=True)
            raise InternalServerException("Failed to generate or send password reset email. Please try again later.")
