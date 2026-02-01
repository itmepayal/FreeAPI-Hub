from drf_spectacular.utils import OpenApiExample, extend_schema, OpenApiResponse
from accounts.serializers.auth import (
    RegisterSerializer, 
)

# =============================================================
# Register Swagger
# =============================================================
# ----------------------------
# Request Example
# ----------------------------
register_request_example = OpenApiExample(
    name="User Registration Request",
    summary="Example payload for registering a new user",
    value={
    "email": "arjun.mehta@protonmail.com",
    "username": "arjun_mehta",
    "password": "StrongPass@2025",
    },
    request_only=True
)

# ----------------------------
# Response Example
# ----------------------------
register_success_example = OpenApiExample(
    name="User Registration Success Response",
    summary="Example response after successful user registration",
    value={
        "success": True,
        "message": "User registered successfully. Please verify your email.",
        "data": {
            "user": {
                "id": "5fe5027b-2745-411b-88ff-997988864366",
                "email": "arjun.mehta@protonmail.com",
                "username": "arjun.mehta",
                "role": "USER",
                "is_verified": False,
                "avatar_url": "https://ui-avatars.com/api/?name=demo&size=200",
                "presence": {
                    "is_online": False,
                    "last_seen": None,
                    "status_message": "Hey there! I am using config Hub."
                },
                "security": {
                    "is_2fa_enabled": False
                }
            }
        }
    },
    response_only=True
)

# ----------------------------
# Extend Schema for Registration View
# ----------------------------
register_schema = extend_schema(
    request=RegisterSerializer,
    examples=[register_request_example],
    responses={
        201: OpenApiResponse(
            description="User registered successfully",
            examples=[register_success_example]
        )
    },
    description=(
        "Register a new user account. "
        "An email verification link is sent to the user's email address. "
        "Returns the newly created user object with default presence and security settings."
    )
)
