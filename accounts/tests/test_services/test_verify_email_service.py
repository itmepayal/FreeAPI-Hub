# =============================================================
# Pytest: VerifyEmailService
# =============================================================
import pytest

# =============================================================
# Local Imports — Models Under Test
# =============================================================
from accounts.models import UserSecurity, User

# =============================================================
# Local Imports — Service Under Test
# =============================================================
from accounts.services.auth import VerifyEmailService

# =============================================================
# Core Exceptions — Expected Failure Types
# =============================================================
from core.exceptions import (
    InvalidTokenException,
    OperationNotAllowedException,
)

# =============================================================
# Test Case 1: Successful Email Verification
# =============================================================
@pytest.mark.django_db
def test_verify_email_success(
    user_factory,
    set_security_flags,
    mock_hash_token,
    future_time,
):
    # Step 1 — Arrange: Create unverified user
    user = user_factory(is_verified=False)

    # Step 2 — Arrange: Fetch related security profile
    security = UserSecurity.objects.get(user=user)
    token_in_db = security.email_verification_token

    # Step 3 — Arrange: Set token expiry in future
    set_security_flags(
        user,
        email_verification_expiry=future_time
    )

    # Step 4 — Arrange: Mock hash_token to match DB token
    mock_hash_token.return_value = token_in_db

    # Step 5 — Act: Execute email verification
    result = VerifyEmailService.verify_email("raw_token_here")

    # Step 6 — Assert: Returned object is security profile
    assert result == security

    # Step 7 — Assert: User is now marked verified
    user.refresh_from_db()
    assert user.is_verified is True


# =============================================================
# Test Case 2: Invalid Token
# =============================================================
@pytest.mark.django_db
def test_verify_email_invalid_token(mock_hash_token):

    # Step 1 — Arrange: Hash resolves to non-existent token
    mock_hash_token.return_value = "non_existent_token"

    # Step 2 — Act + Assert: Expect invalid token exception
    with pytest.raises(InvalidTokenException) as excinfo:
        VerifyEmailService.verify_email("bad_token")

    # Step 3 — Assert: Error message is correct
    assert "Invalid or expired verification token" in str(excinfo.value)


# =============================================================
# Test Case 3: Already Verified User
# =============================================================
@pytest.mark.django_db
def test_verify_email_already_verified(
    user_factory,
    set_security_flags,
    mock_hash_token,
    future_time,
):
    # Step 1 — Arrange: Create already verified user
    user = user_factory(is_verified=True)

    # Step 2 — Arrange: Fetch security profile
    security = UserSecurity.objects.get(user=user)
    token_in_db = security.email_verification_token

    # Step 3 — Arrange: Ensure token expiry still valid
    set_security_flags(
        user,
        email_verification_expiry=future_time
    )

    # Step 4 — Arrange: Mock hash_token match
    mock_hash_token.return_value = token_in_db

    # Step 5 — Act + Assert: Expect already verified error
    with pytest.raises(OperationNotAllowedException) as excinfo:
        VerifyEmailService.verify_email("raw_token")

    # Step 6 — Assert: Correct message returned
    assert "Email already verified" in str(excinfo.value)


# =============================================================
# Test Case 4: Expired Token
# =============================================================
@pytest.mark.django_db
def test_verify_email_expired_token(
    user_factory,
    set_security_flags,
    mock_hash_token,
    past_time,
):
    # Step 1 — Arrange: Create unverified user
    user = user_factory(is_verified=False)

    # Step 2 — Arrange: Fetch security profile
    security = UserSecurity.objects.get(user=user)

    # Step 3 — Arrange: Force known token value
    security.email_verification_token = "hashed_token_here"
    security.save()

    # Step 4 — Arrange: Set expiry in the past
    set_security_flags(
        user,
        email_verification_expiry=past_time
    )

    # Step 5 — Arrange: Mock hash_token match
    mock_hash_token.return_value = "hashed_token_here"

    # Step 6 — Act + Assert: Expect expired token error
    with pytest.raises(InvalidTokenException) as excinfo:
        VerifyEmailService.verify_email("raw")

    # Step 7 — Assert: Correct message returned
    assert "Invalid or expired verification token" in str(excinfo.value)


# =============================================================
# Test Case 5: Atomic Save Failure During Verification
# =============================================================
@pytest.mark.django_db
def test_verify_email_atomic_save_failure(
    user_factory,
    set_security_flags,
    mock_hash_token,
    future_time,
):
    from unittest.mock import patch

    # Step 1 — Arrange: Create unverified user
    user = user_factory(is_verified=False)

    # Step 2 — Arrange: Fetch security profile
    security = UserSecurity.objects.get(user=user)

    # Step 3 — Arrange: Set known token value
    security.email_verification_token = "hashed_token_here"
    security.save()

    # Step 4 — Arrange: Set valid future expiry
    set_security_flags(
        user,
        email_verification_expiry=future_time
    )

    # Step 5 — Arrange: Mock hash_token match
    mock_hash_token.return_value = "hashed_token_here"

    # Step 6 — Arrange: Force DB save failure
    with patch.object(User, "save", side_effect=Exception("DB fail")):

        # Step 7 — Act + Assert: Expect propagated exception
        with pytest.raises(Exception) as excinfo:
            VerifyEmailService.verify_email("raw")

    # Step 8 — Assert: Failure reason preserved
    assert "DB fail" in str(excinfo.value)
