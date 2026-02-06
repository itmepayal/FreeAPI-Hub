# =============================================================
# Django REST Framework
# =============================================================
from rest_framework import serializers


# =============================================================
# OAuth Callback Serializer
# =============================================================
class OAuthCallbackSerializer(serializers.Serializer):
    """
    Handles OAuth provider callback payload.

    Use Case:
    - Google OAuth callback
    - GitHub OAuth callback
    - Third-party auth exchanges

    Validates authorization code returned by provider.
    """

    # ---------------------------------------------------------
    # Authorization Code
    # ---------------------------------------------------------
    code = serializers.CharField(
        required=True,
        help_text="Authorization code returned by OAuth provider (Google/GitHub).",
    )


# =============================================================
# Empty Serializer
# =============================================================
class EmptySerializer(serializers.Serializer):
    """
    Used for endpoints that accept no request body.

    Common Uses:
    - Redirect URL generators
    - Health checks
    - OAuth start endpoints
    - Simple trigger endpoints
    """

    # No input fields required
    pass
