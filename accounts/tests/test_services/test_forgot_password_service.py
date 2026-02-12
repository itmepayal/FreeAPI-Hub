# =============================================================
# Pytest: ForgotPasswordService
# =============================================================
import pytest
from django.test import RequestFactory
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, MagicMock

# =============================================================
# Local Models
# =============================================================
from django.contrib.auth import get_user_model
from accounts.models import UserSecurity

# =============================================================
# Core Exceptions
# =============================================================
from core.exceptions import (
    InvalidTokenException,
    OperationNotAllowedException,
)

# =============================================================
# Services
# =============================================================
from accounts.services.auth.forgot_password_service import ForgotPasswordService

User = get_user_model()

# =============================================================
# Test Case 1: Success Path
# =============================================================
@pytest.mark.django_db
@patch.object(ForgotPasswordService, "send_password_reset_email")
def test_send_reset_email_success(mock_send_password_email):
    factory = RequestFactory()

    user = User.objects.create(
        username="testuser",
        email="test@example.com",
        is_verified=True
    )

    request = factory.post("/forgot-password", REMOTE_ADDR="127.0.0.1")

    with patch(
        "django.db.transaction.on_commit",
        side_effect=lambda fn: fn()
    ):
        ForgotPasswordService.send_reset_email(
            email=user.email,
            request=request
        )

    security = UserSecurity.objects.get(user=user)

    assert security.forgot_password_token is not None
    assert security.forgot_password_expiry is not None
    mock_send_password_email.assert_called_once()

@pytest.mark.django_db
@patch.object(ForgotPasswordService, "send_password_reset_email")
def test_send_reset_email_non_existing_user(mock_send_password_email):
    factory = RequestFactory()
    request = factory.post("/forgot-password")

    ForgotPasswordService.send_reset_email(
        email="unknown@example.com",
        request=request
    )

    mock_send_password_email.assert_not_called()

@pytest.mark.django_db
@patch.object(ForgotPasswordService, "send_password_reset_email")
def test_security_row_created_if_missing(mock_send_password_email):
    factory = RequestFactory()

    user = User.objects.create(
        username="testuser",
        email="test@example.com",
        is_verified=True
    )

    UserSecurity.objects.filter(user=user).delete()

    request = factory.post("/forgot-password")

    with patch(
        "django.db.transaction.on_commit",
        side_effect=lambda fn: fn()
    ):
        ForgotPasswordService.send_reset_email(
            email=user.email,
            request=request
        )

    assert UserSecurity.objects.filter(user=user).exists()
    mock_send_password_email.assert_called_once()
    