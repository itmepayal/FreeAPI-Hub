# =============================================================
# Django REST Framework
# =============================================================
from rest_framework import generics, status, permissions

# =============================================================
# Local App
# =============================================================
from accounts.serializers.auth.auth import ForgotPasswordSerializer
from accounts.swagger.auth import register_schema
from accounts.services.auth import ForgotPasswordService
from accounts.models import User

# =============================================================
# Core Utilities
# =============================================================
from core.utils.responses import api_response
from core.logging.logger import get_logger
from core.utils.helpers import get_client_ip

# =============================================================
# Logger
# =============================================================
logger = get_logger(__name__)

# =============================================================
# Forgot Password View
# =============================================================
@register_schema
class ForgotPasswordView(generics.GenericAPIView):
    """
    Handles "forgot password" requests.
    
    Security Notes:
    - Does NOT reveal whether the email exists in the system.
    - Prevents email enumeration attacks.
    - Generates a secure token and sends reset link via email if user exists.
    """
    serializer_class = ForgotPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        # Validate input
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Extract validated email & client IP
        email = serializer.validated_data["email"]
        ip_address = get_client_ip(request)
        
        # Fetch user if exists (do not reveal to client)
        user = User.objects.filter(email=email).first()
        
        # Generate reset token & send email (if user exists)
        if user:
            try:
                ForgotPasswordService.send_reset_email(user, request_ip=ip_address)
            except Exception as e:
                # Log errors internally, do not expose to client
                logger.warning(f"Forgot password processing failed for {email}: {str(e)}")
        
        # API Response
        return api_response(
            message="If the email exists, a reset link has been sent.",
            status_code=status.HTTP_200_OK,
        )
