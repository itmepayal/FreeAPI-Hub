from drf_spectacular.utils import OpenApiExample, extend_schema, OpenApiResponse
from accounts.serializers.auth import RefreshTokenSerializer

# =============================================================
# Logout Swagger
# =============================================================

# ----------------------------
# Request Example
# ----------------------------
logout_request_example = OpenApiExample(
    name="User Logout Request",
    summary="Logout using refresh token",
    value={
        "refresh_token": (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        )
    },
    request_only=True,
)

# ----------------------------
# Response Example
# ----------------------------
logout_success_example = OpenApiExample(
    name="Logout Success Response",
    summary="User logged out successfully",
    value={
        "success": True,
        "message": "Logout successful."
    },
    response_only=True,
)

# ----------------------------
# Extend Schema for Logout View
# ----------------------------
logout_schema = extend_schema(
    request=RefreshTokenSerializer,
    examples=[logout_request_example],
    responses={
        200: OpenApiResponse(
            description="User logged out successfully",
            examples=[logout_success_example],
        ),
        400: OpenApiResponse(description="Invalid or expired refresh token"),
        401: OpenApiResponse(description="Authentication required"),
    },
    description=(
        "Logs out the authenticated user by blacklisting the refresh token. "
        "Once logged out, the refresh token cannot be used again."
    ),
)
