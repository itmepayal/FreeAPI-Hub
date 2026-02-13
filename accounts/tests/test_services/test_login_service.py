# =============================================================
# Pytest: LoginService
# =============================================================
import pytest

# =============================================================
# Local Imports — Service Under Test
# =============================================================
from accounts.services.auth import LoginService

# =============================================================
# Core Exceptions — Expected Failure Types
# =============================================================
from core.exceptions import (
    AuthenticationRequiredException,
    InactiveUserException,
    InvalidTokenException,
    ServiceException,
    InternalServerException,
)

# =============================================================
# Test Case 1: Successful Login (No 2FA Enabled)
# =============================================================
@pytest.mark.django_db
def test_login_user_success(
    user_factory,
    set_security_flags,
    mock_authenticate,
    mock_tokens,
):
    # Step 1 — Arrange: Create valid active + verified user
    user = user_factory()

    # Step 2 — Arrange: Disable 2FA in security profile
    set_security_flags(user, is_2fa_enabled=False)

    # Step 3 — Arrange: Mock authenticate() to return user
    mock_authenticate.return_value = user

    # Step 4 — Act: Execute login service
    result = LoginService.login_user(
        email=user.email,
        password="StrongPass123!",
        request_ip="127.0.0.1"
    )

    # Step 5 — Assert: Correct user returned
    assert result["user"] == user

    # Step 6 — Assert: Tokens were generated
    assert result["tokens"]["access"] == "access123"


# =============================================================
# Test Case 2: Login Requires 2FA
# =============================================================
@pytest.mark.django_db
def test_login_user_requires_2fa(
    user_factory,
    set_security_flags,
    mock_authenticate,
    mock_2fa_token,
):
    # Step 1 — Arrange: Create active verified user
    user = user_factory()

    # Step 2 — Arrange: Enable 2FA flag
    set_security_flags(user, is_2fa_enabled=True)

    # Step 3 — Arrange: Mock authenticate() success
    mock_authenticate.return_value = user

    # Step 4 — Act: Execute login
    result = LoginService.login_user(
        email=user.email,
        password="StrongPass123!",
        request_ip="127.0.0.1"
    )

    # Step 5 — Assert: 2FA challenge required
    assert result["requires_2fa"] is True

    # Step 6 — Assert: Temporary token issued
    assert result["temp_token"] == "temp2fa123"


# =============================================================
# Test Case 3: Invalid Credentials
# =============================================================
@pytest.mark.django_db
def test_login_user_invalid_credentials(mock_authenticate):
    # Step 1 — Arrange: Force authenticate() to fail
    mock_authenticate.return_value = None

    # Step 2 — Act + Assert: Expect auth exception
    with pytest.raises(AuthenticationRequiredException):
        LoginService.login_user(
            email="wrong@example.com",
            password="wrongpass",
            request_ip="127.0.0.1"
        )


# =============================================================
# Test Case 4: Inactive User Login
# =============================================================
@pytest.mark.django_db
def test_login_user_inactive(
    user_factory,
    mock_authenticate,
):
    # Step 1 — Arrange: Create inactive user
    user = user_factory(is_active=False)

    # Step 2 — Arrange: Mock authenticate success
    mock_authenticate.return_value = user

    # Step 3 — Act + Assert: Expect inactive exception
    with pytest.raises(InactiveUserException):
        LoginService.login_user(
            user.email,
            "StrongPass123!",
            "127.0.0.1"
        )


# =============================================================
# Test Case 5: Email Not Verified
# =============================================================
@pytest.mark.django_db
def test_login_user_email_not_verified(
    user_factory,
    mock_authenticate,
):
    # Step 1 — Arrange: Create unverified user
    user = user_factory(is_verified=False)

    # Step 2 — Arrange: Mock authenticate success
    mock_authenticate.return_value = user

    # Step 3 — Act + Assert: Expect verification exception
    with pytest.raises(InvalidTokenException):
        LoginService.login_user(
            user.email,
            "StrongPass123!",
            "127.0.0.1"
        )


# =============================================================
# Test Case 6: Missing Security Profile
# =============================================================
@pytest.mark.django_db
def test_login_user_missing_security(
    user_factory,
    mock_authenticate,
):
    # Step 1 — Arrange: Create valid user
    user = user_factory()

    # Step 2 — Arrange: Remove security relation
    user.security = None

    # Step 3 — Arrange: Mock authenticate success
    mock_authenticate.return_value = user

    # Step 4 — Act + Assert: Expect service exception
    with pytest.raises(ServiceException):
        LoginService.login_user(
            user.email,
            "StrongPass123!",
            "127.0.0.1"
        )

# =============================================================
# Test Case 7: Unexpected Internal Error
# =============================================================
@pytest.mark.django_db
def test_login_user_unexpected_exception(mock_authenticate):
    # Step 1 — Arrange: Force unexpected failure
    mock_authenticate.side_effect = Exception("DB error")

    # Step 2 — Act + Assert: Expect wrapped internal exception
    with pytest.raises(InternalServerException):
        LoginService.login_user(
            "any@example.com",
            "any",
            "127.0.0.1"
        )
