from drf_spectacular.utils import OpenApiExample, extend_schema, OpenApiResponse
from accounts.serializers.auth import VerifyEmailSerializer

# =============================================================
# Verify Email Swagger
# =============================================================

# ----------------------------
# Request Example
# ----------------------------
verify_email_request_example = OpenApiExample(
    name="Verify Email Request",
    summary="Verify email using token",
    value={
        "token": "8d84e13ed34af2241ce43c57518d53c5031f125e"
    },
    request_only=True,
)

# ----------------------------
# Response Example
# ----------------------------
verify_email_success_example = OpenApiExample(
    name="Verify Email Success",
    summary="Email verified successfully",
    value={
        "success": True,
        "message": "Email verified successfully.",
        "data": {
            "user": {
                "id": "5fe5027b-2745-411b-88ff-997988864366",
                "email": "arjun.mehta@protonmail.com"
            }
        }
    },
    response_only=True,
)

# ----------------------------
# Extend Schema for Verify Email View
# ----------------------------
verify_email_schema = extend_schema(
    request=VerifyEmailSerializer,
    examples=[verify_email_request_example],
    responses={
        200: OpenApiResponse(
            description="Email verified successfully",
            examples=[verify_email_success_example],
        )
    },
    description=(
        "Verify a user's email address using the verification token sent to their email. "
        "After successful verification, the user's email is marked as verified."
    ),
)
