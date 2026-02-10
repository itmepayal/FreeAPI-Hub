import pytest
from unittest.mock import Mock
from accounts.serializers.auth import (
    ResetPasswordSerializer, 
    ChangePasswordSerializer
)
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError

User = get_user_model()

class DummyRequest:
    def __init__(self, user):
        self.user = user
    
# ======================================================
# Reset Password Serializer Tests
# ======================================================

@pytest.mark.django_db
def test_reset_password_valid():
    data = {
        "token":"sometoken",
        "new_password": "StrongPass123!",
        "confirm_password": "StrongPass123!"
    }
    serializer = ResetPasswordSerializer(data=data)
    assert serializer.is_valid()
    
def test_reset_password_mismatch():
    data = {
        "token":"sometoken",
        "new_password": "StrongPass123!",
        "confirm_password": "MissMatchPass123!"
    }
    serializer = ResetPasswordSerializer(data=data)
    assert not serializer.is_valid()
    assert "confirm_password" in serializer.errors

def test_reset_password_weak_password():
    data = {
        "token": "sometoken",
        "new_password": "1234",
        "confirm_password": "1234"
    }
    serializer = ResetPasswordSerializer(data=data)
    assert not serializer.is_valid()
    assert "new_password" in serializer.errors

def test_reset_password_missing_token():
    data = {
        "new_password":"StrongPass123!",
        "confirm_password": "StrongPass123"
    }
    serializer = ResetPasswordSerializer(data=data)
    assert not serializer.is_valid()
    assert "token" in serializer.errors
    
# ======================================================
# Change Password Serializer Tests
# ======================================================
@pytest.mark.django_db
def test_change_password_valid():
    user = User.objects.create(username="testuser")
    user.set_password("OldPass123!") 
    user.save()

    context = {"request": DummyRequest(user)}

    data = {
        "old_password": "OldPass123!",
        "new_password": "NewPass123!",
        "confirm_password": "NewPass123!"
    }

    serializer = ChangePasswordSerializer(data=data, context=context)
    assert serializer.is_valid(), serializer.errors  

@pytest.mark.django_db
def test_change_password_wrong_old():
    user = User.objects.create(username="testuser")
    user.set_password("OldPass123!") 
    user.save()

    context = {"request": DummyRequest(user)}

    data = {
        "old_password": "WrongPassword!",
        "new_password": "NewPass123!",
        "confirm_password": "NewPass123!"
    }
    serializer = ChangePasswordSerializer(data=data, context=context)
    assert not serializer.is_valid()
    assert "old_password" in serializer.errors

@pytest.mark.django_db
def test_change_password_reuse_old():
    user = User.objects.create(username="testuser")
    user.set_password("OldPass123!") 
    user.save()
    context = {"request": DummyRequest(user)}
    data = {
        "old_password": "OldPass123!",
        "new_password": "OldPass123!",
        "confirm_password": "OldPass123!"
    }
    serializer = ChangePasswordSerializer(data=data, context=context)
    assert not serializer.is_valid()
    assert "new_password" in serializer.errors

@pytest.mark.django_db
def test_change_password_unauthenticated():
    class UnauthenticatedUser:
        is_authenticated = False

    user = UnauthenticatedUser()
    context = {"request": DummyRequest(user)}

    data = {
        "old_password": "OldPass123!",
        "new_password": "NewPass123!",
        "confirm_password": "NewPass123!"
    }

    serializer = ChangePasswordSerializer(data=data, context=context)

    assert not serializer.is_valid()
    
    assert "non_field_errors" in serializer.errors or "old_password" in serializer.errors or "new_password" in serializer.errors