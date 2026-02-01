from drf_spectacular.utils import OpenApiExample, extend_schema, OpenApiResponse
from accounts.serializers.auth import RefreshTokenSerializer

# =============================================================
# Refresh Token Swagger
# =============================================================

# ----------------------------
# Request Example
# ----------------------------
refresh_request_example = OpenApiExample(
    name="Refresh Token Request",
    summary="Refresh access token using refresh token",
    value={
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    },
    request_only=True,
)

# ----------------------------
# Response Example
# ----------------------------
refresh_success_example = OpenApiExample(
    name="Access Token Refresh Success Response",
    summary="New access token generated",
    value={
        "success": True,
        "message": "Access token refreshed successfully.",
        "data": {
            "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        }
    },
    response_only=True,
)

# ----------------------------
# Extend Schema for Refresh Token View
# ----------------------------
refresh_token_schema = extend_schema(
    request=RefreshTokenSerializer,
    examples=[refresh_request_example],
    responses={
        200: OpenApiResponse(
            description="Access token refreshed successfully",
            examples=[refresh_success_example],
        ),
        401: OpenApiResponse(description="Invalid or expired refresh token"),
    },
    description=(
        "Generates a new access token using a valid refresh token. "
        "If the refresh token is expired, invalid, or blacklisted, the request will fail."
    ),
)
