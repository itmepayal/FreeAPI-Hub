# =============================================================
# Pytest: RefreshTokenService
# =============================================================
import pytest
from unittest.mock import patch, MagicMock

# =============================================================
# Services
# =============================================================
from accounts.services.auth import RefreshTokenService

# =============================================================
# JWT Exceptions
# =============================================================
from rest_framework_simplejwt.exceptions import TokenError

# =============================================================
# Core Exceptions
# =============================================================
from core.exceptions import (
    InvalidTokenException,
    InternalServerException,
    ServiceException,
)

# =============================================================
# Test Case 1: Successful Access Token Refresh
# =============================================================
@pytest.mark.django_db
def test_refresh_access_token_success():
    # Step 1 — Create mock RefreshToken instance
    mock_token = MagicMock()
    mock_token.access_token = "new_access_token_123"

    # Step 2 — Patch RefreshToken constructor
    with patch(
        "accounts.services.auth.refresh_token_service.RefreshToken",
        return_value=mock_token
    ):
        # Step 3 — Call service
        new_token = RefreshTokenService.refresh_access_token("valid.refresh.token")

    # Step 4 — Assertions
    assert new_token == "new_access_token_123"
    
# =============================================================
# Test Case 2: Invalid TokenError
# =============================================================
@pytest.mark.django_db
def test_refresh_access_token_invalid_token():
    """
    Test TokenError raises InvalidTokenException
    """

    # Step 1 — Patch RefreshToken to raise TokenError
    with patch(
        "accounts.services.auth.refresh_token_service.RefreshToken",
        side_effect=TokenError("expired")
    ):
        # Step 2 — Expect InvalidTokenException
        with pytest.raises(InvalidTokenException) as excinfo:
            RefreshTokenService.refresh_access_token("bad.token")

    # Step 3 — Validate message
    assert "Invalid or expired refresh token" in str(excinfo.value)
    
# =============================================================
# Test Case 3: ServiceException Re-raised
# =============================================================
@pytest.mark.django_db
def test_refresh_access_token_service_exception():
    """
    Test ServiceException is re-raised without wrapping
    """

    # Step 1 — Patch RefreshToken to raise ServiceException
    with patch(
        "accounts.services.auth.refresh_token_service.RefreshToken",
        side_effect=ServiceException("service fail")
    ):
        # Step 2 — Expect same exception
        with pytest.raises(ServiceException):
            RefreshTokenService.refresh_access_token("token")


# =============================================================
# Test Case 4: Unexpected Exception Wrapped
# =============================================================
@pytest.mark.django_db
def test_refresh_access_token_unexpected_exception():
    """
    Test unexpected errors are wrapped into InternalServerException
    """

    # Step 1 — Patch RefreshToken to raise generic exception
    with patch(
        "accounts.services.auth.refresh_token_service.RefreshToken",
        side_effect=Exception("decode failure")
    ):
        # Step 2 — Expect wrapped exception
        with pytest.raises(InternalServerException) as excinfo:
            RefreshTokenService.refresh_access_token("token")

    # Step 3 — Validate wrapped message
    assert "Failed to refresh access token due to unexpected error" in str(excinfo.value)