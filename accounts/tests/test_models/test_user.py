import pytest
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from accounts.models import User
from accounts.tests.factories.user_factory import UserFactory
from core.constants import ROLE_USER, ROLE_SUPERADMIN

@pytest.mark.django_db
class TestUserModel:

    # ============================================================
    # Creation & Default Values
    # ============================================================

    # Ensure a user created via factory has correct default values
    def test_user_creation_defaults(self):
        user = UserFactory()

        assert user.email is not None
        assert user.username is not None
        assert user.role == ROLE_USER
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False
        assert isinstance(user.is_verified, bool)

    # Validate default boolean flags on user creation
    def test_default_flags(self):
        user = UserFactory()
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser

    # Check that normal users get ROLE_USER by default
    def test_role_default_applied(self):
        user = User.objects.create_user(
            email="r@test.com",
            username="r",
            password="x"
        )
        assert user.role == ROLE_USER

    # Superusers must always have ROLE_SUPERADMIN
    def test_superuser_role_is_superadmin(self):
        user = User.objects.create_superuser(
            email="admin@test.com",
            username="admin",
            password="x"
        )
        assert user.role == ROLE_SUPERADMIN


    # ============================================================
    # String Representation
    # ============================================================

    # __str__ should return email for readability
    def test_user_str_representation(self):
        user = UserFactory()
        assert str(user) == user.email

    # __str__ should safely handle empty email
    def test_str_with_missing_email(self):
        user = User(email="", username="x")
        assert str(user) == ""


    # ============================================================
    # Manager Methods
    # ============================================================

    # Verify create_user sets correct flags and password
    def test_user_manager_create_user(self):
        user = User.objects.create_user(
            email="new@example.com",
            username="newuser",
            password="testpass123"
        )
        assert user.check_password("testpass123")
        assert user.is_active is True
        assert user.is_staff is False

    # Verify create_superuser enforces admin privileges
    def test_user_manager_create_superuser(self):
        user = User.objects.create_superuser(
            email="admin@example.com",
            username="admin",
            password="adminpass123"
        )
        assert user.is_superuser is True
        assert user.is_staff is True

    # Custom manager method should return only active users
    def test_manager_active_queryset(self):
        active_user = UserFactory(is_active=True)
        inactive_user = UserFactory(is_active=False)

        qs = User.objects.active()

        assert active_user in qs
        assert inactive_user not in qs

    # create_superuser must fail if required flags are incorrect
    def test_create_superuser_requires_flags(self):
        with pytest.raises(ValueError):
            User.objects.create_superuser(
                email="bad@admin.com",
                username="bad",
                password="x",
                is_staff=False
            )

    # Email is mandatory when creating a user
    def test_create_user_without_email_fails(self):
        with pytest.raises(ValueError):
            User.objects.create_user(
                email="",
                username="x",
                password="x"
            )

    # Username is mandatory when creating a user
    def test_create_user_without_username_fails(self):
        with pytest.raises(ValueError):
            User.objects.create_user(
                email="a@test.com",
                username="",
                password="x"
            )

    # Password can be optional, but must be unusable if missing
    def test_create_user_without_password(self):
        user = User.objects.create_user(
            email="nopass@test.com",
            username="nopass"
        )
        assert not user.has_usable_password()

    # Emails should be normalized (domain lowercased)
    def test_email_normalized(self):
        user = User.objects.create_user(
            email="Test@Example.COM",
            username="x",
            password="x"
        )
        assert user.email == "Test@example.com"


    # ============================================================
    # Password Behavior
    # ============================================================

    # Factory should hash passwords automatically
    def test_factory_password_is_hashed(self):
        user = UserFactory(password="Secret123!")
        assert user.check_password("Secret123!")

    # Raw password must never be stored directly
    def test_password_not_stored_raw(self):
        user = UserFactory(password="Plain123!")
        assert user.password != "Plain123!"


    # ============================================================
    # Constraints & Validation
    # ============================================================

    # Email must be unique at database level
    def test_unique_email_constraint(self):
        user = UserFactory()
        with pytest.raises(IntegrityError):
            User.objects.create(
                email=user.email,
                username="other"
            )

    # Invalid role values must be rejected
    def test_invalid_role_rejected(self):
        user = User(email="x@test.com", username="x", role="INVALID")
        with pytest.raises(ValidationError):
            user.full_clean()

    # Username length should respect model constraints
    def test_username_max_length_validation(self):
        user = User(email="a@test.com", username="x" * 151)
        with pytest.raises(ValidationError):
            user.full_clean()

    # Email format must be valid
    def test_model_validation_invalid_email(self):
        user = User(email="not-an-email", username="x")
        with pytest.raises(ValidationError):
            user.full_clean()

    # Username is required at model validation level
    def test_model_validation_requires_username(self):
        user = User(email="x@test.com")
        with pytest.raises(ValidationError):
            user.full_clean()


    # ============================================================
    # Avatar URL Property
    # ============================================================

    # Custom avatar URL should be returned as-is
    def test_avatar_url_with_custom_avatar(self):
        user = UserFactory(avatar="https://example.com/avatar.jpg")
        assert user.avatar_url == user.avatar

    # Default avatar should be generated when avatar is missing
    def test_avatar_url_without_custom_avatar(self):
        user = UserFactory(username="John Doe", avatar=None)

        assert "ui-avatars.com" in user.avatar_url
        assert "John%20Doe" in user.avatar_url

    # Avatar generation should be safe with no email or username
    def test_avatar_safe_when_no_email_and_username(self):
        user = User(username=None, email=None)
        assert "ui-avatars.com" in user.avatar_url

    # Email prefix should be used when username is empty
    def test_avatar_uses_email_when_no_username(self):
        user = UserFactory(username="", avatar=None)
        assert user.email.split("@")[0] in user.avatar_url

    # Email prefix should also be used when username is None
    def test_avatar_username_none_uses_email_prefix(self):
        user = UserFactory(username=None, avatar=None)
        assert user.email.split("@")[0] in user.avatar_url

    # Non-http avatar URLs should fall back to default avatar
    def test_avatar_non_http_falls_back(self):
        user = UserFactory(avatar="file://avatar.png")
        assert "ui-avatars.com" in user.avatar_url

    # Only http/https URLs are allowed as avatar sources
    def test_avatar_url_accepts_http_and_https(self):
        user1 = UserFactory(avatar="http://cdn.site/img.png")
        user2 = UserFactory(avatar="https://cdn.site/img.png")

        assert user1.avatar_url.startswith("http://")
        assert user2.avatar_url.startswith("https://")

    # Special characters in usernames must be URL encoded
    def test_avatar_special_characters_encoded(self):
        user = UserFactory(username="John+Doe")
        assert "John%2BDoe" in user.avatar_url


    # ============================================================
    # Flags & Toggles
    # ============================================================

    # User deactivation should persist correctly
    def test_user_deactivation(self):
        user = UserFactory(is_active=False)
        assert user.is_active is False

    # Verification flag should toggle and save correctly
    def test_user_verification_toggle(self):
        user = UserFactory(is_verified=False)

        user.is_verified = True
        user.save()

        assert user.is_verified is True

    # Normal users should never be superusers by default
    def test_user_not_superuser_by_default(self):
        user = UserFactory()
        assert not user.is_superuser


    # ============================================================
    # PermissionsMixin
    # ============================================================

    # New users should not have any permissions or groups
    def test_user_has_no_permissions_by_default(self):
        user = UserFactory()
        assert user.groups.count() == 0
        assert user.user_permissions.count() == 0


    # ============================================================
    # Model Metadata
    # ============================================================

    # Validate authentication-related model settings
    def test_required_fields(self):
        assert User.USERNAME_FIELD == "email"
        assert "username" in User.REQUIRED_FIELDS

    # Email field should be indexed for performance
    def test_email_is_indexed(self):
        field = User._meta.get_field("email")
        assert field.db_index is True

    # Role field should be indexed for filtering
    def test_role_is_indexed(self):
        field = User._meta.get_field("role")
        assert field.db_index is True

    # Base model timestamps must exist
    def test_base_model_fields_exist(self):
        user = UserFactory()
        assert user.created_at is not None
        assert user.updated_at is not None
