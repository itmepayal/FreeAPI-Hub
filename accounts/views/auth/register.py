# =============================================================
# Django
# =============================================================
from django.db import transaction

# =============================================================
# Django REST Framework
# =============================================================
from rest_framework import generics, status, permissions

# =============================================================
# Local App
# =============================================================
from accounts.serializers.auth import RegisterSerializer, UserSerializer
from accounts.swagger.auth import register_schema
from accounts.services.auth import RegisterService

# =============================================================
# Core Utilities
# =============================================================
from core.logging.logger import get_logger
from core.utils.helpers import get_client_ip
from core.utils.responses import api_response

# =============================================================
# Logger
# =============================================================
logger = get_logger(__name__)


# =============================================================
# Register View
# =============================================================
@register_schema
class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint.

    Flow:
    1. Validate incoming registration data
    2. Create user inside a DB transaction
    3. Generate email verification token
    4. Send verification email (outside transaction)
    5. Return created user payload

    Design Notes:
    - User creation and security updates are atomic
    - Email sending is intentionally executed AFTER commit
    - Business logic is delegated to service layer
    """

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Handle user registration request.
        """
        # Validate request payload
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # Atomic block ensures user + security data
            # are either fully created or fully rolled back
            with transaction.atomic():
                # Create user
                user = serializer.save()

                # Audit log for traceability
                logger.info(
                    "New user registered",
                    extra={
                        "user_id": user.id,
                        "email": user.email,
                        "ip": get_client_ip(request),
                    },
                )

                # Generate and persist email verification token
                raw_token = RegisterService.create_email_verification(user)

        except Exception as exc:
            # Any failure here rolls back the transaction
            logger.error(
                "User registration failed",
                extra={
                    "email": request.data.get("email"),
                    "error": str(exc),
                },
            )

            return api_response(
                message="Registration failed. Please try again.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Send verification email AFTER successful commit
        # (email failures should not rollback user creation)
        try:
            RegisterService.send_verification_email(user, raw_token)
        except Exception as exc:
            # Log warning only — user is already created
            logger.warning(
                "Verification email sending failed",
                extra={
                    "user_id": user.id,
                    "email": user.email,
                    "error": str(exc),
                },
            )

        # API Response
        return api_response(
            message="User registered successfully. Please verify your email.",
            data={
                "user": UserSerializer(user).data,
            },
            status_code=status.HTTP_201_CREATED,
        )
