from urllib.parse import quote

from django.conf import settings
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers

from accounts.models import User, UserPresence, UserSecurity

from core.constants.roles import ROLE_CHOICES

# ----------------------------
# Nested Serializers for Related Models
# ----------------------------
class UserPresenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPresence
        fields = ["is_online", "last_seen", "status_message"]
        read_only_fields = ["is_online", "last_seen", "status_message"]

class UserSecuritySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSecurity
        fields = ["is_2fa_enabled"]
        read_only_fields = ["is_2fa_enabled"]

# ----------------------------
# User Serializer (Main)
# ----------------------------
class UserSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField(help_text="Full URL to user's avatar")
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
        """Return full URL for avatar or fallback to UI Avatar."""
        return obj.avatar_url  
    
# ----------------------------
# Register Serializer
# ----------------------------
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["email", "username", "password"]
        
    def validate_password(self, value):
        """
        Use Django's built-in password validators to validate the password.
        """
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.message)
        return value

    def create(self, validated_data):
        """Create a new user with hashed password."""
        user = User(
            email=validated_data["email"].lower(),
            username=validated_data.get("username")
        )
        user.set_password(validated_data["password"])
        user.save()
        return user

# ----------------------------
# Verify Email Serializer
# ----------------------------
class VerifyEmailSerializer(serializers.Serializer):
    token = serializers.CharField(help_text="Email verification token")

# ----------------------------
# Login Serializer
# ----------------------------
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(help_text="User email for login")
    password = serializers.CharField(write_only=True, help_text="User password")

# ----------------------------
# Logout Serializer
# ----------------------------
class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(help_text="User refresh token for logout")
    
# ----------------------------
# Forgot Password Serializer
# ----------------------------
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(help_text="Email to send reset password link")

# ----------------------------
# Reset Password Serializer
# ----------------------------
class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(help_text="Password reset token")
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        help_text="New password to set"
    )
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")

        if new_password != confirm_password:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })

        try:
            validate_password(new_password)
        except serializers.ValidationError as e:
            raise serializers.ValidationError({
                "new_password": e.messages
            })

        data.pop("confirm_password")

        return data

# ----------------------------
# Change Password Serializer
# ----------------------------
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        request = self.context.get("request")

        if not request or not request.user or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")

        user = request.user

        if not user.check_password(attrs["old_password"]):
            raise serializers.ValidationError({
                "old_password": "Old password is incorrect."
            })

        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })

        if user.check_password(attrs["new_password"]):
            raise serializers.ValidationError({
                "new_password": "New password must be different from the old password."
            })

        validate_password(attrs["new_password"], user=user)

        attrs.pop("confirm_password")
        return attrs

# ----------------------------
# Resend Email Verification Serializer
# ----------------------------
class ResendEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(help_text="Email to resend verification")

    def validate_email(self, value):
        try:
            security = UserSecurity.objects.select_related("user").get(user__email=value)
        except UserSecurity.DoesNotExist:
            raise serializers.ValidationError("No account found with this email.")

        if security.user.is_verified:
            raise serializers.ValidationError("Email is already verified.")

        self.context["user"] = security.user
        self.context["security"] = security  
        return value

    def validate(self, attrs):
        attrs["user"] = self.context["user"]
        attrs["security"] = self.context.get("security")
        return attrs

# ----------------------------
# Avatar Serializer
# ----------------------------
class UpdateAvatarSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=True, allow_null=False, help_text="Upload new avatar image")
    
    class Meta:
        model = User
        fields = ["avatar"]

# ----------------------------
# Role Serializer
# ----------------------------
class ChangeRoleSerializer(serializers.Serializer):
    user_id = serializers.UUIDField(required=True, help_text="User ID to change role")
    role = serializers.ChoiceField(choices=ROLE_CHOICES, required=True, help_text="New role")

# ----------------------------
# OAuth Callback
# ----------------------------
class OAuthCallbackSerializer(serializers.Serializer):
    code = serializers.CharField(required=True, help_text="OAuth authorization code")

# ----------------------------
# Enable 2FA Serializer
# ----------------------------
class Enable2FASerializer(serializers.Serializer):
    token = serializers.CharField(
        required=True,
        write_only=True,
        help_text="TOTP token generated by authenticator app to enable 2FA",
    )

# ----------------------------
# Disable 2FA Serializer
# ----------------------------
class Disable2FASerializer(serializers.Serializer):
    token = serializers.CharField(
        required=True,
        write_only=True,
        help_text="TOTP token to confirm disabling 2FA",
    )

# ----------------------------
# Setup 2FA Serializer
# ----------------------------
class Setup2FASerializer(serializers.Serializer):
    totp_uri = serializers.CharField(read_only=True, help_text="TOTP URI for authenticator app")
    qr_code = serializers.CharField(read_only=True, help_text="Base64 QR code for scanning")