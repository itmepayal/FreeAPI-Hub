from rest_framework_simplejwt.tokens import RefreshToken
from core.exceptions.base import InternalServerException


def generate_jwt_tokens(user):
    try:
        refresh = RefreshToken.for_user(user)

        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        return access_token, refresh_token

    except Exception as exc:
        raise InternalServerException("Failed to generate JWT tokens.") from exc