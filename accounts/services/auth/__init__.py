# =============================================================
# Import all auth-related services
# =============================================================
from .login_service import LoginService
from .logout_service import LogoutService
from .register_service import RegisterService
from .refresh_token_service import RefreshTokenService
from .forgot_password_service import ForgotPasswordService
from .reset_password_service import ResetPasswordService
from .change_password_service import ChangePasswordService
from .resend_email_service import ResendEmailService
from .verify_email_service import VerifyEmailService
from .two_factor_service import TwoFactorService
from .user_service import UserService
from .change_role_service import ChangeRoleService
from .oauth_service import GoogleOAuthService, GitHubOAuthService

# =============================================================
# Explicitly define the public API of this package
# =============================================================
__all__ = [
    "LoginService",
    "LogoutService",
    "RegisterService",
    "RefreshTokenService",
    "ForgotPasswordService",
    "ResetPasswordService",
    "ChangePasswordService",
    "ResendEmailService",
    "VerifyEmailService",
    "TwoFactorService",
    "UserService"
]
