from rest_framework import serializers

# =============================================================
# OAuth Callback Serializer
# =============================================================
class OAuthCallbackSerializer(serializers.Serializer):
    """
    Serializer for handling OAuth callback requests.

    Attributes:
        code (str): The authorization code returned by the OAuth provider.
    """
    code = serializers.CharField(
        required=True,
        help_text="Authorization code returned by OAuth provider (Google/GitHub)."
    )


# =============================================================
# Empty Serializer
# =============================================================
class EmptySerializer(serializers.Serializer):
    """
    Serializer for endpoints that do not require any input data.
    Can be used for simple GET endpoints that only return a URL or message.
    """
    pass
