import pytest

from accounts.serializers.auth import (
    LoginSerializer,
)

# =============================================================
# Login
# =============================================================

@pytest.mark.django_db
class TestLoginSerializer:
    
    def test_valid(self):
        s = LoginSerializer(data={"email":"a@a.com", "password":"x"})
        assert s.is_valid()
        
    def test_bad_email(self):
        s = LoginSerializer(data={"email":"bad", "password": "x"})
        assert not s.is_valid()
        assert "email" in s.errors
    