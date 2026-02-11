# =============================================================
# Pytest: LogoutService
# =============================================================
import pytest
from unittest.mock import patch, MagicMock

# =============================================================
# Local Imports
# =============================================================
from accounts.models import User
from accounts.services.auth import LogoutService

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
# Test Case 1: Successful Logout
# =============================================================
@pytest.mark.django_db
def test_logout_user_success():
    # Step 1 — Create user
    user = User.objects.create_user(
        username="logoutuser",
        email="logout@example.com",
        password="StrongPass123!"
    )
    
    # Step 2 — Create mock token with matching user_id
    mock_token = MagicMock()
    mock_token.payload = {"user_id": str(user.id)}

    # Step 3 — Patch RefreshToken constructor
    with patch(
        "accounts.services.auth.logout_service.RefreshToken",
        return_value=mock_token
    ):
        # Step 4 — Call logout service
        LogoutService.logout_user(user, "refresh.token.value")

    # Step 5 — Assert blacklist called
    mock_token.blacklist.assert_called_once()

# =============================================================
# Test Case 2: Token User Mismatch
# =============================================================
@pytest.mark.django_db
def test_logout_user_token_user_mismatch():
    # Step 1 — Create user
    user = User.objects.create_user(
        username="logoutuser2",
        email="logout2@example.com",
        password="StrongPass123!"
    )

    # Step 2 — Mock token with different user_id
    mock_token = MagicMock()
    mock_token.payload = {"user_id": "999999"}

    # Step 3 — Patch RefreshToken
    with patch(
        "accounts.services.auth.logout_service.RefreshToken",
        return_value=mock_token
    ):
        # Step 4 — Expect InvalidTokenException
        with pytest.raises(InvalidTokenException) as excinfo:
            LogoutService.logout_user(user, "bad.token")
    
    # Step 5 — Validate message
    assert "Token does not belong to the user" in str(excinfo.value)

# =============================================================
# Test Case 3: Invalid TokenError Raised
# =============================================================
@pytest.mark.django_db
def test_logout_user_invalid_token_error():
    # Step 1 — Create user
    user = User.objects.create_user(
        username="logoutuser3",
        email="logout3@example.com",
        password="StrongPass123!"
    )
    
    # Step 2 — Patch RefreshToken to raise TokenError
    with patch(
        "accounts.services.auth.logout_service.RefreshToken",
        side_effect=TokenError("expired")
    ):
        # Step 3 — Expect InvalidTokenException
        with pytest.raises(InvalidTokenException) as excinfo:
            LogoutService.logout_user(user, "expired.token")

    # Step 4 — Validate message
    assert "Invalid or expired refresh token" in str(excinfo.value)

# =============================================================
# Test Case 4: ServiceException Re-raised
# =============================================================
@pytest.mark.django_db
def test_logout_user_service_exception_reraised():
    # Step 1 — Create user
    user = User.objects.create_user(
        username="logoutuser4",
        email="logout4@example.com",
        password="StrongPass123!"
    )

    # Step 2 — Patch RefreshToken to raise ServiceException
    with patch(
        "accounts.services.auth.logout_service.RefreshToken",
        side_effect=ServiceException("service fail")
    ):
        # Step 3 — Expect same ServiceException
        with pytest.raises(ServiceException):
            LogoutService.logout_user(user, "token")
            
# =============================================================
# Test Case 5: Unexpected Exception Wrapped
# =============================================================
@pytest.mark.django_db
def test_logout_user_unexpected_exception():

    # Step 1 — Create user
    user = User.objects.create_user(
        username="logoutuser5",
        email="logout5@example.com",
        password="StrongPass123!"
    )

    # Step 2 — Mock token but blacklist fails
    mock_token = MagicMock()
    mock_token.payload = {"user_id": str(user.id)}
    mock_token.blacklist.side_effect = Exception("DB failure")

    # Step 3 — Patch RefreshToken
    with patch(
        "accounts.services.auth.logout_service.RefreshToken",
        return_value=mock_token
    ):
        # Step 4 — Expect wrapped exception
        with pytest.raises(InternalServerException) as excinfo:
            LogoutService.logout_user(user, "token")

    # Step 5 — Validate wrapped message
    assert "Logout failed due to an unexpected error" in str(excinfo.value)
