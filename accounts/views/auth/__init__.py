# =============================================================
# Import all auth-related views
# =============================================================
from .register import RegisterView
from .verify_email import VerifyEmailView
from .login import LoginView
from .logout import LogoutView
from .refresh_token import RefreshTokenView
from .forgot_password import ForgotPasswordView
from .reset_password import ResetPasswordView
from .change_password import ChangePasswordView
from .resend_email import ResendEmailView
from .two_factor import Enable2FAView, Disable2FAView, Setup2FAView, Verify2FAView
from .user import CurrentUserView, UpdateAvatarView
from .change_role import ChangeRoleView

# =============================================================
# Explicitly define the public API for easier imports
# =============================================================
__all__ = [
    "RegisterView",
    "VerifyEmailView",
    "LoginView",
    "LogoutView",
    "RefreshTokenView",
    "ForgotPasswordView",
    "ResetPasswordView",
    "ChangePasswordView",
    "ResendEmailView",
    "Enable2FAView",
    "Disable2FAView",
    "Verify2FAView",
    "Setup2FAView",
    "CurrentUserView",
    "UpdateAvatarView",
    "ChangeRoleView"
]
