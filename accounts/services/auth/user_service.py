# =============================================================
# Local App Services
# =============================================================
from accounts.models import User
from accounts.serializers.auth import UserSerializer

# =============================================================
# Core Utilities
# =============================================================
from core.cloudinary.uploader import upload_to_cloudinary
from core.logging.logger import get_logger
from core.exception.base import ExternalServiceException

# =============================================================
# Logger
# =============================================================
logger = get_logger(__name__)

# =============================================================
# User Services
# =============================================================
class UserService:
    """
    Handles user-related business logic.
    """

    @staticmethod
    def get_current_user_profile(user) -> dict:
        """
        Return serialized profile data for current user.
        """
        return UserSerializer(user).data

    @staticmethod
    def update_avatar(user: User, avatar_file) -> str:
        """
        Update user's avatar and return the new avatar URL.

        Raises:
            ExternalServiceException: If avatar upload fails
        """
        try:
            # Upload avatar to Cloudinary
            result = upload_to_cloudinary(
                avatar_file,
                folder="avatars",
                use_filename=True,
                unique_filename=True,
                overwrite=True,
            )

            # Extract secure URL safely
            avatar_url = (
                result.get("secure_url")
                if isinstance(result, dict)
                else str(result)
            )

            # Persist avatar URL
            user.avatar = avatar_url
            user.save(update_fields=["avatar"])

            logger.info(
                "Avatar updated successfully",
                extra={"user_id": user.id, "email": user.email},
            )

            return avatar_url

        except Exception as e:
            logger.error(
                "Avatar upload failed",
                extra={"user_id": user.id, "email": user.email},
                exc_info=True,
            )
            raise ExternalServiceException(
                "Failed to upload avatar. Please try again later."
            ) from e
