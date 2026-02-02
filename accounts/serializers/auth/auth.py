# =============================================================
# Django Imports
# =============================================================
from django.contrib.auth.password_validation import validate_password

# =============================================================
# Django REST Framework Imports
# =============================================================
from rest_framework import serializers

# =============================================================
# Local Application Imports
# =============================================================
from accounts.models import User, UserSecurity

# =============================================================
# Registration Serializers
# =============================================================

class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer responsible for user registration.

    - Validates password using Django's built-in validators
    - Hashes password before saving
    - Creates a new User instance
    """
    password = serializers.CharField(
        write_only=True,
        min_length=6,
        help_text="User password (will be hashed before saving)"
    )

    class Meta:
        model = User
        fields = ["email", "username", "password"]

    def validate_password(self, value):
        """
        Validate password strength using Django's password validators.
        """
        try:
            validate_password(value)
        except Exception as e:
            raise serializers.ValidationError(str(e))
        return value

    def create(self, validated_data):
        """
        Create and return a new user with a hashed password.
        """
        user = User(
            email=validated_data["email"].lower(),
            username=validated_data.get("username"),
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


# =============================================================
# Email Verification Serializer
# =============================================================

class VerifyEmailSerializer(serializers.Serializer):
    """
    Serializer used to verify a user's email address via token.
    """
    token = serializers.CharField(help_text="Email verification token")


# =============================================================
# Login & Session Serializers
# =============================================================

class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login using email and password.
    """
    email = serializers.EmailField(help_text="Registered user email")
    password = serializers.CharField(
        write_only=True,
        help_text="User password"
    )


class RefreshTokenSerializer(serializers.Serializer):
    """
    Serializer used to refresh or revoke authentication tokens.
    """
    refresh_token = serializers.CharField(
        help_text="Refresh token used for logout or token rotation"
    )


# =============================================================
# Password Recovery Serializers
# =============================================================

class ForgotPasswordSerializer(serializers.Serializer):
    """
    Serializer to initiate the forgot-password flow.
    """
    email = serializers.EmailField(
        help_text="Registered email to send reset password link"
    )

# =============================================================
# Resend Email Verification Serializer
# =============================================================

class ResendEmailSerializer(serializers.Serializer):
    """
    Serializer to resend email verification link
    for users who have not verified their email.
    """
    email = serializers.EmailField(
        help_text="Email address to resend verification link"
    )

    def validate_email(self, value):
        """
        Ensure the user exists and email is not already verified.
        """
        try:
            security = UserSecurity.objects.select_related("user").get(
                user__email=value
            )
        except UserSecurity.DoesNotExist:
            raise serializers.ValidationError(
                "No account found with this email."
            )

        if security.user.is_verified:
            raise serializers.ValidationError(
                "Email is already verified."
            )

        # Store validated objects in serializer context
        self.context["user"] = security.user
        self.context["security"] = security
        return value

    def validate(self, attrs):
        """
        Attach resolved user and security objects
        to validated data for downstream use.
        """
        attrs["user"] = self.context["user"]
        attrs["security"] = self.context["security"]
        return attrs
