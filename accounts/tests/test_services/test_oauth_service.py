import pytest
from unittest.mock import patch, MagicMock

from django.conf import settings
from django.contrib.auth import get_user_model

from accounts.services.auth import GoogleOAuthService, GitHubOAuthService
from core.exceptions import InternalServerException, ValidationException

User = get_user_model()

def test_google_auth_url():
    url = GoogleOAuthService.get_auth_url()

    assert "accounts.google.com" in url
    assert "client_id=" in url
    assert "redirect_uri=" in url
    assert "scope=openid+email+profile" in url
    
@pytest.mark.django_db
@patch("accounts.services.auth.oauth_service.generate_tokens")
@patch("accounts.services.auth.oauth_service.requests.get")
@patch("accounts.services.auth.oauth_service.requests.post")
def test_google_oauth_success(
    mock_post,
    mock_get,
    mock_generate_tokens,
):
    mock_post.return_value = MagicMock(
        status_code=200,
        json=lambda: {
            "access_token": "google-access-token",
            "id_token": "google-id-token",
        },
        raise_for_status=lambda: None,
    )

    mock_get.return_value = MagicMock(
        status_code=200,
        json=lambda: {
            "email": "user@gmail.com",
            "name": "Test User",
            "sub": "google-123",
        },
        raise_for_status=lambda: None,
    )

    mock_generate_tokens.return_value = ("access.jwt", "refresh.jwt")

    frontend_url = "http://frontend.test"

    redirect_url = GoogleOAuthService.handle_callback(
        code="valid-code",
        frontend_url=frontend_url,
    )

    user = User.objects.get(email="user@gmail.com")

    assert user.is_verified is True
    assert redirect_url.startswith(f"{frontend_url}/google/callback")
    assert "access=access.jwt" in redirect_url
    assert "refresh=refresh.jwt" in redirect_url

@patch("accounts.services.auth.oauth_service.requests.post")
def test_google_oauth_missing_access_token(mock_post):
    mock_post.return_value = MagicMock(
        status_code=200,
        json=lambda: {},
        raise_for_status=lambda: None,
    )
    
    with pytest.raises(InternalServerException):
        GoogleOAuthService.handle_callback(
            code="bad-code",
            frontend_url="http://frontend.test",
        )

@patch("accounts.services.auth.oauth_service.requests.post")
@patch("accounts.services.auth.oauth_service.requests.get")
def test_google_oauth_missing_email(mock_get, mock_post):
    mock_post.return_value = MagicMock(
        json=lambda: {"access_token": "token"},
        raise_for_status=lambda: None,
    )
    
    mock_get.return_value = MagicMock(
        json=lambda: {"name": "No Email User"},
        raise_for_status=lambda: None,
    )
    
    with pytest.raises(InternalServerException):
        GoogleOAuthService.handle_callback(
            code="code",
            frontend_url="http://frontend.test",
        )

def test_github_auth_url():
    url = GitHubOAuthService.get_auth_url()

    assert "github.com/login/oauth/authorize" in url
    assert "client_id=" in url
    assert "redirect_uri=" in url
    assert "scope=user%3Aemail" in url    
    
@pytest.mark.django_db
@patch("accounts.services.auth.oauth_service.generate_tokens")
@patch("accounts.services.auth.oauth_service.requests.get")
@patch("accounts.services.auth.oauth_service.requests.post")
def test_github_oauth_success(mock_post, mock_get, mock_generate_tokens):
    # Mock access token response
    mock_post.return_value = MagicMock(
        status_code=200,
        json=lambda: {"access_token": "github-access-token"},
        raise_for_status=lambda: None
    )

    # Mock GitHub user info response
    mock_get.return_value = MagicMock(
        status_code=200,
        json=lambda: {
            "login": "githubuser",
            "id": 123,
            "email": "user@github.com"
        },
        raise_for_status=lambda: None
    )

    # Mock JWT token generation
    mock_generate_tokens.return_value = ("access.jwt", "refresh.jwt")

    frontend_url = "http://frontend.test"

    redirect_url = GitHubOAuthService.handle_callback(
        code="valid-code",
        frontend_url=frontend_url,
    )

    user = User.objects.get(email="user@github.com")

    assert user.is_verified is True
    assert redirect_url.startswith(f"{frontend_url}/github/callback")
    assert "access=access.jwt" in redirect_url
    assert "refresh=refresh.jwt" in redirect_url
    assert "username=githubuser" in redirect_url

@patch("accounts.services.auth.oauth_service.requests.post")
def test_github_oauth_missing_access_token(mock_post):
    mock_post.return_value = MagicMock(
        status_code=200,
        json=lambda: {},  
        raise_for_status=lambda: None
    )

    with pytest.raises(InternalServerException):
        GitHubOAuthService.handle_callback(
            code="bad-code",
            frontend_url="http://frontend.test"
        )

@pytest.mark.django_db
@patch("accounts.services.auth.oauth_service.requests.post")
@patch("accounts.services.auth.oauth_service.requests.get")
def test_github_oauth_missing_email(mock_get, mock_post):
    # Valid access token
    mock_post.return_value = MagicMock(
        status_code=200,
        json=lambda: {"access_token": "token"},
        raise_for_status=lambda: None
    )

    # GitHub response with no email
    mock_get.return_value = MagicMock(
        status_code=200,
        json=lambda: {"login": "userlogin", "id": 456, "email": None},
        raise_for_status=lambda: None
    )

    frontend_url = "http://frontend.test"

    redirect_url = GitHubOAuthService.handle_callback(
        code="code",
        frontend_url=frontend_url
    )

    user = User.objects.get(email="456@github.local")

    assert user.username == "userlogin"
    assert user.is_verified is True
    assert redirect_url.startswith(f"{frontend_url}/github/callback")
    assert "access=" in redirect_url
    assert "refresh=" in redirect_url
    assert "username=userlogin" in redirect_url
    