# =============================================================
# Django REST Framework
# =============================================================
from rest_framework import serializers


# =============================================================
# TOTP Token Validation Mixin
# =============================================================
class TOTPTokenValidationMixin:
    """
    Shared validator for TOTP tokens.

    Rules:
    - Must contain only digits
    - Must be exactly 6 characters
    """

    # ---------------------------------------------------------
    # Token Field Validator
    # ---------------------------------------------------------
    def validate_token(self, value):
        value = value.strip()

        if not value.isdigit():
            raise serializers.ValidationError(
                "Token must contain only digits."
            )

        if len(value) != 6:
            raise serializers.ValidationError(
                "Token must be a 6-digit code."
            )

        return value


# =============================================================
# Enable 2FA Serializer
# =============================================================
class Enable2FASerializer(TOTPTokenValidationMixin, serializers.Serializer):
    """
    Enables two-factor authentication for authenticated users.
    """

    # ---------------------------------------------------------
    # Input Fields
    # ---------------------------------------------------------
    token = serializers.CharField(
        write_only=True,
        help_text="6-digit TOTP token from authenticator app",
    )

    # ---------------------------------------------------------
    # Object Validation
    # ---------------------------------------------------------
    def validate(self, attrs):
        """Ensure request user is authenticated."""
        request = self.context.get("request")

        if not request or not request.user or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")

        return attrs


# =============================================================
# Disable 2FA Serializer
# =============================================================
class Disable2FASerializer(TOTPTokenValidationMixin, serializers.Serializer):
    """
    Disables two-factor authentication for authenticated users.
    """

    # ---------------------------------------------------------
    # Input Fields
    # ---------------------------------------------------------
    token = serializers.CharField(
        write_only=True,
        help_text="6-digit TOTP token to confirm disable action",
    )

    # ---------------------------------------------------------
    # Object Validation
    # ---------------------------------------------------------
    def validate(self, attrs):
        """Ensure request user is authenticated."""
        request = self.context.get("request")

        if not request or not request.user or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")

        return attrs


# =============================================================
# Verify 2FA Serializer
# =============================================================
class Verify2FASerializer(TOTPTokenValidationMixin, serializers.Serializer):
    """
    Verifies a TOTP code during login or sensitive operations.
    """

    # ---------------------------------------------------------
    # Input Fields
    # ---------------------------------------------------------
    token = serializers.CharField(
        write_only=True,
        help_text="6-digit TOTP code from authenticator app",
    )
