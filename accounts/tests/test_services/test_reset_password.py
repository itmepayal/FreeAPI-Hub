# =============================================================
# Pytest: ResetPasswordService
# =============================================================
import pytest
from unittest.mock import MagicMock, patch
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.hashers import check_password

# =============================================================
# Local Model Imports
# =============================================================
from accounts.models import UserSecurity

# =============================================================
# Core Exception Imports
# =============================================================
from core.exceptions import InvalidTokenException, ValidationException

# =============================================================
# Local Service Imports
# =============================================================
from accounts.services.auth import ResetPasswordService

# =============================================================
# Test Case 1: Success Path — Reset Password with Valid Token
# =============================================================
@pytest.mark.django_db
def test_reset_password_success(user_factory):
    # Step 1 — Create active user using fixture
    user = user_factory(is_active=True)

    # Step 2 — Fetch associated UserSecurity object
    security = user.security

    # Step 3 — Generate a valid forgot password token
    raw_token = security.generate_forgot_password()

    # Step 4 — Define new strong password
    new_password = "StrongPassword@123"

    # Step 5 — Call ResetPasswordService to reset password
    result_user = ResetPasswordService.reset_password(
        token=raw_token,
        new_password=new_password,
    )

    # Step 6 — Refresh user and security objects from database
    user.refresh_from_db()
    security.refresh_from_db()

    # Step 7 — Assertions: check password updated, token cleared
    assert result_user.id == user.id
    assert check_password(new_password, user.password)
    assert security.forgot_password_token is None
    assert security.forgot_password_expiry is None


# =============================================================
# Test Case: Missing Token — Expect InvalidTokenException
# =============================================================
@pytest.mark.django_db
def test_reset_password_missing_token(user_factory):
    # Step 1 — Create user using fixture
    user = user_factory()

    # Step 2 — Call ResetPasswordService with empty token
    # Step 3 — Expect InvalidTokenException to be raised
    with pytest.raises(InvalidTokenException):
        ResetPasswordService.reset_password(token="", new_password="StrongPassword@123")


# =============================================================
# Test Case: Invalid Token — Expect InvalidTokenException
# =============================================================
@pytest.mark.django_db
def test_reset_password_invalid_token(user_factory):
    # Step 1 — Create user using fixture
    user = user_factory()

    # Step 2 — Call ResetPasswordService with invalid token
    # Step 3 — Expect InvalidTokenException to be raised
    with pytest.raises(InvalidTokenException):
        ResetPasswordService.reset_password(token="invalid-token", new_password="StrongPassword@123")


# =============================================================
# Test Case: Expired Token — Expect InvalidTokenException
# =============================================================
@pytest.mark.django_db
def test_reset_password_expired_token(user_factory, past_time):
    # Step 1 — Create user using fixture
    user = user_factory()
    security = user.security

    # Step 2 — Generate a valid forgot password token
    raw_token = security.generate_forgot_password()

    # Step 3 — Force token expiry into the past using fixture
    security.forgot_password_expiry = past_time
    security.save()

    # Step 4 — Call ResetPasswordService with expired token
    # Step 5 — Expect InvalidTokenException to be raised
    with pytest.raises(InvalidTokenException):
        ResetPasswordService.reset_password(token=raw_token, new_password="StrongPassword@123")


# =============================================================
# Test Case: Inactive User — Expect InvalidTokenException
# =============================================================
@pytest.mark.django_db
def test_reset_password_inactive_user(user_factory):
    # Step 1 — Create inactive user using fixture
    user = user_factory(is_active=False)
    security = user.security

    # Step 2 — Generate a valid forgot password token
    raw_token = security.generate_forgot_password()

    # Step 3 — Call ResetPasswordService and expect failure
    with pytest.raises(InvalidTokenException):
        ResetPasswordService.reset_password(token=raw_token, new_password="StrongPassword@123")


# =============================================================
# Test Case: Weak Password — Expect ValidationException
# =============================================================
@pytest.mark.django_db
def test_reset_password_weak_password(user_factory):
    # Step 1 — Create active user using fixture
    user = user_factory()
    security = user.security

    # Step 2 — Generate a valid forgot password token
    raw_token = security.generate_forgot_password()

    # Step 3 — Call ResetPasswordService with weak password
    with pytest.raises(ValidationException):
        ResetPasswordService.reset_password(token=raw_token, new_password="123")
