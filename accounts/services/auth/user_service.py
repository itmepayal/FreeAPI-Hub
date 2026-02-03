# =============================================================
# User Services
# =============================================================
from accounts.models import User
from accounts.serializers.auth import UserSerializer

# =============================================================
# Core Utilities
# =============================================================
from core.cloudinary.uploader import upload_to_cloudinary
from core.exceptions.base import ExternalServiceException, ServiceException

# =============================================================
# Base Service
# =============================================================
from accounts.services.base import BaseService


# =============================================================
# User Service
# =============================================================
class UserService(BaseService):
    """
    Service layer for user-related operations.

    Responsibilities:
    1. Fetch and serialize the current user's profile.
    2. Handle avatar updates via Cloudinary.
    3. Log all actions for traceability.
    4. Wrap external service failures in a consistent exception.
    """

    @classmethod
    def get_current_user_profile(cls, user: User) -> dict:
        """
        Retrieve the current user's profile as a serialized dictionary.

        Steps:
        1. Log the profile fetch attempt.
        2. Serialize the User object using UserSerializer.
        3. Return serialized data.

        Args:
            user (User): The currently authenticated user.

        Returns:
            dict: Serialized user profile.

        Raises:
            ServiceException: If any unexpected error occurs during serialization.
        """
        try:
            cls.logger().debug(
                "Fetching user profile",
                extra={"user_id": user.id, "email": user.email},
            )
            return UserSerializer(user).data

        except Exception as exc:
            cls.logger().error(
                "Failed to fetch user profile",
                exc_info=True,
                extra={"user_id": user.id, "email": user.email},
            )
            raise ServiceException("Could not fetch user profile.") from exc

    @classmethod
    def update_avatar(cls, user: User, avatar_file) -> str:
        """
        Update the user's avatar and return the new URL.

        Steps:
        1. Log the avatar upload attempt.
        2. Upload the file to Cloudinary.
        3. Update the User model with the new avatar URL.
        4. Log success and return the URL.

        Args:
            user (User): The user whose avatar is being updated.
            avatar_file: File object representing the new avatar.

        Returns:
            str: URL of the uploaded avatar.

        Raises:
            ExternalServiceException: If the avatar upload fails due to external service.
            ServiceException: For other unexpected errors.
        """
        try:
            cls.logger().info(
                "Uploading avatar",
                extra={"user_id": user.id, "email": user.email},
            )

            # Upload to Cloudinary
            result = upload_to_cloudinary(
                avatar_file,
                folder="avatars",
                use_filename=True,
                unique_filename=True,
                overwrite=True,
            )

            avatar_url = (
                result.get("secure_url")
                if isinstance(result, dict)
                else str(result)
            )

            # Update user record
            user.avatar = avatar_url
            user.save(update_fields=["avatar"])

            cls.logger().info(
                "Avatar updated successfully",
                extra={"user_id": user.id, "avatar_url": avatar_url},
            )

            return avatar_url

        except ServiceException:
            # Re-raise known service exceptions without modification
            raise

        except Exception as exc:
            cls.logger().error(
                "Avatar upload failed",
                exc_info=True,
                extra={"user_id": user.id, "email": user.email},
            )
            raise ExternalServiceException(
                "Failed to upload avatar. Please try again later."
            ) from exc
