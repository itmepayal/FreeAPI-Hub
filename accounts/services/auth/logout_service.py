# =============================================================
# JWT
# =============================================================
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
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
# Logout Service
# =============================================================
class LogoutService:
    """
    Handles user logout by blacklisting refresh tokens.
    """
    @staticmethod
    def logout_user(user, refresh_token: str):
        """
        Blacklist a refresh token to log out the user.

        Args:
            user: Authenticated User instance
            refresh_token (str): JWT refresh token to blacklist

        Raises:
            InvalidTokenException: If the token is invalid or expired
            InternalServerException: If unexpected error occurs during logout
        """
        try:
            # --------------------------
            # Parse & verify refresh token
            # --------------------------
            token = RefreshToken(refresh_token)

            # Ensure token belongs to this user
            if str(token.payload.get("user_id")) != str(user.id):
                logger.warning(f"User {user.email} tried to blacklist a token that doesn't belong to them.")
                raise InvalidTokenException("Token does not belong to the user.")

            # Blacklist the token
            token.blacklist()

            # Log successful logout
            logger.info(f"User logged out successfully: {user.email}")

        except TokenError as te:
            logger.error(f"Logout failed for {user.email}: {str(te)}")
            raise InvalidTokenException("Invalid or expired refresh token.") from te

        except Exception as e:
            logger.error(f"Unexpected error during logout for {user.email}: {str(e)}", exc_info=True)
            raise InternalServerException("Logout failed due to an unexpected error.") from e
