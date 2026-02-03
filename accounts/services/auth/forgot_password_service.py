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
from core.exceptions.base import (
    ResourceNotFoundException,
    InternalServerException,
    ServiceException,
)

# =============================================================
# Core Services
# =============================================================
from core.email.services import send_email

# =============================================================
# Base Service
# =============================================================
from accounts.services.base import BaseService

# =============================================================
# Forgot Password Service
# =============================================================
class ForgotPasswordService(BaseService):
    """
    Service layer to handle "forgot password" functionality.

    Responsibilities:
    1. Generate a secure password reset token.
    2. Persist hashed token and expiry in UserSecurity model.
    3. Send password reset email with token link.
    4. Log all relevant actions for traceability.

    Design Notes:
    - Uses transaction.atomic() to ensure DB consistency.
    - Does NOT reveal if the user exists to prevent enumeration attacks.
    - Any unexpected errors are wrapped in InternalServerException.
    """

    @classmethod
    def send_reset_email(cls, email: str, request_ip: str) -> None:
        """
        Handle password reset token generation and email sending.

        Steps:
        1. Fetch user by email (if exists).
        2. Create a secure token and hash it.
        3. Save hashed token and expiry in DB atomically.
        4. Send reset email to user with the raw token link.

        Args:
            email (str): Email address provided in reset request.
            request_ip (str): IP address for logging purposes.

        Raises:
            InternalServerException: If DB operation or email sending fails.
        """
        try:
            # Fetch user; silently ignore if not found
            user = User.objects.filter(email=email).first()
            if not user:
                cls.logger().info(
                    "Password reset requested for non-existent email",
                    extra={"email": email, "ip": request_ip},
                )
                return  # Silently succeed to prevent enumeration

            with transaction.atomic():
                security, _ = UserSecurity.objects.select_for_update().get_or_create(user=user)

                # 1. Generate secure token
                raw_token = secrets.token_urlsafe(32)
                hashed_token = hashlib.sha256(raw_token.encode()).hexdigest()

                # 2. Set token & expiry
                security.forgot_password_token = hashed_token
                security.forgot_password_expiry = timezone.now() + timedelta(
                    hours=settings.PASSWORD_RESET_EXPIRY_HOURS
                )
                security.save(
                    update_fields=["forgot_password_token", "forgot_password_expiry"]
                )

            # 3. Send reset email
            reset_link = f"{settings.FRONTEND_URL}/reset-password/{raw_token}"
            send_email(
                to_email=user.email,
                template_id=settings.SENDGRID_PASSWORD_RESET_TEMPLATE_ID,
                dynamic_data={
                    "username": user.username,
                    "reset_link": reset_link,
                },
            )

            cls.logger().info(
                "Password reset email sent successfully",
                extra={"user_id": user.id, "ip": request_ip},
            )

        except Exception as exc:
            cls.logger().error(
                "Failed to generate/send password reset email",
                exc_info=True,
                extra={"email": email, "ip": request_ip},
            )
            raise InternalServerException(
                "Failed to generate or send password reset email. Please try again later."
            ) from exc
