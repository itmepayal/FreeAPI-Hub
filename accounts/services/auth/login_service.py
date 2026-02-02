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
from core.logging.logger import get_logger
from core.exception.base import (
    InvalidTokenException,
    AuthenticationRequiredException,
    InactiveUserException
)

# =============================================================
# Logger
# =============================================================
logger = get_logger(__name__)

# =============================================================
# Login Service
# =============================================================
class LoginService:
    """
    Handles user login and JWT token generation.
    """

    @staticmethod
    def login_user(email: str, password: str, request_ip: str):
        """
        Authenticate user, check email verification, and generate JWT tokens.

        Args:
            email (str): User email
            password (str): User password
            request_ip (str): IP address for logging

        Returns:
            dict: Dictionary containing user instance and tokens or 2FA info

        Raises:
            AuthenticationRequiredException: If credentials are invalid
            InactiveUserException: If the user is inactive
            InvalidTokenException: If email is not verified
        """
        # Authenticate user
        user = authenticate(email=email, password=password)
        
        if not user:
            logger.warning(f"Failed login attempt for email: {email} from IP: {request_ip}")
            raise AuthenticationRequiredException("Invalid credentials.")

        if not user.is_active:
            logger.warning(f"Inactive user {email} attempted login from IP: {request_ip}")
            raise InactiveUserException("User account is inactive.")

        if not user.is_verified:
            raise InvalidTokenException("Email is not verified. Please verify your email first.")

        security = user.security

        # IF 2FA enabled → RETURN temp token
        if security.is_2fa_enabled:
            temp_token = LoginService._generate_2fa_token(user)
            logger.info(f"User {email} requires 2FA for login from IP: {request_ip}")
            return {
                "user": user,
                "requires_2fa": True,
                "temp_token": temp_token,
            }

        # Generate JWT tokens
        tokens = LoginService._generate_tokens(user)

        logger.info(f"User logged in successfully without 2FA: {email} from IP: {request_ip}")
        return {
            "user": user,
            "tokens": tokens,
        }

    @staticmethod
    def _generate_tokens(user: User):
        """
        Generate standard JWT access & refresh tokens.
        """
        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

    @staticmethod
    def _generate_2fa_token(user: User):
        """
        Generate a short-lived 2FA token used ONLY for OTP verification.
        """
        token = AccessToken.for_user(user)
        token["type"] = "2fa"
        token.set_exp(lifetime=timedelta(minutes=5))
        return str(token)
