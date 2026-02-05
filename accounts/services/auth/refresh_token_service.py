# =============================================================
# JWT
# =============================================================
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

# =============================================================
# Core Exceptions
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
# Refresh Token Service
# =============================================================
class RefreshTokenService(BaseService):

    @classmethod
    def refresh_access_token(cls, refresh_token: str) -> str:
        try:

            # Step 1 — Parse and validate refresh token
            token = RefreshToken(refresh_token)

            # Step 2 — Generate new access token
            new_access_token = str(token.access_token)

            # Step 3 — Log successful token refresh
            cls.logger().info(
                "Access token refreshed successfully"
            )

            # Step 4 — Return new access token
            return new_access_token

        # Step 5 — Handle invalid or expired token
        except TokenError as exc:
            cls.logger().warning(
                "Invalid or expired refresh token",
                exc_info=True,
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
                "Unexpected error while refreshing token",
                exc_info=True,
            )
            raise InternalServerException(
                "Failed to refresh access token due to unexpected error."
            ) from exc
