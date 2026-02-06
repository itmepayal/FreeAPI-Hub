# =============================================================
# Django REST Framework
# =============================================================
from rest_framework import serializers

# =============================================================
# Local Application Models
# =============================================================
from accounts.models import User, UserPresence, UserSecurity

# =============================================================
# User Presence Serializer
# =============================================================
class UserPresenceSerializer(serializers.ModelSerializer):
    """
    Exposes user real-time presence state.
    System-managed fields only.
    """

    class Meta:
        model = UserPresence
        fields = ["is_online", "last_seen", "status_message"]
        read_only_fields = fields


# =============================================================
# User Security Serializer
# =============================================================
class UserSecuritySerializer(serializers.ModelSerializer):
    """
    Exposes high-level security status flags.
    Sensitive configuration is intentionally hidden.
    """

    class Meta:
        model = UserSecurity
        fields = ["is_2fa_enabled"]
        read_only_fields = fields


# =============================================================
# User Serializer (Primary)
# =============================================================
class UserSerializer(serializers.ModelSerializer):
    """
    Primary serializer for user profile responses.

    Used In:
    - Profile APIs
    - Auth responses
    - Admin user views

    Excludes:
    - Passwords
    - Tokens
    - Sensitive security internals
    """

    # ---------------------------------------------------------
    # Computed Fields
    # ---------------------------------------------------------
    avatar_url = serializers.SerializerMethodField(
        help_text="Resolved absolute avatar URL",
    )

    # ---------------------------------------------------------
    # Nested Read-Only Relations
    # ---------------------------------------------------------
    presence = UserPresenceSerializer(read_only=True)
    security = UserSecuritySerializer(read_only=True)

    # ---------------------------------------------------------
    # Model Configuration
    # ---------------------------------------------------------
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
        read_only_fields = [
            "id",
            "avatar_url",
            "presence",
            "security",
        ]

    # ---------------------------------------------------------
    # Field Resolvers
    # ---------------------------------------------------------
    def get_avatar_url(self, obj):
        """
        Resolve avatar URL consistently.

        Behavior:
        - Returns uploaded avatar if present
        - Falls back to default avatar URL
        """
        return obj.avatar_url


# =============================================================
# Update Avatar Serializer
# =============================================================
class UpdateAvatarSerializer(serializers.Serializer):
    """
    Handles avatar image upload requests.
    """

    # ---------------------------------------------------------
    # Input Fields
    # ---------------------------------------------------------
    avatar = serializers.ImageField(
        required=True,
        help_text="Upload a new avatar image",
    )
