# accounts/services/oauth_service.py
from django.conf import settings
from django.db import transaction
from urllib.parse import urlencode
import requests
import logging

from accounts.models import User
from core.constants.auth import LOGIN_GOOGLE, LOGIN_GITHUB
from accounts.services.base import BaseService
from accounts.services.jwt import generate_jwt_tokens
from core.exceptions.base import ValidationException, InternalServerException, ServiceException

class GoogleOAuthService(BaseService):
    """Service layer for Google OAuth."""

    @staticmethod
    def get_auth_url() -> str:
        return (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"response_type=code&client_id={settings.GOOGLE_CLIENT_ID}"
            f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
            f"&scope=openid%20email%20profile&access_type=offline&prompt=consent"
        )

    @classmethod
    def handle_callback(cls, code: str, frontend_url: str) -> str:
        try:
            # Exchange code for access token
            token_res = requests.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                    "grant_type": "authorization_code",
                },
            ).json()
            access_token = token_res.get("access_token")
            if not access_token:
                raise ServiceException("Failed to get access token from Google")

            # Get user info
            user_info = requests.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            ).json()

            email = user_info.get("email")
            username = user_info.get("name")
            if not email:
                raise ValidationException("Email not available from Google")

            # Create/update user and generate tokens
            with transaction.atomic():
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={"username": username, "is_verified": True, "login_type": LOGIN_GOOGLE},
                )
                if not created:
                    user.username = username
                    user.is_verified = True
                    user.save(update_fields=["username", "is_verified"])

                access_jwt, refresh_jwt = generate_jwt_tokens(user)

            params = urlencode({"access": access_jwt, "refresh": refresh_jwt})
            return f"{frontend_url}/google/callback?{params}"

        except Exception as exc:
            cls.logger().error("Error during Google OAuth", exc_info=True)
            raise InternalServerException("Failed Google OAuth login.") from exc


class GitHubOAuthService(BaseService):
    """Service layer for GitHub OAuth."""

    @staticmethod
    def get_auth_url() -> str:
        return (
            f"https://github.com/login/oauth/authorize"
            f"?client_id={settings.GITHUB_CLIENT_ID}"
            f"&redirect_uri={settings.GITHUB_REDIRECT_URI}"
            f"&scope=user:email"
        )

    @classmethod
    def handle_callback(cls, code: str, frontend_url: str) -> str:
        try:
            # Exchange code for access token
            token_res = requests.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "client_id": settings.GITHUB_CLIENT_ID,
                    "client_secret": settings.GITHUB_CLIENT_SECRET,
                    "code": code,
                },
                headers={"Accept": "application/json"},
            ).json()
            access_token = token_res.get("access_token")
            if not access_token:
                raise ServiceException("Failed to get access token from GitHub")

            # Get user info
            user_info = requests.get(
                "https://api.github.com/user",
                headers={"Authorization": f"token {access_token}"},
            ).json()
            email = user_info.get("email") or f"{user_info.get('id')}@github.com"
            username = user_info.get("login")

            # Create/update user and generate tokens
            with transaction.atomic():
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={"username": username, "is_verified": True, "login_type": LOGIN_GITHUB},
                )
                if not created:
                    user.username = username
                    user.is_verified = True
                    user.save(update_fields=["username", "is_verified"])

                access_jwt, refresh_jwt = generate_jwt_tokens(user)

            params = urlencode({"access": access_jwt, "refresh": refresh_jwt, "username": username})
            return f"{frontend_url}/github/callback?{params}"

        except Exception as exc:
            cls.logger().error("Error during GitHub OAuth", exc_info=True)
            raise InternalServerException("Failed GitHub OAuth login.") from exc
