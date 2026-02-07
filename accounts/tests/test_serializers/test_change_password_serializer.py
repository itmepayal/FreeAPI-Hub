import pytest
from unittest.mock import patch, Mock
from accounts.serializers.auth import (
    ChangePasswordSerializer,
)

# =============================================================
# Change Password
# =============================================================

@pytest.mark.django_db
class TestChangePasswordSerializer:
    def test_valid(self, user_instance):
        req = Mock(user=user_instance)
        
        s = ChangePasswordSerializer(
            data={
                "old_password": "password123",
                "new_password": "NewSecurePass123!",
                "confirm_password": "NewSecurePass123!",
            },
            context={"request": req}
        )
        
        assert s.is_valid()
        
    def test_unauthenticated(self):
        s = ChangePasswordSerializer(data={})
        assert not s.is_valid()
        