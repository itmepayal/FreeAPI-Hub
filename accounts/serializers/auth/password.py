# =============================================================
# Django Password Validation
# =============================================================
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

# =============================================================
# Django REST Framework
# =============================================================
from rest_framework import serializers

# =============================================================
# Reset Password Serializer
# =============================================================
class ResetPasswordSerializer(serializers.Serializer):
    """
    Handles password reset using a reset token.
    """

    # ---------------------------------------------------------
    # Input Fields
    # ---------------------------------------------------------
    token = serializers.CharField(
        help_text="Password reset token"
    )

    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        help_text="New password to set",
    )

    confirm_password = serializers.CharField(
        write_only=True,
        help_text="Must match new_password",
    )

    # ---------------------------------------------------------
    # Object Validation
    # ---------------------------------------------------------
    def validate(self, data):
        """Validate password match and strength."""

        # Check password confirmation
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })

        # Run Django password validators
        try:
            validate_password(data["new_password"])
        except DjangoValidationError as e:
            raise serializers.ValidationError({
                "new_password": e.messages
            })

        # Remove confirmation field after validation
        data.pop("confirm_password")
        return data


# =============================================================
# Change Password Serializer
# =============================================================
class ChangePasswordSerializer(serializers.Serializer):
    """
    Handles password change for authenticated users.
    """

    # ---------------------------------------------------------
    # Input Fields
    # ---------------------------------------------------------
    old_password = serializers.CharField(
        write_only=True,
        help_text="Current account password",
    )

    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        help_text="New desired password",
    )

    confirm_password = serializers.CharField(
        write_only=True,
        help_text="Must match new_password",
    )

    # ---------------------------------------------------------
    # Object Validation
    # ---------------------------------------------------------
    def validate(self, attrs):
        """Validate authentication, old password, and new password rules."""

        request = self.context.get("request")

        # Ensure authentication
        if not request or not request.user or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")

        user = request.user

        # Verify old password
        if not user.check_password(attrs["old_password"]):
            raise serializers.ValidationError({
                "old_password": "Old password is incorrect."
            })

        # Confirm new password match
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })

        # Prevent password reuse
        if user.check_password(attrs["new_password"]):
            raise serializers.ValidationError({
                "new_password": "New password must be different from the old password."
            })

        # Run Django password validators
        try:
            validate_password(attrs["new_password"], user=user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({
                "new_password": e.messages
            })

        # Cleanup confirmation field
        attrs.pop("confirm_password")
        return attrs
