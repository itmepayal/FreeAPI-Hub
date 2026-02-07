import pytest

from accounts.serializers.auth import (
    ResetPasswordSerializer,
)

# =============================================================
# Password Reset / Forgot
# =============================================================
class TestResetPasswordSerializer:
    def test_valid(self):
        s = ResetPasswordSerializer(
            data = {
                "token":"t",
                "new_password":"NewSecurePass123!",
                "confirm_password": "NewSecurePass123!",
            }
        )
        assert s.is_valid()
        assert "confirm_password" not in s.validated_data
    
    def test_mismatch(self):
        s = ResetPasswordSerializer(
            data = {
                "token":"t",
                "new_password": "ValidPass123!",
                "confirm_password": "DifferentPass123!"
            }
        )
        assert not s.is_valid()
        assert "confirm_password" in s.errors
