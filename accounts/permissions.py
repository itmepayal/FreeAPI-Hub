# =============================================================
# Django REST Framework
# =============================================================
from rest_framework.permissions import BasePermission

# =============================================================
# Third-Party Authentication
# =============================================================
from rest_framework_simplejwt.authentication import JWTAuthentication

# =============================================================
# Core Utilities
# =============================================================
from core.constants.roles import ROLE_SUPERADMIN

# =============================================================
# Custom Permission: Is2FAToken
# =============================================================
class Is2FAToken(BasePermission):
    """
    Permission class to allow access only if the request contains
    a valid JWT token of type '2fa'.

    Responsibilities:
    - Authenticate the request using JWTAuthentication.
    - Verify that the token's type is '2fa'.
    - Attach the authenticated user to `request.user` if valid.
    - Deny access otherwise.
    """

    def has_permission(self, request, view):
        """
        Check if the request has a valid 2FA token.

        Steps:
        1. Authenticate the request using JWTAuthentication.
        2. If authentication fails, deny access.
        3. Extract the user and token from validated credentials.
        4. Attach user to request.
        5. Return True if token type is '2fa', else False.
        """
        auth = JWTAuthentication()
        validated = auth.authenticate(request)

        if not validated:
            # No valid JWT provided
            return False

        user, token = validated
        request.user = user

        return token.get("type") == "2fa"

class IsSuperAdmin(BasePermission):
    """
    Allows access only to authenticated users with SUPERADMIN role.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == ROLE_SUPERADMIN)
