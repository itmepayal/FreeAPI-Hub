import pytest
from unittest.mock import MagicMock
from django.test import RequestFactory
from accounts.services.auth import ResendEmailService
from core.exceptions import PermissionDeniedException, InternalServerException

# ==========================================================
# Test: User Not Found
# ==========================================================
@pytest.mark.django_db
def test_resend_email_user_not_found(fake_request):
    # Step 1 — Call service with non-existent email
    ResendEmailService.resend_verification_email(
        "no@user.com",
        fake_request
    )
    # Nothing to assert because it silently returns for non-existing users


# ==========================================================
# Test: Inactive User
# ==========================================================
@pytest.mark.django_db
def test_resend_email_inactive_user(user_factory, fake_request):
    # Step 1 — Create inactive user via fixture
    user = user_factory(is_active=False, is_verified=False)

    # Step 2 — Should raise PermissionDeniedException
    with pytest.raises(PermissionDeniedException):
        ResendEmailService.resend_verification_email(user.email, fake_request)


# ==========================================================
# Test: Success
# ==========================================================
@pytest.mark.django_db
def test_resend_email_success(user_factory, set_security_flags, mock_send_email, mock_on_commit, fake_request):
    # Step 1 — Create active, unverified user
    user = user_factory(is_active=True, is_verified=False)

    # Step 2 — Apply security flags if needed
    security = set_security_flags(user)

    # Step 3 — Mock token generation
    security.generate_email_verification_token = MagicMock(return_value="rawtoken123")

    # Step 4 — Call service
    ResendEmailService.resend_verification_email(user.email, fake_request)

    # Step 5 — Assert email was scheduled to send
    assert mock_on_commit.called
    mock_send_email.assert_not_called()  # Because it's called inside on_commit


# ==========================================================
# Test: Token Generation Failure
# ==========================================================
@pytest.mark.django_db
def test_token_generation_failure(user_factory, mock_security_get, fake_request):
    # Step 1 — Create user
    user = user_factory(is_active=True, is_verified=False)

    # Step 2 — Mock security to throw exception
    sec = MagicMock()
    sec.generate_email_verification_token.side_effect = Exception("boom")
    mock_security_get.objects.get.return_value = sec

    # Step 3 — Expect InternalServerException
    with pytest.raises(InternalServerException):
        ResendEmailService.resend_verification_email(user.email, fake_request)

# ==========================================================
# Test: send_verification_email Utility
# ==========================================================
# @pytest.mark.django_db
# def test_send_verification_email(user_factory, mock_send_email):
#     # Step 1 — Create user
#     user = user_factory(is_active=True, is_verified=False)

#     # Step 2 — Call utility directly
#     ResendEmailService.send_verification_email(user, "token123")

#     # Step 3 — Assert email was sent
#     mock_send_email.assert_called_once()
