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
from django.db import transaction

# =============================================================
# Local Models
# =============================================================
from accounts.models import User, UserSecurity

# =============================================================
# Core Exceptions
# =============================================================
from core.exceptions.base import InternalServerException

# =============================================================
# Email Service
# =============================================================
from core.email.services import send_email 

# =============================================================
# Base Service
# =============================================================
from accounts.services.base import BaseService


# =============================================================
# Register Service
# =============================================================
class RegisterService(BaseService):
    """
    Service layer for handling user registration.

    Responsibilities:
    1. Create a new user in the database.
    2. Generate a secure email verification token and store its hash.
    3. Send verification email to the user.
    4. Log all relevant actions for traceability.

    Design Notes:
    - Uses transaction.atomic() to ensure DB consistency.
    - Email sending occurs outside the transaction to avoid rollback if email fails.
    - Any unexpected errors are wrapped in InternalServerException.
    """

    @classmethod
    def register_user(cls, validated_data: dict, request) -> User:
        """
        Main method to register a user and trigger email verification.

        Steps:
        1. Create user in DB.
        2. Generate email verification token and save hash.
        3. Send verification email to the user.
        4. Return the created User object.

        Args:
            validated_data (dict): Cleaned user input data from serializer.
            request: DRF request object (used to log client IP).

        Returns:
            User: Newly created user instance.

        Raises:
            InternalServerException: If user creation or token generation fails.
        """
        try:
            with transaction.atomic():
                # 1. Create the user
                user = User.objects.create_user(**validated_data)

                cls.logger().info(
                    "New user registered",
                    extra={
                        "user_id": user.id,
                        "email": user.email,
                        "ip": cls.get_client_ip(request),
                    },
                )

                # 2. Generate email verification token
                raw_token = cls.create_email_verification(user)

            # 3. Send verification email AFTER successful commit
            try:
                cls.send_verification_email(user, raw_token)
            except Exception as exc:
                # Only log a warning; user is already created
                cls.logger().warning(
                    "Failed to send verification email",
                    exc_info=True,
                    extra={"user_id": user.id, "email": user.email},
                )

            # 4. Return user object
            return user
        
        except ValidationException:
            raise

        except Exception as exc:
            cls.logger().error(
                "User registration failed",
                exc_info=True,
                extra={"email": validated_data.get("email")},
            )
            raise InternalServerException("User registration failed.") from exc

    @classmethod
    def create_email_verification(cls, user) -> str:
        """
        Generate a secure email verification token and store its hash in the DB.

        Steps:
        1. Generate a random 20-byte hex token.
        2. Hash the token using SHA-256 for secure storage.
        3. Set an expiry timestamp based on settings.
        4. Save the hashed token and expiry in UserSecurity model.

        Args:
            user (User): The user for whom the token is generated.

        Returns:
            str: The raw (unhashed) token to send via email.
        """
        raw_token = secrets.token_hex(20)
        hashed_token = hashlib.sha256(raw_token.encode()).hexdigest()
        expiry = timezone.now() + timedelta(hours=settings.EMAIL_VERIFICATION_EXPIRY_HOURS)

        # Create or update security record
        security, _ = UserSecurity.objects.get_or_create(user=user)
        security.email_verification_token = hashed_token
        security.email_verification_expiry = expiry
        security.save(update_fields=["email_verification_token", "email_verification_expiry"])

        return raw_token

    @classmethod
    def send_verification_email(cls, user, raw_token: str):
        """
        Send a verification email to the user with the provided token.

        Args:
            user (User): User object to send email to.
            raw_token (str): Unhashed token to include in email verification link.

        Raises:
            InternalServerException: If sending email fails (logged but does not rollback user creation).
        """
        verify_link = f"{settings.FRONTEND_URL}/verify-email/{raw_token}"

        send_email(
            to_email=user.email,
            template_id=settings.SENDGRID_EMAIL_VERIFICATION_TEMPLATE_ID,
            dynamic_data={
                "username": user.username,
                "verify_link": verify_link,
            },
        )

        cls.logger().info(
            "Verification email sent successfully",
            extra={"user_id": user.id, "email": user.email},
        )

    @staticmethod
    def get_client_ip(request):
        """
        Extract the client's IP address from request headers.

        Args:
            request: DRF request object.

        Returns:
            str: Client IP address.
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
