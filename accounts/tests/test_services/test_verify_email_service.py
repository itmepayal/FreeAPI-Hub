# =============================================================
# Pytest: VerifyEmailService
# =============================================================
import pytest
from unittest.mock import patch
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
    OperationNotAllowedException,
)

# =============================================================
# Services
# =============================================================
from accounts.services.auth import VerifyEmailService

# =============================================================
# Test Case 1: Success Path
# =============================================================
@pytest.mark.django_db
def test_verify_email_success():
    # Step 1 — Create user (signal automatically creates UserSecurity)
    user = User.objects.create(
        username="testuser",
        email="test@example.com",
        is_verified=False
    )

    # Step 2 — Fetch the UserSecurity object created by signal
    security = UserSecurity.objects.get(user=user)
    token_in_db = security.email_verification_token

    # Step 3 — Ensure token expiry is in the future
    security.email_verification_expiry = timezone.now() + timedelta(hours=1)
    security.save()

    # Step 4 — Patch hash_token in the service module
    with patch(
        "accounts.services.auth.verify_email_service.hash_token",
        return_value=token_in_db
    ):
        # Step 4a — Call the service with any raw token
        result = VerifyEmailService.verify_email("raw_token_here")

    # Step 5 — Assertions: service returns security object, user marked verified
    assert result == security
    user.refresh_from_db()
    security.refresh_from_db()
    assert user.is_verified is True

# =============================================================
# Test Case 2: Invalid Token
# =============================================================
@pytest.mark.django_db
def test_verify_email_invalid_token():
    # Step 1 — Patch hash_token to return a token that does NOT exist in DB
    with patch(
        "accounts.services.auth.verify_email_service.hash_token",
        return_value="non_existent_token"
    ):
        # Step 2 — Call service with some raw token and expect InvalidTokenException
        with pytest.raises(InvalidTokenException) as excinfo:
            VerifyEmailService.verify_email("some_invalid_token")

        # Step 3 — Assert exception message is correct
        assert "Invalid or expired verification token" in str(excinfo.value)


# =============================================================
# Test Case 3: Already Verified
# =============================================================
@pytest.mark.django_db
def test_verify_email_already_verified():
    """
    Test user already verified raises OperationNotAllowedException
    """
    # Step 1 — Create a verified user
    user = User.objects.create(
        username="verified_user",
        email="verified@example.com",
        is_verified=True
    )

    # Step 2 — Fetch UserSecurity
    security = UserSecurity.objects.get(user=user)
    token_in_db = security.email_verification_token

    # Step 3 — Ensure token is valid
    security.email_verification_expiry = timezone.now() + timedelta(hours=1)
    security.save()

    # Step 4 — Patch hash_token
    with patch(
        "accounts.services.auth.verify_email_service.hash_token",
        return_value=token_in_db
    ):
        # Step 5 — Expect exception since user is already verified
        with pytest.raises(OperationNotAllowedException) as excinfo:
            VerifyEmailService.verify_email("raw_token_here")
        assert "Email already verified" in str(excinfo.value)

# =============================================================
# Test Case 4: Expired Token
# =============================================================
@pytest.mark.django_db
def test_verify_email_expired_token():
    """
    Test expired token raises InvalidTokenException
    """
    # Step 1 — Create unverified user
    user = User.objects.create(
        username="expired_user",
        email="expired@example.com",
        is_verified=False
    )

    # Step 2 — Fetch UserSecurity
    security = UserSecurity.objects.get(user=user)

    # Step 3 — Expire token
    security.email_verification_token = "hashed_token_here"
    security.email_verification_expiry = timezone.now() - timedelta(hours=1)  # expired
    security.save()

    # Step 4 — Patch hash_token to match DB
    with patch(
        "accounts.services.auth.verify_email_service.hash_token",
        return_value="hashed_token_here"
    ):
        # Step 5 — Expect InvalidTokenException
        with pytest.raises(InvalidTokenException) as excinfo:
            VerifyEmailService.verify_email("raw_token_here")
        assert "Invalid or expired verification token" in str(excinfo.value)

# =============================================================
# Test Case 5: Atomic Save Failure
# =============================================================
@pytest.mark.django_db
def test_verify_email_atomic_save_failure():
    """
    Test transaction fails if saving user raises exception
    """
    # Step 1 — Create user
    user = User.objects.create(
        username="atomic_user",
        email="atomic@example.com",
        is_verified=False
    )

    # Step 2 — Fetch UserSecurity
    security = UserSecurity.objects.get(user=user)

    # Step 3 — Set valid token and future expiry
    security.email_verification_token = "hashed_token_here"
    security.email_verification_expiry = timezone.now() + timedelta(hours=1)
    security.save()

    # Step 4 — Patch hash_token and make User.save fail
    with patch(
        "accounts.services.auth.verify_email_service.hash_token",
        return_value="hashed_token_here"
    ), patch.object(User, "save", side_effect=Exception("DB fail")):
        # Step 5 — Expect exception
        with pytest.raises(Exception) as excinfo:
            VerifyEmailService.verify_email("raw_token_here")
        # Step 6 — Assert exception message
        assert "DB fail" in str(excinfo.value)
