from drf_spectacular.utils import OpenApiExample, extend_schema, OpenApiResponse
from accounts.serializers.auth.auth import LoginSerializer

# =============================================================
# Login Swagger
# =============================================================

# ----------------------------
# Request Example
# ----------------------------
login_request_example = OpenApiExample(
    name="User Login Request",
    summary="Login using email and password",
    value={
        "email": "arjun.mehta@protonmail.com",
        "password": "StrongPass@2025"
    },
    request_only=True,
)

# ----------------------------
# Response Example
# ----------------------------
login_success_example = OpenApiExample(
    name="Login Success Response",
    summary="Successful login with JWT tokens",
    value={
        "success": True,
        "message": "Login successful.",
        "data": {
            "user": {
                "id": "5fe5027b-2745-411b-88ff-997988864366",
                "email": "arjun.mehta@protonmail.com",
                "username": "arjun_mehta",
                "role": "USER",
                "is_verified": True,
                "avatar_url": "https://ui-avatars.com/api/?name=demo&size=200",
                "presence": {
                    "is_online": False,
                    "last_seen": None,
                    "status_message": "Hey there! I am using Config Hub."
                },
                "security": {
                    "is_2fa_enabled": False
                }
            },
            "tokens": {
                "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    },
    response_only=True,
)

# ----------------------------
# Extend Schema for Login View
# ----------------------------
login_schema = extend_schema(
    request=LoginSerializer,
    examples=[login_request_example],
    responses={
        200: OpenApiResponse(
            description="User logged in successfully",
            examples=[login_success_example],
        ),
        401: OpenApiResponse(description="Invalid credentials"),
        403: OpenApiResponse(description="Email not verified"),
    },
    description=(
        "Authenticate a user using email and password. "
        "Returns JWT access and refresh tokens upon successful login. "
        "User must verify their email before logging in."
    ),
)
