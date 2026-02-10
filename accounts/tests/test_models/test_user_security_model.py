import pytest
from datetime import timedelta

import pyotp
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings

from accounts.models.user_security import hash_token
# ======================================================
# Fixtures
# ======================================================

User = get_user_model()

@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="sec@test.com",
        username="secuser",
        password="pass123"
    )

@pytest.fixture
def security(user):
    return user.security  

# ======================================================
# hash_token Tests
# ======================================================
def test_hash_token_is_deterministic():
    token = "abc123"
    assert hash_token(token) == hash_token(token)


def test_hash_token_changes_value():
    assert hash_token("a") != hash_token("b")

# ======================================================
# Forgot Password Token Tests
# ======================================================
@pytest.mark.django_db
def test_generate_forgot_password_sets_fields(security):
    raw = security.generate_forgot_password()
    
    assert raw is not None
    assert security.forgot_password_token == hash_token(raw)
    assert security.forgot_password_expiry > timezone.now()
    
@pytest.mark.django_db
def test_verify_forgot_password_success(security):
    raw = security.generate_forgot_password()
    assert security.verify_forgot_password_token(raw) is True

@pytest.mark.django_db
def test_verify_forgot_password_wrong_token(security):
    security.generate_forgot_password()
    assert security.verify_forgot_password_token("wrong") is False
    
@pytest.mark.django_db
def test_verify_forgot_password_expired(security):
    raw = security.generate_forgot_password()
    
    security.forgot_password_expiry = timezone.now() - timedelta(minutes=1)
    security.save()
    
    assert security.verify_forgot_password_token(raw) is False
    
@pytest.mark.django_db
def test_clear_forgot_password_token(security):
    security.generate_forgot_password()
    security.clear_forgot_password_token()
    
    assert security.forgot_password_token is None
    assert security.forgot_password_expiry is None

# ======================================================
# Email Verification Token Tests
# ======================================================
@pytest.mark.django_db
def test_generate_email_token_sets_fields(security):
    raw = security.generate_email_verification_token()
    
    assert security.email_verification_token == hash_token(raw)
    assert security.email_verification_expiry > timezone.now()
    
@pytest.mark.django_db
def test_verify_email_token_success(security):
    raw = security.generate_email_verification_token()
    assert security.verify_email_verification_token(raw) is True

@pytest.mark.django_db
def test_verify_email_token_expired(security):
    raw = security.generate_email_verification_token()

    security.email_verification_expiry = timezone.now() - timedelta(minutes=1)
    security.save()
    
    assert security.verify_email_verification_token(raw) is False
    
@pytest.mark.django_db
def test_clear_email_token(security):
    security.generate_email_verification_token()
    security.clear_email_verification_token()
    
    assert security.email_verification_token is None
    assert security.email_verification_expiry is None

# ======================================================
# TOTP Tests
# ======================================================
@pytest.mark.django_db
def test_generate_totp_secret(security):
    secret = security.generate_totp_secret()
    
    assert secret is not None
    assert security.totp_secret == secret
    
@pytest.mark.django_db
def test_verify_topt_success(security):
    secret = security.generate_totp_secret()
    
    totp = pyotp.TOTP(secret)
    code = totp.now()

    assert security.verify_totp(code) is True
    
@pytest.mark.django_db
def test_verify_totp_invalid(security):
    security.generate_totp_secret()
    assert security.verify_totp("000000") is False

@pytest.mark.django_db
def test_verify_totp_without_secret(security):
    assert security.verify_totp("123456") is False
    
# ======================================================
# TOTP URI Tests
# ======================================================
@pytest.mark.django_db
def test_get_totp_uri_returns_none_without_secret(security):
    assert security.get_totp_uri() is None
    
@pytest.mark.django_db
def test_get_totp_uri_contains_data(security, settings):
    settings.TOTP_ISSUER_NAME = "MyApp"
    
    security.generate_totp_secret()
    uri = security.get_totp_uri()

    assert "otpauth://totp/" in uri
    assert security.totp_secret in uri
    assert "issuer=" in uri
    

# ======================================================
# __str__ Test
# ======================================================

@pytest.mark.django_db
def test_str_representation(security, user):
    assert str(security) == f"Security<{user.email}>"