import pytest

from accounts.serializers.auth import (
    RegisterSerializer,
)

# =============================================================
# RegisterSerializer
# =============================================================

@pytest.mark.django_db 
class TestRegisterSerializer:
    
    def test_valid_registration(self, user_data):
        data = user_data.copy()
        s = RegisterSerializer(data=data)
        assert s.is_valid()

    def test_email_normalized(self, user_data):
        data = user_data.copy()
        data["email"] = "TEST@EXAMPLE.COM"
        
        s = RegisterSerializer(data=data)
        assert s.is_valid()
        
        user = s.save()
        assert user.email == "test@example.com"
    
    def test_weak_password_validation(self, user_data):
        data = user_data.copy()
        data["password"] = "123"
        
        s = RegisterSerializer(data=data)
        assert not s.is_valid()
        assert "password" in s.errors
    
    def test_missing_required_fields(self):
        s = RegisterSerializer(data={"email":"a@a.com"})
        assert not s.is_valid()
        assert "username" in s.errors
        assert "password" in s.errors
        
    def test_duplicate_email(self, user_instance, user_data):
        data = user_data.copy()
        data["email"] = user_instance.email
    
        s = RegisterSerializer(data=data)
        assert not s.is_valid()
        assert "email" in s.errors
    
    def test_create_user(self, user_data):
        data = user_data.copy()
        s = RegisterSerializer(data=data)
        assert s.is_valid()
        
        user = s.save()
        assert user.check_password(data["password"])
        assert not user.is_verified
        