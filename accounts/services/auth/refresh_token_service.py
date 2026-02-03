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
# RefreshToken Service
# =============================================================
class RefreshTokenService(BaseService):
    """
    Service layer for handling JWT refresh token operations.

    Responsibilities:
    1. Validate a given refresh token.
    2. Generate a new access token based on the valid refresh token.
    3. Log all relevant actions for traceability.

    Design Notes:
    - Exceptions are categorized and logged at appropriate levels.
    - Preserves consistent behavior with other auth service classes.
    """
    @classmethod
    def refresh_access_token(cls, refresh_token: str) -> str:
        """
        Generate a new access token from a valid refresh token.

        Steps:
        1. Parse and validate the provided refresh token.
        2. Create a new access token.
        3. Log success or handle errors.

        Args:
            refresh_token (str): JWT refresh token

        Returns:
            str: New access token

        Raises:
            InvalidTokenException: If the refresh token is invalid or expired
            InternalServerException: If an unexpected error occurs
        """
        try:
            # 1. Parse & validate refresh token
            token = RefreshToken(refresh_token)

            # 2. Generate new access token
            new_access_token = str(token.access_token)

            # 3. Log successful refresh
            cls.logger().info(
                "Access token refreshed successfully",
            )

            return new_access_token

        except TokenError as exc:
            cls.logger().warning(
                "Invalid or expired refresh token",
                exc_info=True,
            )
            raise InvalidTokenException("Invalid or expired refresh token.") from exc

        except ServiceException:
            # Preserve already-classified service errors
            raise

        except Exception as exc:
            cls.logger().error(
                "Unexpected error while refreshing access token",
                exc_info=True,
            )
            raise InternalServerException(
                "Failed to refresh access token due to unexpected error."
            ) from exc
