# =============================================================
# Django
# =============================================================
from django.conf import settings
from django.db import transaction

# =============================================================
# Local Models
# =============================================================
from accounts.models import User, UserSecurity

# =============================================================
# Core Utilities
# =============================================================
from core.exceptions import PermissionDeniedException, InternalServerException
from core.email import send_email
from core.utils.helpers import get_client_ip

# =============================================================
# Base Service
# =============================================================
from accounts.services import BaseService

# =============================================================
# Resend Email Verification Service
# =============================================================
class ResendEmailService(BaseService):

    @classmethod
    def resend_verification_email(cls, email: str, request) -> None:
        try:
            # Step 1 — Lookup user silently 
            user = User.objects.filter(email=email).first()

            if not user:
                cls.logger().info(
                    "Resend verification requested for non-existing email",
                    extra={"email": email},
                )
                return  # Silent success response

            # Step 2 — Ensure user account is active
            if not user.is_active:
                cls.logger().warning(
                    "Inactive user attempted email verification resend",
                    extra={"user_id": user.id, "email": user.email},
                )
                raise PermissionDeniedException("User account is inactive.")

            # Step 3 — Fetch related security record
            security = UserSecurity.objects.get(user=user)

            # Step 4 — Rotate verification token atomically
            with transaction.atomic():

                raw_token = security.generate_email_verification_token()

                cls.logger().info(
                    "Verification email resend initiated",
                    extra={
                        "user_id": user.id,
                        "email": user.email,
                        "ip": get_client_ip(request),
                    },
                )

            # Step 5 — Send verification email after DB commit
            transaction.on_commit(
                lambda: cls.send_verification_email(user, raw_token)
            )

        except PermissionDeniedException:
            raise

        except Exception as exc:
            # Step 6 — Log failure with context
            cls.logger().error(
                "Verification email resend failed",
                exc_info=True,
                extra={"email": email},
            )

            # Step 7 — Raise controlled internal error
            raise InternalServerException(
                "Failed to resend verification email. Please try again later."
            ) from exc

    # =========================================================
    # Email Sender
    # =========================================================
    @classmethod
    def send_verification_email(cls, user: User, raw_token: str) -> None:
        # Step 1 — Build frontend verification URL
        verify_link = f"{settings.FRONTEND_URL}/verify-email/{raw_token}"

        # Step 2 — Dispatch email via email service
        send_email(
            to_email=user.email,
            template_id=settings.SENDGRID_EMAIL_VERIFICATION_TEMPLATE_ID,
            dynamic_data={
                "username": user.username,
                "verify_link": verify_link,
            },
        )

        # Step 3 — Log successful email dispatch
        cls.logger().info(
            "Verification email resent successfully",
            extra={"user_id": user.id},
        )
