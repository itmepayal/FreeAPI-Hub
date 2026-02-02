# =============================================================
# Standard Library
# =============================================================
import secrets
import hashlib
from datetime import timedelta

# =============================================================
# Django
# =============================================================
from django.conf import settings
from django.utils import timezone

# =============================================================
# Local Models
# =============================================================
from accounts.models import UserSecurity

# =============================================================
# Core Utilities & Exceptions
# =============================================================
from core.logging.logger import get_logger
from core.email.services import send_email
from core.exception.base import InternalServerException

# =============================================================
# Logger
# =============================================================
logger = get_logger(__name__)

# =============================================================
# Register Service
# =============================================================
class RegisterService:
    """
    Handles registration-related side effects:
    - Generate secure email verification token
    - Persist hashed token in UserSecurity
    - Send verification email
    """

    @staticmethod
    def create_email_verification(user):
        """
        Generate and store an email verification token.

        Raises:
            InternalServerException: If DB operation fails
        """
        try:
            # Generate secure random token
            raw_token = secrets.token_hex(20)

            # Hash token before storing
            hashed_token = hashlib.sha256(raw_token.encode()).hexdigest()

            # Set token expiry
            expiry = timezone.now() + timedelta(
                hours=settings.EMAIL_VERIFICATION_EXPIRY_HOURS
            )

            # Ensure UserSecurity record exists
            security, _ = UserSecurity.objects.get_or_create(user=user)

            # Persist verification details
            security.email_verification_token = hashed_token
            security.email_verification_expiry = expiry
            security.save(
                update_fields=[
                    "email_verification_token",
                    "email_verification_expiry",
                ]
            )

            return raw_token

        except Exception as e:
            logger.error(f"Failed to create email verification for {user.email}: {str(e)}", exc_info=True)
            raise InternalServerException("Failed to generate email verification token.") from e

    @staticmethod
    def send_verification_email(user, raw_token):
        """
        Send the email verification message to the user.

        Raises:
            InternalServerException: If sending email fails
        """
        try:
            # Construct frontend verification URL
            verify_link = f"{settings.FRONTEND_URL}/verify-email/{raw_token}"

            # Send email using SendGrid dynamic template
            send_email(
                to_email=user.email,
                template_id=settings.SENDGRID_EMAIL_VERIFICATION_TEMPLATE_ID,
                dynamic_data={
                    "username": user.username,
                    "verify_link": verify_link,
                },
            )

            logger.info(
                "Verification email sent successfully",
                extra={
                    "user_id": user.id,
                    "email": user.email,
                },
            )

        except Exception as e:
            logger.error(f"Failed to send verification email to {user.email}: {str(e)}", exc_info=True)
            raise InternalServerException("Failed to send verification email.") from e
