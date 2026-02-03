# =============================================================
# Python Standard Library
# =============================================================
from datetime import timedelta

# =============================================================
# Django
# =============================================================
from django.contrib.auth import authenticate

# =============================================================
# Local App Models
# =============================================================
from accounts.models.user import User

# =============================================================
# JWT
# =============================================================
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

# =============================================================
# Core Utilities & Exceptions
# =============================================================
from core.exceptions.base import (
    InvalidTokenException,
    AuthenticationRequiredException,
    InactiveUserException,
    InternalServerException,
    ServiceException,
)

# =============================================================
# Base Service
# =============================================================
from accounts.services.base import BaseService

# =============================================================
# Login Service
# =============================================================
class LoginService(BaseService):
    """
    Service layer for handling user login and JWT token generation.

    Responsibilities:
    1. Authenticate user credentials.
    2. Ensure user account is active and email is verified.
    3. Handle 2FA scenarios with temporary tokens.
    4. Generate JWT access & refresh tokens for standard login.
    5. Log all relevant actions for traceability.

    Design Notes:
    - Uses DRF-compatible authenticate method.
    - 2FA tokens are short-lived and separate from standard JWT tokens.
    - Exceptions are meaningful and propagate to global handler.
    """

    @classmethod
    def login_user(cls, email: str, password: str, request_ip: str):
        """
        Authenticate a user and return tokens or 2FA info.

        Steps:
        1. Authenticate using email & password.
        2. Check if user is active.
        3. Verify if email is confirmed.
        4. Check if 2FA is enabled; return temporary token if required.
        5. Otherwise, generate standard JWT tokens.

        Args:
            email (str): User email.
            password (str): User password.
            request_ip (str): IP address for logging.

        Returns:
            dict: {
                "user": User instance,
                "tokens": JWT tokens (if no 2FA),
                "requires_2fa": True/False,
                "temp_token": str (if 2FA required)
            }

        Raises:
            AuthenticationRequiredException: Invalid credentials.
            InactiveUserException: Account inactive.
            InvalidTokenException: Email not verified.
            InternalServerException: Unexpected errors.
        """
        try:
            # 1. Authenticate credentials
            user = authenticate(email=email, password=password)
            if not user:
                cls.logger().warning(
                    "Failed login attempt",
                    extra={"email": email, "ip": request_ip},
                )
                raise AuthenticationRequiredException("Invalid credentials.")

            # 2. Check active status
            if not user.is_active:
                cls.logger().warning(
                    "Inactive user attempted login",
                    extra={"user_id": user.id, "ip": request_ip},
                )
                raise InactiveUserException("User account is inactive.")

            # 3. Check email verification
            if not user.is_verified:
                raise InvalidTokenException(
                    "Email is not verified. Please verify your email first."
                )

            security = user.security

            # 4. Handle 2FA flow
            if security.is_2fa_enabled:
                temp_token = cls._generate_2fa_token(user)
                cls.logger().info(
                    "Login requires 2FA",
                    extra={"user_id": user.id, "ip": request_ip},
                )
                return {
                    "user": user,
                    "requires_2fa": True,
                    "temp_token": temp_token,
                }

            # 5. Standard login: generate tokens
            tokens = cls._generate_tokens(user)
            cls.logger().info(
                "User logged in successfully",
                extra={"user_id": user.id, "ip": request_ip},
            )

            return {
                "user": user,
                "tokens": tokens,
            }

        except ServiceException:
            raise

        except Exception as exc:
            cls.logger().error(
                "Unexpected error during login",
                exc_info=True,
                extra={"email": email, "ip": request_ip},
            )
            raise InternalServerException(
                "Login failed due to an unexpected error."
            ) from exc

    # =============================================================
    # Token Helpers
    # =============================================================
    @staticmethod
    def _generate_tokens(user: User) -> dict:
        """
        Generate standard JWT access & refresh tokens.

        Returns:
            dict: {
                "access": str,
                "refresh": str
            }
        """
        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

    @staticmethod
    def _generate_2fa_token(user: User) -> str:
        """
        Generate a short-lived 2FA token for OTP verification.

        Returns:
            str: JWT token valid for 5 minutes with "type": "2fa"
        """
        token = AccessToken.for_user(user)
        token["type"] = "2fa"
        token.set_exp(lifetime=timedelta(minutes=5))
        return str(token)
