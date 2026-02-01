from django.urls import path
from accounts.views.auth.register import RegisterView
from accounts.views.auth.email_verification import VerifyEmailView
from accounts.views.auth.login import LoginView
from accounts.views.auth.logout import LogoutView
from accounts.views.auth.refresh_token import RefreshTokenView
from accounts.views.auth.forgot_password import ForgotPasswordView
from accounts.views.auth.reset_password import ResetPasswordView
from accounts.views.auth.change_password import ChangePasswordView
from accounts.views.auth.resend_email import ResendEmailView

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
    # path('me/', CurrentUserView.as_view(), name='current-user'),
    # path('me/avatar/', UpdateAvatarView.as_view(), name='update-avatar'),

    # ------------------------
    # OAuth
    # ------------------------
    # path('google/', GoogleLoginView.as_view(), name='google-login'),
    # path('google/callback/', GoogleLoginCallbackView.as_view(), name='google-callback'),
    # path('github/', GitHubLoginView.as_view(), name='github-login'),
    # path('github/callback/', GitHubLoginCallbackView.as_view(), name='github-callback'),

    # ------------------------
    # Role Management
    # ------------------------
    # path('change-role/', ChangeRoleView.as_view(), name='change-role'),

    # ------------------------
    # 2FA
    # ------------------------
    # path('2fa/setup/', Setup2FAView.as_view(), name='2fa-setup'),
    # path('2fa/enable/', Enable2FAView.as_view(), name='2fa-enable'),
    # path('2fa/disable/', Disable2FAView.as_view(), name='2fa-disable'),
]
