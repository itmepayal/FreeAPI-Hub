# =============================================================
# Django
# =============================================================
from django.conf import settings
from django.db import transaction

# =============================================================
# Local Models
# =============================================================
from accounts.models import User, UserSecurity, UserPresence

# =============================================================
# Core Utilities
# =============================================================
from core.exceptions import InternalServerException
from core.email import send_email
from core.utils.helpers import get_client_ip

# =============================================================
# Base Service
# =============================================================
from accounts.services import BaseService

# =============================================================
# Registration Service
# =============================================================
class RegisterService(BaseService):

    @classmethod
    def register_user(cls, validated_data: dict, request) -> User:
        try:
            # Step 1 — Start atomic transaction for registration flow
            with transaction.atomic():

                # Step 2 — Create user using custom manager logic
                user = User.objects.create_user(**validated_data)

                # Step 3 — Ensure security record exists for tokens & auth metadata
                security, _ = UserSecurity.objects.get_or_create(user=user)

                # Step 4 — Ensure presence record exists for online/offline tracking
                UserPresence.objects.get_or_create(user=user)

                # Step 5 — Generate email verification token (stored hashed in DB)
                raw_token = security.generate_email_verification_token()

                # Step 6 — Log successful registration event
                cls.logger().info(
                    "New user registered",
                    extra={
                        "user_id": user.id,
                        "email": user.email,
                        "ip": get_client_ip(request),
                    },
                )

            # Step 7 — Send verification email only after DB commit succeeds
            transaction.on_commit(
                lambda: cls.send_verification_email(user, raw_token)
            )

            # Step 8 — Return created user instance
            return user

        except Exception as exc:
            # Step 9 — Log failure with context
            cls.logger().error(
                "User registration failed",
                exc_info=True,
                extra={"email": validated_data.get("email")},
            )

            # Step 10 — Raise controlled internal error
            raise InternalServerException("User registration failed.") from exc

    # =========================================================
    # Email Sender
    # =========================================================
    @classmethod
    def send_verification_email(cls, user, raw_token: str):

        # Step 1 — Build frontend verification URL
        verify_link = f"{settings.FRONTEND_URL}/verify-email/{raw_token}"

        # Step 2 — Send verification email via email service
        send_email(
            to_email=user.email,
            template_id=settings.SENDGRID_EMAIL_VERIFICATION_TEMPLATE_ID,
            dynamic_data={
                "username": user.username,
                "verify_link": verify_link,
            },
        )

        # Step 3 — Log email dispatch success
        cls.logger().info(
            "Verification email sent",
            extra={"user_id": user.id}
        )
