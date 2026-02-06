from django.urls import path
from accounts.views.auth import (
    RegisterView,
    VerifyEmailView,
    LoginView,
    LogoutView,
    RefreshTokenView,
    ForgotPasswordView,
    ResetPasswordView,
    ChangePasswordView,
    ResendEmailView,
    Setup2FAView,
    Enable2FAView,
    Verify2FAView,
    Disable2FAView,
    CurrentUserView, 
    UpdateAvatarView,
    ChangeRoleView,
    GoogleLoginView,
    GoogleLoginCallbackView,
    GitHubLoginView,
    GitHubLoginCallbackView
)

urlpatterns = [
    # ------------------------
    # Authentication
    # ------------------------
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh-token/', RefreshTokenView.as_view(), name='refresh-token'),

    # ------------------------
    # Password Management
    # ------------------------
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),

    # ------------------------
    # Email Verification
    # ------------------------
    path('resend-email/', ResendEmailView.as_view(), name='resend-email'),

    # ------------------------
    # User Profile
    # ------------------------
    path('me/', CurrentUserView.as_view(), name='current-user'),
    path('me/avatar/', UpdateAvatarView.as_view(), name='update-avatar'),
    
    # ------------------------
    # Google OAuth
    # ------------------------
    path("google/login/", GoogleLoginView.as_view(), name="google-login"),
    path("google/callback/", GoogleLoginCallbackView.as_view(), name="google-callback"),

    # ------------------------
    # GitHub OAuth
    # ------------------------
    path("github/login/", GitHubLoginView.as_view(), name="github-login"),
    path("github/callback/", GitHubLoginCallbackView.as_view(), name="github-callback"),

    # ------------------------
    # Role Management
    # ------------------------
    path('change-role/', ChangeRoleView.as_view(), name='change-role'),

    # ------------------------
    # Two-Factor Authentication (2FA)
    # ------------------------
    path('me/2fa/setup/', Setup2FAView.as_view(), name='2fa-setup'),
    path('me/2fa/enable/', Enable2FAView.as_view(), name='2fa-enable'),
    path('me/2fa/verify/', Verify2FAView.as_view(), name='2fa-verify'),
    path('me/2fa/disable/', Disable2FAView.as_view(), name='2fa-disable'),
]
