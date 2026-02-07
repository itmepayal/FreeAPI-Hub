# tests/test_serializers.py
import pytest
from uuid import uuid4
from unittest.mock import patch, Mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError as DjangoValidationError

from accounts.models import User, UserSecurity, UserPresence
from accounts.serializers.auth import (
    Enable2FASerializer,
    Disable2FASerializer,
    Verify2FASerializer,
)

from core.constants import ROLE_CHOICES

# =============================================================
# 2FA
# =============================================================
@pytest.mark.django_db
class Test2FA:
    @pytest.mark.parametrize("token,ok", [
        ("123456", True),
        ("abc", False),
        ("123", False),
    ])
    
    @patch("accounts.models.UserSecurity.verify_totp")
    def test_enable_2fa_token(self, mock_verify, token, ok, user_instance):
        mock_verify.return_value = True
        
        request = Mock()
        request.user = user_instance
        
        s = Enable2FASerializer(
            data={"token": token},
            context={"request": request} 
        )
        
        assert s.is_valid() == ok