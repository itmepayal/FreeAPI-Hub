from rest_framework import generics, permissions
from django.shortcuts import redirect

from accounts.serializers.auth import OAuthCallbackSerializer, EmptySerializer
from accounts.services.auth import GoogleOAuthService, GitHubOAuthService
from core.utils.responses import api_response
from core.logging.logger import get_logger

logger = get_logger(__name__)

class GoogleLoginView(generics.GenericAPIView):
    serializer_class = EmptySerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        url = GoogleOAuthService.get_auth_url()
        logger.info("Google OAuth login URL generated")
        return api_response(message="Google login URL generated", data={"auth_url": url})


class GoogleLoginCallbackView(generics.GenericAPIView):
    serializer_class = OAuthCallbackSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        serializer = self.get_serializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data["code"]

        redirect_url = GoogleOAuthService.handle_callback(code, frontend_url="http://localhost:5173")
        logger.info(f"Redirecting Google user to {redirect_url}")
        return redirect(redirect_url)


class GitHubLoginView(generics.GenericAPIView):
    serializer_class = EmptySerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        url = GitHubOAuthService.get_auth_url()
        logger.info("GitHub OAuth login URL generated")
        return api_response(message="GitHub login URL generated", data={"auth_url": url})


class GitHubLoginCallbackView(generics.GenericAPIView):
    serializer_class = OAuthCallbackSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        serializer = self.get_serializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data["code"]

        redirect_url = GitHubOAuthService.handle_callback(code, frontend_url="http://localhost:5173")
        logger.info(f"Redirecting GitHub user to {redirect_url}")
        return redirect(redirect_url)
