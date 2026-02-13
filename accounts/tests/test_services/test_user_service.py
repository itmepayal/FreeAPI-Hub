# =============================================================
# Third-Party Imports
# =============================================================
import pytest
from unittest.mock import patch, MagicMock

# =============================================================
# Local Service Imports
# =============================================================
from accounts.services.auth.user_service import UserService

# =============================================================
# Core Exceptions
# =============================================================
from core.exceptions.base import ServiceException, ExternalServiceException

# ==========================================================
# Test: Get Current User Profile — Success
# ==========================================================
@pytest.mark.django_db
@patch("accounts.services.auth.user_service.UserSerializer")
def test_get_current_user_profile_success(mock_serializer, user_factory):
    # Step 1 — Create a user
    user = user_factory(email="test@test.com")

    # Step 2 — Mock serializer
    mock_serializer.return_value.data = {
        "id": user.id,
        "email": user.email
    }

    # Step 3 — Execute service
    data = UserService.get_current_user_profile(user)

    # Step 4 — Assert
    assert data["email"] == user.email
    mock_serializer.assert_called_once_with(user)

# ==========================================================
# Test: Get Current User Profile — Failure
# ==========================================================
@pytest.mark.django_db
@patch("accounts.services.auth.user_service.UserSerializer")
def test_get_current_user_profile_failure(mock_serializer, user_factory):
    user = user_factory(email="test@test.com")

    mock_serializer.side_effect = Exception("boom")

    with pytest.raises(ServiceException):
        UserService.get_current_user_profile(user)

# ==========================================================
# Test: Update Avatar — Success (Dict)
# ==========================================================
@pytest.mark.django_db
@patch("accounts.services.auth.user_service.upload_to_cloudinary")
def test_update_avatar_success_dict(mock_upload, user_factory):
    user = user_factory()
    mock_upload.return_value = {"secure_url": "https://cdn/avatar.jpg"}

    file_mock = MagicMock()
    url = UserService.update_avatar(user, file_mock)

    assert url == "https://cdn/avatar.jpg"
    user.refresh_from_db()
    assert user.avatar == url

# ==========================================================
# Test: Update Avatar — Success (String)
# ==========================================================
@pytest.mark.django_db
@patch("accounts.services.auth.user_service.upload_to_cloudinary")
def test_update_avatar_success_string(mock_upload, user_factory):
    user = user_factory()
    mock_upload.return_value = "https://cdn/avatar2.jpg"

    file_mock = MagicMock()
    url = UserService.update_avatar(user, file_mock)

    assert url == "https://cdn/avatar2.jpg"

# ==========================================================
# Test: Update Avatar — Upload Failure
# ==========================================================
@pytest.mark.django_db
@patch("accounts.services.auth.user_service.upload_to_cloudinary")
def test_update_avatar_upload_failure(mock_upload, user_factory):
    user = user_factory()
    mock_upload.side_effect = Exception("cloud error")

    with pytest.raises(ExternalServiceException):
        UserService.update_avatar(user, MagicMock())
