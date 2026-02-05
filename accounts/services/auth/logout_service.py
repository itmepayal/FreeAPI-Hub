# =============================================================
# JWT
# =============================================================
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

# =============================================================
# Core Utilities & Exceptions
# =============================================================
from core.exceptions import (
    InvalidTokenException,
    InternalServerException,
    ServiceException,
)

# =============================================================
# Base Service
# =============================================================
from accounts.services import BaseService


# =============================================================
# Logout Service
# =============================================================
class LogoutService(BaseService):

    @classmethod
    def logout_user(cls, user, refresh_token: str) -> None:
        try:

            # Step 1 — Parse refresh token
            token = RefreshToken(refresh_token)

            # Step 2 — Validate token ownership
            token_user_id = str(token.payload.get("user_id"))

            if token_user_id != str(user.id):
                cls.logger().warning(
                    "Token user mismatch during logout",
                    extra={"user_id": user.id},
                )
                raise InvalidTokenException(
                    "Token does not belong to the user."
                )

            # Step 3 — Blacklist refresh token
            token.blacklist()

            # Step 4 — Log successful logout
            cls.logger().info(
                "User logged out successfully",
                extra={"user_id": user.id},
            )

        # Step 5 — Handle invalid token errors
        except TokenError as exc:
            cls.logger().warning(
                "Invalid or expired refresh token during logout",
                exc_info=True,
                extra={"user_id": user.id},
            )
            raise InvalidTokenException(
                "Invalid or expired refresh token."
            ) from exc

        # Step 6 — Re-raise known service exceptions
        except ServiceException:
            raise

        # Step 7 — Handle unexpected failures
        except Exception as exc:
            cls.logger().error(
                "Unexpected error during logout",
                exc_info=True,
                extra={"user_id": user.id},
            )
            raise InternalServerException(
                "Logout failed due to an unexpected error."
            ) from exc
