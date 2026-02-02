# =============================================================
# Django REST Framework Imports
# =============================================================
from rest_framework import serializers

# =============================================================
# Local Application Imports
# =============================================================
from accounts.models import User, UserPresence, UserSecurity

# =============================================================
# Nested Serializers for Related Models
# =============================================================
# These serializers expose read-only user-related metadata.
# They live in separate tables to keep the main User model lean.
# Nested serialization avoids redundant queries and improves clarity.
# =============================================================

class UserPresenceSerializer(serializers.ModelSerializer):
    """
    Serializer for user's real-time presence information.

    - Fields are managed by the system (not user-editable)
    - Exposed as read-only
    """

    class Meta:
        model = UserPresence
        fields = ["is_online", "last_seen", "status_message"]
        read_only_fields = fields


class UserSecuritySerializer(serializers.ModelSerializer):
    """
    Serializer for user security-related flags.

    - Only exposes high-level security state (e.g., 2FA enabled)
    - Sensitive configuration details are not exposed
    """

    class Meta:
        model = UserSecurity
        fields = ["is_2fa_enabled"]
        read_only_fields = fields


# =============================================================
# User Serializer (Main)
# =============================================================
# Primary serializer for returning user profile data.
# Used across the application in:
# - Profile endpoints
# - Authentication responses
# - Admin user management
#
# Notes:
# - Sensitive fields (password, tokens, etc.) are excluded
# - Related models (presence, security) are nested and read-only
# - Computed fields (avatar_url) provide safe URLs for frontend
# =============================================================

class UserSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField(
        help_text="Resolved absolute URL to the user's avatar image"
    )

    # Nested, read-only related data
    presence = UserPresenceSerializer(read_only=True)
    security = UserSecuritySerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "role",
            "is_verified",
            "avatar_url",
            "presence",
            "security",
        ]
        read_only_fields = ["id", "avatar_url", "presence", "security"]

    def get_avatar_url(self, obj):
        """
        Returns the absolute URL for the user's avatar.

        Logic:
        - Returns uploaded avatar if present
        - Falls back to a default UI avatar if none exists

        Keeping this in the model/serializer ensures consistency
        across all API responses and frontend clients.
        """
        return obj.avatar_url


# =============================================================
# Serializer for Updating Avatar
# =============================================================
class UpdateAvatarSerializer(serializers.Serializer):
    """
    Serializer to update user avatar.
    Accepts:
    - avatar: file upload (image)
    """
    avatar = serializers.ImageField(
        required=True,
        help_text="Upload a new avatar image."
    )