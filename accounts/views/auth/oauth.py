# =============================================================
# Django REST Framework
# =============================================================
from rest_framework import generics, status, permissions
from django.shortcuts import redirect
from django.conf import settings

# =============================================================
# Local App
# =============================================================
from accounts.serializers.auth import OAuthCallbackSerializer, EmptySerializer
from accounts.services.auth import GoogleOAuthService, GitHubOAuthService

# =============================================================
# Core Utilities
# =============================================================
from core.utils.responses import api_response
from core.logging.logger import get_logger

# =============================================================
# Logger
# =============================================================
logger = get_logger(__name__)

# =============================================================
# Google Login View
# =============================================================
class GoogleLoginView(generics.GenericAPIView):
    serializer_class = EmptySerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        # Step 1 — Generate Google OAuth authorization URL
        auth_url = GoogleOAuthService.get_auth_url()

        # Step 2 — Log event
        logger.info("Google OAuth login URL generated")

        # Step 3 — Return standardized API response
        return api_response(
            message="Google login URL generated successfully.",
            data={"auth_url": auth_url},
            status_code=status.HTTP_200_OK,
        )


# =============================================================
# Google OAuth Callback View
# =============================================================
class GoogleLoginCallbackView(generics.GenericAPIView):
    serializer_class = OAuthCallbackSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        # Step 1 — Validate callback query params
        serializer = self.get_serializer(data=request.GET)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data["code"]

        # Step 2 — Delegate OAuth handling to service layer
        redirect_url = GoogleOAuthService.handle_callback(
            code=code,
            frontend_url=settings.FRONTEND_URL,
        )

        # Step 3 — Log redirect
        logger.info("Google OAuth callback successful", extra={"redirect": redirect_url})

        # Step 4 — Redirect user to frontend
        return redirect(redirect_url)

# =============================================================
# GitHub Login View
# =============================================================
class GitHubLoginView(generics.GenericAPIView):
    serializer_class = EmptySerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        # Step 1 — Generate GitHub OAuth authorization URL
        auth_url = GitHubOAuthService.get_auth_url()

        # Step 2 — Log event
        logger.info("GitHub OAuth login URL generated")

        # Step 3 — Return standardized API response
        return api_response(
            message="GitHub login URL generated successfully.",
            data={"auth_url": auth_url},
            status_code=status.HTTP_200_OK,
        )

# =============================================================
# GitHub OAuth Callback View
# =============================================================
class GitHubLoginCallbackView(generics.GenericAPIView):
    serializer_class = OAuthCallbackSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        # Step 1 — Validate callback query params
        serializer = self.get_serializer(data=request.GET)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data["code"]

        # Step 2 — Delegate OAuth handling to service layer
        redirect_url = GitHubOAuthService.handle_callback(
            code=code,
            frontend_url=settings.FRONTEND_URL,
        )

        # Step 3 — Log redirect
        logger.info("GitHub OAuth callback successful", extra={"redirect": redirect_url})

        # Step 4 — Redirect user to frontend
        return redirect(redirect_url)
