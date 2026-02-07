# =============================================================
# Django Password Validation
# =============================================================
from django.contrib.auth.password_validation import validate_password

# =============================================================
# Django REST Framework
# =============================================================
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

# =============================================================
# Local Application Models
# =============================================================
from accounts.models import User, UserSecurity

# =============================================================
# User Registration Serializer
# =============================================================
class RegisterSerializer(serializers.ModelSerializer):
    """
    Handles new user registration.

    Responsibilities:
    - Validates password using Django validators
    - Normalizes email
    - Hashes password before persistence
    - Creates User instance
    """

    # ---------------------------------------------------------
    # Input Fields
    # ---------------------------------------------------------
    email = serializers.EmailField(
        required=True,
        help_text="Enter a valid email address",
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="Email is already registered."
            )
        ],
    )

    username = serializers.CharField(
        required=True,
        help_text="Choose a unique username",
    )

    password = serializers.CharField(
        write_only=True,
        min_length=6,
        help_text="User password (stored as hash)",
    )

    # ---------------------------------------------------------
    # Model Configuration
    # ---------------------------------------------------------
    class Meta:
        model = User
        fields = ["email", "username", "password"]

    # ---------------------------------------------------------
    # Field Validators
    # ---------------------------------------------------------
    def validate_email(self, value):
        return value.strip().lower()
    
    def validate_password(self, value):
        """Validate password strength using Django validators."""
        try:
            validate_password(value)
        except Exception as e:
            raise serializers.ValidationError(e.messages)
        return value

    # ---------------------------------------------------------
    # Create Logic
    # ---------------------------------------------------------
    def create(self, validated_data):
        """Create user with normalized email and hashed password."""
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
    Validates email verification token.
    Used in email activation flow.
    """

    token = serializers.CharField(
        help_text="Email verification token"
    )


# =============================================================
# Authentication Serializers
# =============================================================
class LoginSerializer(serializers.Serializer):
    """
    Handles credential validation for login.
    """

    email = serializers.EmailField(
        help_text="Registered user email"
    )

    password = serializers.CharField(
        write_only=True,
        help_text="User password",
    )


# =============================================================
# Token Refresh / Logout Serializer
# =============================================================
class RefreshTokenSerializer(serializers.Serializer):
    """
    Used for refresh-token rotation or logout invalidation.
    """

    refresh_token = serializers.CharField(
        help_text="Refresh token string"
    )


# =============================================================
# Password Recovery Serializer
# =============================================================
class ForgotPasswordSerializer(serializers.Serializer):
    """
    Initiates forgot-password workflow.
    """

    email = serializers.EmailField(
        help_text="Registered email address"
    )


# =============================================================
# Resend Email Verification Serializer
# =============================================================
class ResendEmailSerializer(serializers.Serializer):
    """
    Handles resend verification email requests.
    Ensures:
    - User exists
    - Email is not already verified
    """

    # ---------------------------------------------------------
    # Input Field
    # ---------------------------------------------------------
    email = serializers.EmailField(
        help_text="Email to resend verification link"
    )

    # ---------------------------------------------------------
    # Field Validation
    # ---------------------------------------------------------
    def validate_email(self, value):
        """Validate user existence and verification status."""
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

        self.context["user"] = security.user
        self.context["security"] = security
        return value

    # ---------------------------------------------------------
    # Object Validation
    # ---------------------------------------------------------
    def validate(self, attrs):
        """Attach resolved objects for downstream service use."""
        attrs["user"] = self.context["user"]
        attrs["security"] = self.context["security"]
        return attrs
