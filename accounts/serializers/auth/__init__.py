# =============================================================
# Import all serializers from individual modules
# =============================================================

from .auth import LoginSerializer, RegisterSerializer, RefreshTokenSerializer, ForgotPasswordSerializer, VerifyEmailSerializer, ResendEmailSerializer
from .password import ChangePasswordSerializer, ResetPasswordSerializer
from .two_factor import Enable2FASerializer, Disable2FASerializer, Verify2FASerializer
from .user import UserSerializer, UserPresenceSerializer, UserSecuritySerializer, UpdateAvatarSerializer
from .admin import ChangeRoleSerializer

# =============================================================
# Explicitly define what is exported when importing *
# =============================================================
__all__ = [
    "LoginSerializer",
    "RegisterSerializer",
    "LogoutSerializer",
    "RefreshTokenSerializer",
    "VerifyEmailSerializer",
    "ResendEmailSerializer",
    "ChangePasswordSerializer",
    "ResetPasswordSerializer",
    "ForgotPasswordSerializer",
    "Enable2FASerializer",
    "Disable2FASerializer",
    "Verify2FASerializer",
    "Setup2FASerializer",
    "UserSerializer",
    "UserPresenceSerializer",
    "UserSecuritySerializer",
    "ChangeRoleSerializer",
    "UpdateAvatarSerializer"
]
