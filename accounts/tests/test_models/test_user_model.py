import pytest
from django.db import IntegrityError
from urllib.parse import quote

from accounts.models import User
from core.constants import ROLE_USER


# ======================================================
# Test Constants
# ======================================================

TEST_EMAIL = "user@test.com"
TEST_USERNAME = "testuser"
TEST_PASSWORD = "StrongPass123"

ADMIN_EMAIL = "admin@test.com"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "AdminPass123"

DUPLICATE_EMAIL = "duplicate@test.com"

CUSTOM_AVATAR_URL = "https://cdn.com/a.png"
EMAIL_WITH_PREFIX = "john.doe@test.com"


# ======================================================
# User Creation Tests
# ======================================================

@pytest.mark.django_db
def test_create_user_success():
    user = User.objects.create_user(
        email=TEST_EMAIL,
        username=TEST_USERNAME,
        password=TEST_PASSWORD
    )

    assert user.email == TEST_EMAIL
    assert user.username == TEST_USERNAME
    assert user.check_password(TEST_PASSWORD)
    assert user.is_active is True
    assert user.role == ROLE_USER


@pytest.mark.django_db
def test_create_user_missing_username():
    with pytest.raises(ValueError):
        User.objects.create_user(
            email="nouser@test.com",
            username="",
            password="pass"
        )


# ======================================================
# Superuser Tests
# ======================================================

@pytest.mark.django_db
def test_create_superuser_success():
    admin = User.objects.create_superuser(
        email=ADMIN_EMAIL,
        username=ADMIN_USERNAME,
        password=ADMIN_PASSWORD
    )

    assert admin.is_staff is True
    assert admin.is_superuser is True
    assert admin.is_active is True


# ======================================================
# Default Field Tests
# ======================================================

@pytest.mark.django_db
def test_user_default_flags():
    user = User.objects.create_user(
        email="flags@test.com",
        username="flaguser",
        password="Password@123"
    )

    assert user.is_active is True
    assert user.is_verified is False
    assert user.is_staff is False
    assert user.is_superuser is False


# ======================================================
# Unique Constraint Tests
# ======================================================

@pytest.mark.django_db
def test_email_must_be_unique():
    User.objects.create_user(
        email=DUPLICATE_EMAIL,
        username="u1",
        password="pass"
    )

    with pytest.raises(IntegrityError):
        User.objects.create_user(
            email=DUPLICATE_EMAIL,
            username="u2",
            password="pass"
        )


# ======================================================
# __str__ Method Test
# ======================================================

@pytest.mark.django_db
def test_user_str_returns_email():
    user = User.objects.create_user(
        email="str@test.com",
        username="struser",
        password="pass"
    )

    assert str(user) == "str@test.com"


# ======================================================
# avatar_url Property Tests
# ======================================================

@pytest.mark.django_db
def test_avatar_returns_custom_url():
    user = User.objects.create_user(
        email=TEST_EMAIL,
        username=TEST_USERNAME,
        password=TEST_PASSWORD
    )

    user.avatar = CUSTOM_AVATAR_URL

    assert user.avatar_url == CUSTOM_AVATAR_URL


@pytest.mark.django_db
def test_avatar_generated_from_username():
    user = User.objects.create_user(
        email="name@test.com",
        username="avatarname",
        password="pass"
    )

    url = user.avatar_url

    assert "ui-avatars.com" in url
    assert quote("avatarname") in url


@pytest.mark.django_db
def test_avatar_email_prefix_encoded():
    user = User(
        email=EMAIL_WITH_PREFIX,
        username=""
    )

    assert quote("john.doe") in user.avatar_url


def test_avatar_fallback_user_word():
    user = User(email="", username="")

    assert "name=user" in user.avatar_url


# ======================================================
# Model Config Tests
# ======================================================

def test_username_field_setting():
    assert User.USERNAME_FIELD == "email"


def test_required_fields_setting():
    assert User.REQUIRED_FIELDS == ["username"]
