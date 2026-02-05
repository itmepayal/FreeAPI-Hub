# =============================================================
# Django
# =============================================================
from django.contrib.auth import authenticate

# =============================================================
# Helpers
# =============================================================
from accounts.helpers import generate_tokens, generate_2fa_token

# =============================================================
# Core Exceptions
# =============================================================
from core.exceptions import (
    InvalidTokenException,
    AuthenticationRequiredException,
    InactiveUserException,
    InternalServerException,
    ServiceException,
)

# =============================================================
# Base Service
# =============================================================
from accounts.services import BaseService

# =============================================================
# Login Service
# =============================================================
class LoginService(BaseService):

    @classmethod
    def login_user(cls, email: str, password: str, request_ip: str):
        try:

            # Step 1 — Authenticate credentials
            user = authenticate(email=email, password=password)

            if not user:
                cls.logger().warning(
                    "Failed login attempt",
                    extra={"email": email, "ip": request_ip},
                )
                raise AuthenticationRequiredException("Invalid credentials.")

            # Step 2 — Check active status
            if not user.is_active:
                cls.logger().warning(
                    "Inactive user attempted login",
                    extra={"user_id": user.id, "ip": request_ip},
                )
                raise InactiveUserException("User account is inactive.")

            # Step 3 — Check email verification
            if not user.is_verified:
                raise InvalidTokenException(
                    "Email is not verified. Please verify your email first."
                )

            # Step 4 — Load security profile safely
            security = getattr(user, "security", None)

            if not security:
                cls.logger().error(
                    "Security profile missing",
                    extra={"user_id": user.id}
                )
                raise ServiceException("User security profile missing.")

            # Step 5 — Handle 2FA flow
            if security.is_2fa_enabled:
                temp_token = generate_2fa_token(user)

                cls.logger().info(
                    "Login requires 2FA",
                    extra={"user_id": user.id, "ip": request_ip},
                )

                return {
                    "user": user,
                    "requires_2fa": True,
                    "temp_token": temp_token,
                }

            # Step 6 — Standard login → generate tokens
            tokens = generate_tokens(user)

            cls.logger().info(
                "User logged in successfully",
                extra={"user_id": user.id, "ip": request_ip},
            )

            return {
                "user": user,
                "tokens": tokens,
            }

        # Known service exceptions → rethrow
        except ServiceException:
            raise

        # Unexpected errors → wrap
        except Exception as exc:
            cls.logger().error(
                "Unexpected error during login",
                exc_info=True,
                extra={"email": email, "ip": request_ip},
            )
            raise InternalServerException(
                "Login failed due to an unexpected error."
            ) from exc
