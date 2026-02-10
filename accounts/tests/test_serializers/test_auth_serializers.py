import pytest
from django.contrib.auth import get_user_model

from accounts.serializers.auth import (
    RegisterSerializer,
    LoginSerializer,
    VerifyEmailSerializer,
    RefreshTokenSerializer,
    ForgotPasswordSerializer,
    ResendEmailSerializer,
)

from accounts.models import UserSecurity

User = get_user_model()


# ======================================================
# RegisterSerializer Tests
# ======================================================
@pytest.mark.django_db
def test_register_serializer_valid():
    data = {
        "email":"TEST@Example.com",
        "username": "tester",
        "password": "StrongPassword@123"
    }
    s = RegisterSerializer(data=data)
    assert s.is_valid(), s.errors
    
    user = s.save()
    
    assert user.email == "test@example.com"
    assert user.username == "tester"
    assert user.check_password("StrongPassword@123")
    assert User.objects.filter(email="test@example.com").exists()
    
@pytest.mark.django_db
def test_register_serializer_email_normalized():
    s = RegisterSerializer(
        data={
            "email":"TEST@Example.com",
            "username": "u1",
            "password": "StrongPass13!"
        }
    )
    assert s.is_valid(), s.errors
    assert s.validated_data["email"] == "test@example.com"

@pytest.mark.django_db
def test_register_serializer_duplicate_email():
    User.objects.create_user(
        email="dup@test.com",
        username="u1",
        password="Pass123!!"
    )
    s = RegisterSerializer(data={
        "email": "dup@test.com",
        "username": "u2",
        "password": "Pass123!!"
    })
    assert not s.is_valid()
    assert "email" in s.errors
    assert "already" in str(s.errors["email"]).lower()

@pytest.mark.django_db
def test_register_serializer_weak_password():
    s = RegisterSerializer(data={
        "email": "weak@test.com",
        "username": "weak",
        "password": "123"
    })
    assert not s.is_valid()
    assert "password" in s.errors
    
@pytest.mark.django_db
def test_register_serializer_missing_fields():
    s = RegisterSerializer(data={})
    assert not s.is_valid()
    assert "email" in s.errors
    assert "username" in s.errors
    assert "password" in s.errors

# ======================================================
# LoginSerializer Tests
# ======================================================
def test_login_serializer_valid():
    s = LoginSerializer(data={
        "email": "a@test.com",
        "password": "pass123"
    })
    assert s.is_valid(), s.errors

def test_login_serializer_missing_password():
    s = LoginSerializer(data={
        "email": "a@test.com"
    })
    assert not s.is_valid()
    assert "password" in s.errors
    
def test_login_serializer_missing_email():
    s = LoginSerializer(
        data={
            "password":"pass123"
        }
    )
    assert not s.is_valid()
    assert "email" in s.errors
    
def test_login_serializer_invalid_email_format():
    s = LoginSerializer(data={
        "email": "not-an-email",
        "password": "pass123"
    })
    assert not s.is_valid()
    assert "email" in s.errors

# ======================================================
# VerifyEmailSerializer Tests
# ======================================================

def test_verify_email_serializer_valid():
    s = VerifyEmailSerializer(data={"token": "abc123"})
    assert s.is_valid(), s.errors
    
def test_verify_email_serializer_missing_token():
    s = VerifyEmailSerializer(data={})
    assert not s.is_valid()
    assert "token" in s.errors

# ======================================================
# RefreshTokenSerializer Tests
# ======================================================
def test_refresh_token_serializer_valid():
    s = RefreshTokenSerializer(
        data={
            "refresh_token":"xyz"
        }
    )
    assert s.is_valid(), s.errors
    
def test_refresh_token_serializer_missing():
    s = RefreshTokenSerializer(data={})
    assert not s.is_valid()
    assert "refresh_token" in s.errors
    
# ======================================================
# ForgotPasswordSerializer Tests
# ======================================================
def test_forgot_password_serializer_valid():
    s = ForgotPasswordSerializer(
        data={
            "email":"user@gmail.com"
        }
    )
    assert s.is_valid(), s.errors
    
def test_forgot_password_serializer_invalid_email():
    s = ForgotPasswordSerializer(
        data={
            "emial":"bad"
        }
    )
    assert not s.is_valid()
    assert "email" in s.errors


# ======================================================
# ResendEmailSerializer Tests
# ======================================================
@pytest.mark.django_db
def test_resend_email_serializer_valid():
    user = User.objects.create_user(
        email="resend@test.com",
        username="u1",
        password="Pass123!!",
        is_verified=False
    )
    security = user.security
    
    s = ResendEmailSerializer(
        data={
            "email":user.email
        }
    )
    assert s.is_valid(), s.errors
    
    assert s.validated_data["user"] == user
    assert s.validated_data["security"] == security
    
@pytest.mark.django_db
def test_resend_email_serializer_user_not_found():
    s = ResendEmailSerializer(data={"email": "no@test.com"})
    assert not s.is_valid()
    assert "email" in s.errors
    
@pytest.mark.django_db
def test_resend_email_serializer_already_verified():
    user= User.objects.create_user(
        email="verified@test.com",
        username="u1",
        password="Pass123!!",
        is_verified=True
    )
    s = ResendEmailSerializer(data={"email": user.email})
    assert not s.is_valid()
    assert "email" in s.errors
    assert "verified" in str(s.errors["email"]).lower()

@pytest.mark.django_db
def test_resend_email_serializer_security_missing():
    user = User.objects.create_user(
        email="nos@test.com",
        username="u1",
        password="Password123!!",
        is_verified=False
    )
    UserSecurity.objects.filter(user=user).delete()
    s = ResendEmailSerializer(data={"email": user.email})
    assert not s.is_valid()
    assert "email" in s.errors

# ======================================================
# Serializer Behavior Tests
# ======================================================
@pytest.mark.django_db
def test_register_serializer_password_is_hashed():
    s = RegisterSerializer(data={
        "email": "hash@test.com",
        "username": "u",
        "password": "StrongPass13!"
    })
    assert s.is_valid()
    user = s.save()
    
    assert user.password != "StrongPass13!"
    assert user.password != "StrongPass13!"
    assert user.password.startswith("pbkdf2")