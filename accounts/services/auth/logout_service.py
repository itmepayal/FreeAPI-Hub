# =============================================================
# JWT
# =============================================================
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

# =============================================================
# Core Utilities & Exceptions
# =============================================================
from core.exceptions.base import (
    InvalidTokenException,
    InternalServerException,
    ServiceException,
)

# =============================================================
# Base Service
# =============================================================
from accounts.services.base import BaseService

# =============================================================
# Logout Service
# =============================================================
class LogoutService(BaseService):
    """
    Service layer for handling user logout via refresh token blacklisting.

    Responsibilities:
    1. Parse and validate the provided JWT refresh token.
    2. Ensure the token belongs to the authenticated user.
    3. Blacklist the token to prevent future use.
    4. Log all relevant actions for traceability.

    Design Notes:
    - Exceptions are classified and logged appropriately.
    - Service preserves consistent behavior with other auth services.
    """
    @classmethod
    def logout_user(cls, user, refresh_token: str) -> None:
        """
        Log out a user by blacklisting their refresh token.

        Args:
            user: Authenticated User instance.
            refresh_token (str): JWT refresh token to blacklist.

        Raises:
            InvalidTokenException: If token is invalid, expired, or does not belong to user.
            InternalServerException: If unexpected error occurs during logout.
        """
        try:
            # Parse & verify refresh token
            token = RefreshToken(refresh_token)

            # Ensure token belongs to user
            if str(token.payload.get("user_id")) != str(user.id):
                cls.logger().warning(
                    "Token user mismatch during logout",
                    extra={"user_id": user.id},
                )
                raise InvalidTokenException("Token does not belong to the user.")

            # Blacklist token
            token.blacklist()

            cls.logger().info(
                "User logged out successfully",
                extra={"user_id": user.id},
            )

        except TokenError as exc:
            cls.logger().warning(
                "Invalid or expired refresh token during logout",
                exc_info=True,
                extra={"user_id": user.id},
            )
            raise InvalidTokenException("Invalid or expired refresh token.") from exc

        except ServiceException:
            # Preserve already-classified service errors
            raise

        except Exception as exc:
            cls.logger().error(
                "Unexpected error during logout",
                exc_info=True,
                extra={"user_id": user.id},
            )
            raise InternalServerException(
                "Logout failed due to an unexpected error."
            ) from exc
