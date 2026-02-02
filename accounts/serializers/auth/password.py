# =============================================================
# Django Imports
# =============================================================
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

# =============================================================
# Django REST Framework Imports
# =============================================================
from rest_framework import serializers

# =============================================================
# Password Management Serializers
# =============================================================
# These serializers handle password reset and change workflows.
# They enforce:
# - Django's password validation policies
# - old vs new password verification
# - confirm password matching
# =============================================================

# =============================================================
# Reset Password Serializer
# =============================================================
class ResetPasswordSerializer(serializers.Serializer):
    """
    Serializer for resetting a user's password using a token.

    Fields:
    - token: Required reset token (usually sent via email)
    - new_password: User-provided new password
    - confirm_password: Must match new_password
    """

    token = serializers.CharField(help_text="Password reset token")
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        help_text="New password to set"
    )
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        # Verify that new_password and confirm_password match
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })

        # Run Django's password validators
        try:
            validate_password(data["new_password"])
        except DjangoValidationError as e:
            raise serializers.ValidationError({
                "new_password": e.messages
            })

        # Remove confirm_password from validated data
        data.pop("confirm_password")
        return data

# =============================================================
# Change Password Serializer
# =============================================================
class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing password while logged in.

    Fields:
    - old_password: Current password
    - new_password: New desired password
    - confirm_password: Must match new_password

    Validations:
    - User must be authenticated
    - Old password must be correct
    - New password must differ from old password
    - Must pass Django's password validators
    """

    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        request = self.context.get("request")

        # Ensure user is authenticated
        if not request or not request.user or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")

        user = request.user

        # Verify old password
        if not user.check_password(attrs["old_password"]):
            raise serializers.ValidationError({
                "old_password": "Old password is incorrect."
            })

        # Verify new password matches confirmation
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })

        # Prevent reusing old password
        if user.check_password(attrs["new_password"]):
            raise serializers.ValidationError({
                "new_password": "New password must be different from the old password."
            })

        # Validate new password with Django validators
        try:
            validate_password(attrs["new_password"], user=user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({
                "new_password": e.messages
            })

        # Cleanup
        attrs.pop("confirm_password")
        return attrs
