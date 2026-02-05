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
# Core Exceptions
# =============================================================
from core.exceptions import (
    InternalServerException,
    ServiceException,
)

# =============================================================
# Core Services
# =============================================================
from core.email import send_email
from core.utils.helpers import get_client_ip

# =============================================================
# Base Service
# =============================================================
from accounts.services import BaseService

# =============================================================
# Forgot Password Service
# =============================================================
class ForgotPasswordService(BaseService):

    @classmethod
    def send_reset_email(cls, email: str, request) -> None:
        try:
            # Step 1 — Lookup user 
            user = User.objects.filter(email=email).first()

            if not user:
                cls.logger().info(
                    "Password reset requested for non-existent email",
                    extra={
                        "email": email,
                        "ip": get_client_ip(request),
                    },
                )
                return

            # Step 2 — Start atomic transaction
            with transaction.atomic():

                # Step 3 — Lock security row
                security, _ = (
                    UserSecurity.objects
                    .select_for_update()
                    .get_or_create(user=user)
                )

                # Step 4 — Generate reset token (hashed in DB)
                raw_token = security.generate_forgot_password()

                # Step 5 — Log reset request
                cls.logger().info(
                    "Password reset token generated",
                    extra={
                        "user_id": user.id,
                        "email": user.email,
                        "ip": get_client_ip(request),
                    },
                )

            # Step 6 — Send email ONLY after successful commit
            transaction.on_commit(
                lambda: cls.send_password_reset_email(user, raw_token)
            )

        except ServiceException:
            raise

        except Exception as exc:
            cls.logger().error(
                "Password reset flow failed",
                exc_info=True,
                extra={"email": email},
            )
            raise InternalServerException(
                "Failed to process password reset request."
            ) from exc

    # =========================================================
    # Email Sender
    # =========================================================
    @classmethod
    def send_password_reset_email(cls, user: User, raw_token: str) -> None:

        # Step 1 — Build frontend reset URL
        reset_link = (
            f"{settings.FRONTEND_URL}/reset-password/{raw_token}"
        )

        # Step 2 — Send reset email
        send_email(
            to_email=user.email,
            template_id=settings.SENDGRID_PASSWORD_RESET_TEMPLATE_ID,
            dynamic_data={
                "username": user.username,
                "reset_link": reset_link,
            },
        )

        # Step 3 — Log email success
        cls.logger().info(
            "Password reset email sent",
            extra={"user_id": user.id},
        )
        