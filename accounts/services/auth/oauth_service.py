# =============================================================
# Python
# =============================================================
from urllib.parse import urlencode
import requests

# =============================================================
# Django
# =============================================================
from django.conf import settings
from django.db import transaction

# =============================================================
# Local Models
# =============================================================
from accounts.models import User, UserSecurity, UserPresence

# =============================================================
# Core Constants
# =============================================================
from core.constants.auth import LOGIN_GOOGLE

# =============================================================
# Core Utilities
# =============================================================
from core.exceptions import ValidationException, InternalServerException, ServiceException
from accounts.helpers import generate_tokens

# =============================================================
# Base Service
# =============================================================
from accounts.services.base import BaseService


# =============================================================
# Google OAuth Service
# =============================================================
class GoogleOAuthService(BaseService):

    # ---------------------------------------------------------
    # Auth URL Builder
    # ---------------------------------------------------------
    @staticmethod
    def get_auth_url() -> str:
        """Build Google OAuth authorization URL"""

        params = {
            "response_type": "code",
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent",
        }

        return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"

    # ---------------------------------------------------------
    # Callback Handler
    # ---------------------------------------------------------
    @classmethod
    def handle_callback(cls, code: str, frontend_url: str) -> str:
        try:
            # Step 1 — Exchange code for access token
            token_res = requests.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                    "grant_type": "authorization_code",
                },
                timeout=10,
            )
            token_res.raise_for_status()
            token_data = token_res.json()

            access_token = token_data.get("access_token")
            if not access_token:
                raise ServiceException("Google access token missing")

            # Step 2 — Fetch Google user info
            info_res = requests.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10,
            )
            info_res.raise_for_status()
            user_info = info_res.json()

            email = user_info.get("email")
            username = user_info.get("name") or email.split("@")[0]

            if not email:
                raise ValidationException("Email not provided by Google")

            # Step 3 — Create/update user inside transaction
            with transaction.atomic():

                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        "username": username,
                        "is_verified": True,
                        "login_type": LOGIN_GOOGLE,
                    },
                )

                if not created:
                    user.username = username
                    user.is_verified = True
                    user.login_type = LOGIN_GOOGLE
                    user.save(update_fields=["username", "is_verified", "login_type"])

                # Step 4 — Ensure related records exist
                UserSecurity.objects.get_or_create(user=user)
                UserPresence.objects.get_or_create(user=user)

                # Step 5 — Generate JWT tokens
                access_jwt, refresh_jwt = generate_tokens(user)

                cls.logger().info(
                    "Google OAuth login successful",
                    extra={"user_id": user.id, "email": user.email},
                )

            # Step 6 — Build frontend redirect URL
            params = urlencode({
                "access": access_jwt,
                "refresh": refresh_jwt,
            })

            return f"{frontend_url}/google/callback?{params}"

        except Exception as exc:
            cls.logger().error("Google OAuth failed", exc_info=True)
            raise InternalServerException("Google OAuth login failed.") from exc

# =============================================================
# GitHub OAuth Service
# =============================================================
class GitHubOAuthService(BaseService):

    @staticmethod
    def get_auth_url() -> str:
        """Build GitHub OAuth authorization URL"""

        params = {
            "client_id": settings.GITHUB_CLIENT_ID,
            "redirect_uri": settings.GITHUB_REDIRECT_URI,
            "scope": "user:email",
        }

        return f"https://github.com/login/oauth/authorize?{urlencode(params)}"

    @classmethod
    def handle_callback(cls, code: str, frontend_url: str) -> str:
        try:
            # Step 1 — Exchange code for access token
            token_res = requests.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "client_id": settings.GITHUB_CLIENT_ID,
                    "client_secret": settings.GITHUB_CLIENT_SECRET,
                    "code": code,
                },
                headers={"Accept": "application/json"},
                timeout=10,
            )
            token_res.raise_for_status()
            token_data = token_res.json()

            access_token = token_data.get("access_token")
            if not access_token:
                raise ServiceException("GitHub access token missing")

            # Step 2 — Fetch GitHub user info
            info_res = requests.get(
                "https://api.github.com/user",
                headers={"Authorization": f"token {access_token}"},
                timeout=10,
            )
            info_res.raise_for_status()
            user_info = info_res.json()

            username = user_info.get("login")
            email = user_info.get("email") or f"{user_info['id']}@github.local"

            # Step 3 — Create/update user
            with transaction.atomic():

                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        "username": username,
                        "is_verified": True,
                        "login_type": LOGIN_GITHUB,
                    },
                )

                if not created:
                    user.username = username
                    user.is_verified = True
                    user.login_type = LOGIN_GITHUB
                    user.save(update_fields=["username", "is_verified", "login_type"])

                UserSecurity.objects.get_or_create(user=user)
                UserPresence.objects.get_or_create(user=user)

                # Step 4 — Generate tokens
                access_jwt, refresh_jwt = generate_tokens(user)

                cls.logger().info(
                    "GitHub OAuth login successful",
                    extra={"user_id": user.id, "email": user.email},
                )

            # Step 5 — Build redirect URL
            params = urlencode({
                "access": access_jwt,
                "refresh": refresh_jwt,
                "username": username,
            })

            return f"{frontend_url}/github/callback?{params}"

        except Exception as exc:
            cls.logger().error("GitHub OAuth failed", exc_info=True)
            raise InternalServerException("GitHub OAuth login failed.") from exc
