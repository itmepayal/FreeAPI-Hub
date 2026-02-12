# =============================================================
# Pytest: ResetPasswordService
# =============================================================
import pytest
from django.contrib.auth.hashers import check_password
from django.utils import timezone
from datetime import timedelta

# =============================================================
# Local Models
# =============================================================
from accounts.models import UserSecurity, User

# =============================================================
# Core Exceptions
# =============================================================
from core.exceptions import (
    InvalidTokenException,
    ValidationException,
    InternalServerException,
)

# =============================================================
# Services
# =============================================================
from accounts.services.auth import ResetPasswordService

# =============================================================
# Test Case 1: Success Path
# =============================================================
@pytest.mark.django_db
def test_reset_password_success():
    # Step 1 — Create active user
    user = User.objects.create(
        username="testuser",
        email="test@example.com",
        is_verified=False
    )

    # Step 2 — Fetch UserSecurity created via signal
    security = UserSecurity.objects.get(user=user)

    # Step 3 — Generate forgot password token
    raw_token = security.generate_forgot_password()

    # Step 4 — Define new strong password
    new_password = "StrongPassword@123"

    # Step 5 — Call reset password service
    result_user = ResetPasswordService.reset_password(
        token=raw_token,
        new_password=new_password,
    )

    # Step 6 — Refresh objects from DB
    user.refresh_from_db()
    security.refresh_from_db()

    # Step 7 — Assertions
    assert result_user.id == user.id
    assert check_password(new_password, user.password)
    assert security.forgot_password_token is None
    assert security.forgot_password_expiry is None

# =============================================================
# Test Case: Missing Token
# =============================================================
@pytest.mark.django_db
def test_reset_password_missing_token():
    # Step 1 — Call reset password service with empty token
    with pytest.raises(InvalidTokenException):
        ResetPasswordService.reset_password(
            token="",
            new_password="StrongPassword@123",
        )

# =============================================================
# Test Case: Invalid Token
# =============================================================
@pytest.mark.django_db
def test_reset_password_invalid_token():
    # Step 1 — Call reset password service with invalid token
    with pytest.raises(InvalidTokenException):
        ResetPasswordService.reset_password(
            token="invalid-token",
            new_password="StrongPassword@123",
        )


# =============================================================
# Test Case: Expired Token
# =============================================================
@pytest.mark.django_db
def test_reset_password_expired_token():
    # Step 1 — Create active user
    user = User.objects.create(
        username="testuser",
        email="test@example.com",
        is_verified=False
    )

    # Step 2 — Fetch UserSecurity
    security = UserSecurity.objects.get(user=user)

    # Step 3 — Generate forgot password token
    raw_token = security.generate_forgot_password()

    # Step 4 — Force token expiry into the past
    security.forgot_password_expiry = timezone.now() - timedelta(minutes=1)
    security.save()

    # Step 5 — Call reset password service and expect exception
    with pytest.raises(InvalidTokenException):
        ResetPasswordService.reset_password(
            token=raw_token,
            new_password="StrongPassword@123",
        )


# =============================================================
# Test Case: Inactive User
# =============================================================
@pytest.mark.django_db
def test_reset_password_inactive_user():
    # Step 1 — Create inactive user
    user = User.objects.create(
        username="testuser",
        email="test@example.com",
        is_verified=False,
        is_active=False
    )

    # Step 2 — Fetch UserSecurity
    security = UserSecurity.objects.get(user=user)

    # Step 3 — Generate forgot password token
    raw_token = security.generate_forgot_password()

    # Step 4 — Call reset password service and expect exception
    with pytest.raises(InvalidTokenException):
        ResetPasswordService.reset_password(
            token=raw_token,
            new_password="StrongPassword@123",
        )

# =============================================================
# Test Case: Weak Password
# =============================================================
@pytest.mark.django_db
def test_reset_password_weak_password():
    # Step 1 — Create active user
    user = User.objects.create(
        username="testuser",
        email="test@example.com",
        is_verified=False,
        is_active=True
    )

    # Step 2 — Fetch UserSecurity
    security = UserSecurity.objects.get(user=user)

    # Step 3 — Generate valid forgot password token
    raw_token = security.generate_forgot_password()

    # Step 4 — Call reset password service with weak password
    with pytest.raises(ValidationException):
        ResetPasswordService.reset_password(
            token=raw_token,
            new_password="123",
        )
