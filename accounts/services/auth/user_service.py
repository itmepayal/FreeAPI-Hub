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

    @classmethod
    def get_current_user_profile(cls, user: User) -> dict:
        try:
            # Step 1 — Log profile fetch attempt for traceability
            cls.logger().debug(
                "Fetching user profile",
                extra={
                    "user_id": user.id,
                    "email": user.email
                },
            )

            # Step 2 — Serialize user model into API-safe dict
            data = UserSerializer(user).data

            # Step 3 — Return serialized profile data
            return data

        except Exception as exc:
            # Step 4 — Log failure with full stack trace
            cls.logger().error(
                "Failed to fetch user profile",
                exc_info=True,
                extra={
                    "user_id": user.id,
                    "email": user.email
                },
            )

            # Step 5 — Raise controlled service-layer exception
            raise ServiceException(
                "Could not fetch user profile."
            ) from exc

    # =========================================================
    # Avatar Update Service
    # =========================================================
    @classmethod
    def update_avatar(cls, user: User, avatar_file) -> str:
        try:
            # Step 1 — Log avatar upload request
            cls.logger().info(
                "Uploading avatar",
                extra={
                    "user_id": user.id,
                    "email": user.email
                },
            )

            # Step 2 — Upload avatar file to Cloudinary storage
            result = upload_to_cloudinary(
                avatar_file,
                folder="avatars",
                use_filename=True,
                unique_filename=True,
                overwrite=True,
            )

            # Step 3 — Normalize uploader response to URL string
            avatar_url = (
                result.get("secure_url")
                if isinstance(result, dict)
                else str(result)
            )

            # Step 4 — Update avatar field in database
            user.avatar = avatar_url
            user.save(update_fields=["avatar"])

            # Step 5 — Log successful avatar update
            cls.logger().info(
                "Avatar updated successfully",
                extra={
                    "user_id": user.id,
                    "avatar_url": avatar_url
                },
            )

            # Step 6 — Return avatar URL to caller
            return avatar_url

        except ServiceException:
            # Step 7 — Re-raise known service exceptions unchanged
            raise

        except Exception as exc:
            # Step 8 — Log unexpected external/upload failure
            cls.logger().error(
                "Avatar upload failed",
                exc_info=True,
                extra={
                    "user_id": user.id,
                    "email": user.email
                },
            )

            # Step 9 — Convert to external service exception
            raise ExternalServiceException(
                "Failed to upload avatar. Please try again later."
            ) from exc
