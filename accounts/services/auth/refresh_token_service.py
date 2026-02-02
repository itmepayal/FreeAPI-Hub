# =============================================================
# JWT
# =============================================================
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

# =============================================================
# Core Utilities & Exceptions
# =============================================================
from core.logging.logger import get_logger
from core.exception.base import InvalidTokenException, InternalServerException

# =============================================================
# Logger
# =============================================================
logger = get_logger(__name__)

# =============================================================
# RefreshToken Service
# =============================================================
class RefreshTokenService:
    """
    Handles refreshing JWT access tokens using refresh tokens.
    """

    @staticmethod
    def refresh_access_token(refresh_token: str) -> str:
        """
        Generate a new access token from a valid refresh token.

        Args:
            refresh_token (str): JWT refresh token

        Returns:
            str: New access token

        Raises:
            InvalidTokenException: If the refresh token is invalid or expired
            InternalServerException: For unexpected errors
        """
        try:
            # --------------------------
            # Parse & verify refresh token
            # --------------------------
            token = RefreshToken(refresh_token)

            # Generate new access token
            new_access_token = str(token.access_token)

            logger.info("Access token refreshed successfully")
            return new_access_token

        except TokenError as e:
            logger.warning(f"Invalid or expired refresh token: {str(e)}", exc_info=True)
            raise InvalidTokenException("Invalid or expired refresh token.") from e

        except Exception as e:
            logger.error(f"Unexpected error while refreshing access token: {str(e)}", exc_info=True)
            raise InternalServerException("Failed to refresh access token due to unexpected error.") from e
