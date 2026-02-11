# =============================================================
# Pytest: TwoFactorService
# =============================================================
import pytest
from unittest.mock import patch, MagicMock

# =============================================================
# Local Models
# =============================================================
from accounts.models import User, UserSecurity
from accounts.services.auth import TwoFactorService

# =============================================================
# Core Exceptions
# =============================================================
from core.exceptions import (
    ValidationException,
    AuthenticationFailedException,
)

# =============================================================
# Test Case 1: Setup 2FA Success
# =============================================================
@pytest.mark.django_db
def test_setup_2fa_success():

    # Step 1 — Create test user
    user = User.objects.create_user(
        username="twofa",
        email="twofa@test.com",
        password="Pass123!"
    )

    # Step 2 — Get related security profile
    security = user.security

    # Step 3 — Mock secret + URI generators
    security.generate_totp_secret = MagicMock(return_value="SECRET123")
    security.get_totp_uri = MagicMock(return_value="otpauth://uri")

    # Step 4 — Call 2FA setup service
    result = TwoFactorService.setup_2fa(user)

    # Step 5 — Verify response data
    assert result["totp_secret"] == "SECRET123"
    assert result["totp_uri"] == "otpauth://uri"


# =============================================================
# Test Case 2: Setup 2FA Already Enabled
# =============================================================
@pytest.mark.django_db
def test_setup_2fa_already_enabled():

    # Step 1 — Create user
    user = User.objects.create_user(
        username="twofa2",
        email="twofa2@test.com",
        password="Pass123!"
    )

    # Step 2 — Enable 2FA manually
    security = user.security
    security.is_2fa_enabled = True
    security.save()

    # Step 3 — Expect validation failure
    with pytest.raises(ValidationException):
        TwoFactorService.setup_2fa(user)


# =============================================================
# Test Case 3: Enable 2FA Success
# =============================================================
@pytest.mark.django_db
def test_enable_2fa_success():

    # Step 1 — Create test user
    user = User.objects.create_user(
        username="enable2fa",
        email="enable@test.com",
        password="Pass123!"
    )

    # Step 2 — Get security profile
    security = user.security

    # Step 3 — Mock OTP verification success
    security.verify_totp = MagicMock(return_value=True)

    # Step 4 — Call enable 2FA service
    result = TwoFactorService.enable_2fa(user, "123456")

    # Step 5 — Reload security from DB
    security.refresh_from_db()

    # Step 6 — Verify 2FA enabled
    assert security.is_2fa_enabled is True
    assert result["success"] is True


# =============================================================
# Test Case 4: Enable 2FA Invalid OTP
# =============================================================
@pytest.mark.django_db
def test_enable_2fa_invalid_otp():

    # Step 1 — Create user
    user = User.objects.create_user(
        username="badotp",
        email="bad@test.com",
        password="Pass123!"
    )

    # Step 2 — Mock OTP verification failure
    security = user.security
    security.verify_totp = MagicMock(return_value=False)

    # Step 3 — Expect authentication failure
    with pytest.raises(AuthenticationFailedException):
        TwoFactorService.enable_2fa(user, "000000")


# =============================================================
# Test Case 5: Disable 2FA Success
# =============================================================
@pytest.mark.django_db
def test_disable_2fa_success():

    # Step 1 — Create user
    user = User.objects.create_user(
        username="disable2fa",
        email="disable@test.com",
        password="Pass123!"
    )

    # Step 2 — Prepare enabled 2FA state
    security = user.security
    security.is_2fa_enabled = True
    security.totp_secret = "SECRET"
    security.verify_totp = MagicMock(return_value=True)
    security.save()

    # Step 3 — Call disable 2FA service
    result = TwoFactorService.disable_2fa(user, "123456")

    # Step 4 — Reload security profile
    security.refresh_from_db()

    # Step 5 — Verify disabled + secret cleared
    assert security.is_2fa_enabled is False
    assert security.totp_secret is None
    assert result["success"] is True


# =============================================================
# Test Case 6: Disable 2FA Not Enabled
# =============================================================
@pytest.mark.django_db
def test_disable_2fa_not_enabled():

    # Step 1 — Create user without 2FA
    user = User.objects.create_user(
        username="no2fa",
        email="no2fa@test.com",
        password="Pass123!"
    )

    # Step 2 — Expect validation failure
    with pytest.raises(ValidationException):
        TwoFactorService.disable_2fa(user, "123456")


# =============================================================
# Test Case 7: Verify 2FA and Issue Tokens
# =============================================================
@pytest.mark.django_db
def test_verify_2fa_and_issue_tokens_success():

    # Step 1 — Create user
    user = User.objects.create_user(
        username="verify2fa",
        email="verify@test.com",
        password="Pass123!"
    )

    # Step 2 — Prepare enabled 2FA state
    security = user.security
    security.is_2fa_enabled = True
    security.verify_totp = MagicMock(return_value=True)

    # Step 3 — Mock JWT refresh token creation
    mock_refresh = MagicMock()
    mock_refresh.access_token = "access123"
    mock_refresh.__str__ = lambda self: "refresh123"

    # Step 4 — Patch RefreshToken.for_user
    with patch(
        "accounts.services.auth.two_factor_service.RefreshToken.for_user",
        return_value=mock_refresh
    ):
        tokens = TwoFactorService.verify_2fa_and_issue_tokens(user, "123456")

    # Step 5 — Verify returned tokens
    assert tokens["access"] == "access123"
    assert tokens["refresh"] == "refresh123"


# =============================================================
# Test Case 8: Verify 2FA Invalid OTP
# =============================================================
@pytest.mark.django_db
def test_verify_2fa_invalid_otp():

    # Step 1 — Create user
    user = User.objects.create_user(
        username="verifybad",
        email="verifybad@test.com",
        password="Pass123!"
    )

    # Step 2 — Enable 2FA but mock invalid OTP
    security = user.security
    security.is_2fa_enabled = True
    security.verify_totp = MagicMock(return_value=False)

    # Step 3 — Expect authentication failure
    with pytest.raises(AuthenticationFailedException):
        TwoFactorService.verify_2fa_and_issue_tokens(user, "000000")
