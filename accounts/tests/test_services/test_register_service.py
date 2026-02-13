# =============================================================
# Third-Party Imports
# =============================================================
import pytest
from unittest.mock import patch, MagicMock

# =============================================================
# Local Service Imports
# =============================================================
from accounts.services.auth import RegisterService

# =============================================================
# Core Exceptions
# =============================================================
from core.exceptions import InternalServerException

# =============================================================
# Test: Register User — Success Flow
# =============================================================
@pytest.mark.django_db
def test_register_user_success(
    fake_request,
    validated_data,
    mock_get_ip,
    mock_send_email,
    mock_create_user,
    mock_security_get,
    mock_presence,
    mock_on_commit,
):
    # Step 1 — Prepare fake user object
    fake_user = MagicMock( id=10, email="test@example.com", username="tester")

    # Step 2 — Prepare fake security model with token generator
    fake_security = MagicMock()
    fake_security.generate_email_verification_token.return_value = "raw-token"

    # Step 3 — Configure mocks
    mock_create_user.return_value = fake_user
    mock_security_get.return_value = (fake_security, True)

    # Step 4 — Execute service method
    user = RegisterService.register_user(validated_data, fake_request)

    # Step 5 — Validate results and calls
    assert user == fake_user
    mock_create_user.assert_called_once_with(**validated_data)
    mock_security_get.assert_called_once_with(user=fake_user)
    mock_presence.assert_called_once_with(user=fake_user)
    fake_security.generate_email_verification_token.assert_called_once()
    mock_on_commit.assert_called_once()


# =============================================================
# Test: Register User — Token Generation Failure
# =============================================================
@pytest.mark.django_db
def test_register_user_token_generation_failure(
    fake_request,
    validated_data,
    mock_get_ip,
    mock_create_user,
    mock_security_get,
    mock_presence,
    mock_on_commit,
):
    # Step 1 — Prepare fake user and failing security generator
    fake_user = MagicMock(id=99)
    fake_security = MagicMock()
    fake_security.generate_email_verification_token.side_effect = Exception("boom")

    # Step 2 — Configure mocks
    mock_create_user.return_value = fake_user
    mock_security_get.return_value = (fake_security, True)

    # Step 3 — Execute and expect controlled exception
    with pytest.raises(InternalServerException):
        RegisterService.register_user(validated_data, fake_request)

    # Step 4 — Ensure token generation was attempted
    fake_security.generate_email_verification_token.assert_called_once()


# =============================================================
# Test: Register User — Create User Failure
# =============================================================
@pytest.mark.django_db
def test_create_user_failure(
    fake_request,
    mock_get_ip,
    mock_create_user,
):
    # Step 1 — Force DB/user creation failure
    mock_create_user.side_effect = Exception("db error")

    # Step 2 — Patch logger to verify error logging
    with patch.object(RegisterService, "logger") as mock_logger:

        # Step 3 — Execute and expect controlled exception
        with pytest.raises(InternalServerException):
            RegisterService.register_user(
                {"email": "bad@test.com"},
                fake_request
            )

        # Step 4 — Validate error logging occurred
        mock_logger().error.assert_called_once()


# =============================================================
# Test: Send Verification Email — Delegation Check
# =============================================================
def test_send_verification_email(mock_send_email):

    # Step 1 — Prepare fake user
    user = MagicMock( email="u@test.com", username="user", id=1)

    # Step 2 — Execute email sender
    RegisterService.send_verification_email(user, "TOKEN123")

    # Step 3 — Ensure email service called
    mock_send_email.assert_called_once()


# =============================================================
# Test: Send Verification Email — Link Contains Token
# =============================================================
def test_email_link_contains_token(mock_send_email, settings):

    # Step 1 — Configure settings
    settings.FRONTEND_URL = "https://app.com"
    settings.SENDGRID_EMAIL_VERIFICATION_TEMPLATE_ID = "tmp1"

    # Step 2 — Prepare fake user
    user = MagicMock( email="a@test.com", username="a", id=1)

    # Step 3 — Execute email sender
    RegisterService.send_verification_email(user, "ABC")

    # Step 4 — Extract email payload
    payload = mock_send_email.call_args.kwargs

    # Step 5 — Validate verification link
    assert payload["dynamic_data"]["verify_link"] == \
        "https://app.com/verify-email/ABC"
