# =============================================================
# Django REST Framework
# =============================================================
from rest_framework.permissions import BasePermission

# =============================================================
# Third-Party Authentication
# =============================================================
from rest_framework_simplejwt.authentication import JWTAuthentication

# =============================================================
# Custom Permission: Is2FAToken
# =============================================================
class Is2FAToken(BasePermission):
    """
    Permission class to allow access only if request contains
    a valid JWT token with token_type = '2fa'.
    """

    def has_permission(self, request, view):

        # Step 1 — Authenticate request using JWT
        auth = JWTAuthentication()
        validated = auth.authenticate(request)

        if not validated:
            return False

        # Step 2 — Extract user & token
        user, token = validated
        request.user = user

        # Step 3 — Check token type claim
        return token.get("token_type") == "2fa"
    