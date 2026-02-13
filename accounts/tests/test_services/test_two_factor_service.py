# =============================================================
# Third-Party Imports
# =============================================================
import pytest
from unittest.mock import MagicMock

# =============================================================
# Local Service Imports
# =============================================================
from accounts.services.auth import TwoFactorService

# =============================================================
# Core Exceptions
# =============================================================
from core.exceptions import ValidationException, AuthenticationFailedException

# =============================================================
# Test Case 1: Setup 2FA Success
# =============================================================
@pytest.mark.django_db
def test_setup_2fa_success(twofa_user, mock_totp_setup_methods):

    # Step 1 — Call 2FA setup service
    result = TwoFactorService.setup_2fa(twofa_user)

    # Step 2 — Verify secret and URI returned correctly
    assert result["totp_secret"] == "SECRET123"
    assert result["totp_uri"] == "otpauth://uri"

# =============================================================
# Test Case 2: Setup 2FA Already Enabled
# =============================================================
@pytest.mark.django_db
def test_setup_2fa_already_enabled(security_2fa_enabled):

    # Step 1 — Get user with 2FA already enabled
    user = security_2fa_enabled.user

    # Step 2 — Expect validation exception when setting up 2FA again
    with pytest.raises(ValidationException):
        TwoFactorService.setup_2fa(user)

# =============================================================
# Test Case 3: Enable 2FA Success
# =============================================================
@pytest.mark.django_db
def test_enable_2fa_success(twofa_user, mock_totp_valid):

    # Step 1 — Mock valid TOTP verification
    twofa_user.security.verify_totp = mock_totp_valid

    # Step 2 — Call enable 2FA service with correct OTP
    result = TwoFactorService.enable_2fa(twofa_user, "123456")

    # Step 3 — Refresh security profile
    twofa_user.security.refresh_from_db()

    # Step 4 — Validate 2FA enabled successfully
    assert twofa_user.security.is_2fa_enabled is True
    assert result["success"] is True


# =============================================================
# Test Case 4: Enable 2FA Invalid OTP
# =============================================================
@pytest.mark.django_db
def test_enable_2fa_invalid_otp(twofa_user, mock_totp_invalid):

    # Step 1 — Mock invalid TOTP verification
    twofa_user.security.verify_totp = mock_totp_invalid

    # Step 2 — Expect authentication failure for wrong OTP
    with pytest.raises(AuthenticationFailedException):
        TwoFactorService.enable_2fa(twofa_user, "000000")


# =============================================================
# Test Case 5: Disable 2FA Success
# =============================================================
@pytest.mark.django_db
def test_disable_2fa_success(security_2fa_enabled, mock_totp_valid):

    # Step 1 — Mock valid TOTP verification
    security_2fa_enabled.verify_totp = mock_totp_valid
    user = security_2fa_enabled.user

    # Step 2 — Call disable 2FA service
    result = TwoFactorService.disable_2fa(user, "123456")

    # Step 3 — Refresh security profile
    security_2fa_enabled.refresh_from_db()

    # Step 4 — Validate 2FA disabled and secret cleared
    assert security_2fa_enabled.is_2fa_enabled is False
    assert security_2fa_enabled.totp_secret is None
    assert result["success"] is True


# =============================================================
# Test Case 6: Disable 2FA Not Enabled
# =============================================================
@pytest.mark.django_db
def test_disable_2fa_not_enabled(security_2fa_disabled):

    # Step 1 — Get user with 2FA disabled
    user = security_2fa_disabled.user

    # Step 2 — Expect validation exception when disabling 2FA
    with pytest.raises(ValidationException):
        TwoFactorService.disable_2fa(user, "123456")


# =============================================================
# Test Case 7: Verify 2FA and Issue Tokens
# =============================================================
@pytest.mark.django_db
def test_verify_2fa_and_issue_tokens_success(
    security_2fa_enabled,
    mock_totp_valid,
    mock_refresh_token
):

    # Step 1 — Mock valid TOTP verification
    security_2fa_enabled.verify_totp = mock_totp_valid
    user = security_2fa_enabled.user

    # Step 2 — Call service to verify 2FA and generate JWT tokens
    tokens = TwoFactorService.verify_2fa_and_issue_tokens(user, "123456")

    # Step 3 — Validate returned tokens
    assert tokens["access"] == "access123"
    assert tokens["refresh"] == "refresh123"


# =============================================================
# Test Case 8: Verify 2FA Invalid OTP
# =============================================================
@pytest.mark.django_db
def test_verify_2fa_invalid_otp(
    security_2fa_enabled,
    mock_totp_invalid
):

    # Step 1 — Mock invalid TOTP verification
    security_2fa_enabled.verify_totp = mock_totp_invalid
    user = security_2fa_enabled.user

    # Step 2 — Expect authentication failure for invalid OTP
    with pytest.raises(AuthenticationFailedException):
        TwoFactorService.verify_2fa_and_issue_tokens(user, "000000")
