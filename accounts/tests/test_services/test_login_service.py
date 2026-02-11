# =============================================================
# Pytest: LoginService
# =============================================================
import pytest
from unittest.mock import patch

# =============================================================
# Local Models
# =============================================================
from accounts.models import User, UserSecurity
from accounts.services.auth import LoginService

# =============================================================
# Core Exceptions
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
def test_login_user_success():
    """
    Test successful login when user is verified, active, and 2FA is disabled
    """

    # Step 1 — Create verified & active user
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="StrongPass123!",
        is_verified=True,
        is_active=True
    )

    # Step 2 — Ensure security profile exists with 2FA disabled
    UserSecurity.objects.get(user=user).is_2fa_enabled = False

    # Step 3 — Patch authenticate and token generator
    with patch("accounts.services.auth.login_service.authenticate", return_value=user), \
         patch("accounts.services.auth.login_service.generate_tokens",
               return_value={"access": "access123", "refresh": "refresh123"}):

        # Step 4 — Call login service
        result = LoginService.login_user(
            email=user.email,
            password="StrongPass123!",
            request_ip="127.0.0.1"
        )

    # Step 5 — Validate response
    assert result["user"] == user
    assert "tokens" in result
    assert result["tokens"]["access"] == "access123"


# =============================================================
# Test Case 2: Login Requires 2FA
# =============================================================
@pytest.mark.django_db
def test_login_user_requires_2fa():
    """
    Test login flow when 2FA is enabled
    """

    # Step 1 — Create verified & active user
    user = User.objects.create_user(
        username="test2fa",
        email="test2fa@example.com",
        password="StrongPass123!",
        is_verified=True,
        is_active=True
    )

    # Step 2 — Enable 2FA in security profile
    security = UserSecurity.objects.get(user=user)
    security.is_2fa_enabled = True
    security.save()

    user.refresh_from_db()

    # Step 3 — Patch authenticate and 2FA token generator
    with patch("accounts.services.auth.login_service.authenticate", return_value=user), \
            patch("accounts.services.auth.login_service.generate_2fa_token",
                return_value="temp2fa123"):

        # Step 4 — Call login service
        result = LoginService.login_user(
            email=user.email,
            password="StrongPass123!",
            request_ip="127.0.0.1"
        )

    # Step 5 — Validate 2FA response
    assert result["user"] == user
    assert result["requires_2fa"] is True
    assert result["temp_token"] == "temp2fa123"

# =============================================================
# Test Case 3: Invalid Credentials
# =============================================================
@pytest.mark.django_db
def test_login_user_invalid_credentials():
    """
    Test login failure when authentication returns None
    """

    # Step 1 — Patch authenticate to simulate invalid credentials
    with patch("accounts.services.auth.login_service.authenticate", return_value=None):

        # Step 2 — Expect AuthenticationRequiredException
        with pytest.raises(AuthenticationRequiredException) as excinfo:
            LoginService.login_user(
                email="wrong@example.com",
                password="wrongpass",
                request_ip="127.0.0.1"
            )

    # Step 3 — Validate error message
    assert "Invalid credentials" in str(excinfo.value)


# =============================================================
# Test Case 4: Inactive User Login
# =============================================================
@pytest.mark.django_db
def test_login_user_inactive():
    """
    Test login blocked when user account is inactive
    """

    # Step 1 — Create inactive user
    user = User.objects.create_user(
        username="inactive",
        email="inactive@example.com",
        password="StrongPass123!",
        is_verified=True,
        is_active=False
    )

    # Step 2 — Patch authenticate to return user
    with patch("accounts.services.auth.login_service.authenticate", return_value=user):

        # Step 3 — Expect InactiveUserException
        with pytest.raises(InactiveUserException) as excinfo:
            LoginService.login_user(user.email, "StrongPass123!", "127.0.0.1")

    # Step 4 — Validate error message
    assert "User account is inactive" in str(excinfo.value)


# =============================================================
# Test Case 5: Email Not Verified
# =============================================================
@pytest.mark.django_db
def test_login_user_email_not_verified():
    """
    Test login blocked when email is not verified
    """

    # Step 1 — Create unverified user
    user = User.objects.create_user(
        username="notverified",
        email="notverified@example.com",
        password="StrongPass123!",
        is_verified=False,
        is_active=True
    )

    # Step 2 — Patch authenticate
    with patch("accounts.services.auth.login_service.authenticate", return_value=user):

        # Step 3 — Expect InvalidTokenException
        with pytest.raises(InvalidTokenException) as excinfo:
            LoginService.login_user(user.email, "StrongPass123!", "127.0.0.1")

    # Step 4 — Validate error message
    assert "Email is not verified" in str(excinfo.value)


# =============================================================
# Test Case 6: Missing Security Profile
# =============================================================
@pytest.mark.django_db
def test_login_user_missing_security():
    """
    Test login fails when user.security is missing
    """

    # Step 1 — Create verified & active user
    user = User.objects.create_user(
        username="nosec",
        email="nosec@example.com",
        password="StrongPass123!",
        is_verified=True,
        is_active=True
    )

    # Step 2 — Remove security attribute safely
    user.security = None

    # Step 3 — Patch authenticate
    with patch("accounts.services.auth.login_service.authenticate", return_value=user):

        # Step 4 — Expect ServiceException
        with pytest.raises(ServiceException):
            LoginService.login_user(user.email, "StrongPass123!", "127.0.0.1")


# =============================================================
# Test Case 7: Unexpected Internal Error
# =============================================================
@pytest.mark.django_db
def test_login_user_unexpected_exception():
    """
    Test unexpected errors are wrapped into InternalServerException
    """

    # Step 1 — Patch authenticate to raise unexpected error
    with patch(
        "accounts.services.auth.login_service.authenticate",
        side_effect=Exception("DB error")
    ):

        # Step 2 — Expect InternalServerException
        with pytest.raises(InternalServerException) as excinfo:
            LoginService.login_user("any@example.com", "any", "127.0.0.1")

    # Step 3 — Validate wrapped message
    assert "Login failed due to an unexpected error" in str(excinfo.value)
