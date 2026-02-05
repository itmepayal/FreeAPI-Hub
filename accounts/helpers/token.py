# =============================================================
# Python Standard Library
# =============================================================
from datetime import timedelta

# =============================================================
# Third Party
# =============================================================
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

# =============================================================
# Standard Access + Refresh Token Generator
# =============================================================
def generate_tokens(user) -> dict:
    # Step 1 — Create refresh token for authenticated user
    refresh = RefreshToken.for_user(user)

    # Step 2 — Return both tokens as strings
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


# =============================================================
# Custom Temporary 2FA Token Class
# =============================================================
class TwoFAToken(AccessToken):
    # Step 1 — Set custom token type claim
    token_type = "2fa"

    # Step 2 — Limit token lifetime to short window
    lifetime = timedelta(minutes=5)


# =============================================================
# Temporary 2FA Token Generator
# =============================================================
def generate_2fa_token(user) -> str:
    # Step 1 — Create custom 2FA token for user
    token = TwoFAToken.for_user(user)

    # Step 2 — Return encoded JWT string
    return str(token)
