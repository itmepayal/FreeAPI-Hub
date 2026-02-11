# =============================================================
# Pytest: RegisterService
# =============================================================
import pytest
from unittest.mock import patch, MagicMock

# =============================================================
# Local Models
# =============================================================
from accounts.models import User, UserSecurity, UserPresence
from accounts.services.auth import RegisterService

# =============================================================
# Core Exceptions
# =============================================================
from core.exceptions import InternalServerException

# =============================================================
# Test Case 1: Successful Registration
# =============================================================
@pytest.mark.django_db
def test_register_user_success():
    """
    Test successful user registration
    """
    # Step 1 — Prepare validated data
    validated_data = {
        "username": "testUser",
        "email": "test@gmail.com",
        "password": "StrongPassword@123"
    }

    # Step 2 — Mock request object
    mock_request = MagicMock()
    mock_request.META = {"REMOTE_ADDR": "127.0.0.1"}

    # Step 3 — Patch transaction.on_commit to run immediately and patch send_verification_email
    with patch("django.db.transaction.on_commit", side_effect=lambda func: func()), \
         patch.object(RegisterService, "send_verification_email") as mock_send_email:

        # Step 4 — Call the registration service
        user = RegisterService.register_user(validated_data, mock_request)

    # Step 5 — Assertions: user object created correctly
    assert user is not None
    assert user.username == "testUser"
    assert user.email == "test@gmail.com"

    # Step 6 — Assertions: related objects are created
    assert UserSecurity.objects.filter(user=user).exists()
    assert UserPresence.objects.filter(user=user).exists()

    # Step 7 — Assertions: verification email sent
    mock_send_email.assert_called_once()
    sent_user, raw_token = mock_send_email.call_args[0]
    assert sent_user == user
    assert isinstance(raw_token, str)  # token should be a string


# =============================================================
# Test Case 2: DB Failure Raises Exception
# =============================================================
@pytest.mark.django_db
def test_register_user_db_failure_raises_exception():
    """
    Test registration fails if User.objects.create_user raises an exception
    """
    # Step 1 — Prepare validated data
    validated_data = {
        "username": "error_user",
        "email": "error_user@example.com",
        "password": "StrongPass123!"
    }

    # Step 2 — Mock request object
    mock_request = MagicMock()
    mock_request.META = {"REMOTE_ADDR": "127.0.0.1"}

    # Step 3 — Patch create_user to raise an exception
    with patch("accounts.models.User.objects.create_user", side_effect=Exception("DB fail")):
        # Step 4 — Expect InternalServerException
        with pytest.raises(InternalServerException) as excinfo:
            RegisterService.register_user(validated_data, mock_request)

    # Step 5 — Assert custom exception message
    assert "User registration failed." in str(excinfo.value)
