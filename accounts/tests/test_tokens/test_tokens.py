import pytest
from datetime import timedelta

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from accounts.helpers.token import generate_tokens, generate_2fa_token, TwoFAToken

User = get_user_model()

# ======================================================
# Fixtures
# ======================================================

@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="jwt@test.com",
        username="jwtuser",
        password="pass123"
    )

# ======================================================
# generate_tokens Tests
# ======================================================

@pytest.mark.django_db
def test_generate_tokens_returns_access_and_refresh(user):
    tokens = generate_tokens(user)
    
    assert "access" in tokens
    assert "refresh" in tokens
    
    assert isinstance(tokens["access"], str)
    assert isinstance(tokens["refresh"], str)

@pytest.mark.django_db
def test_access_token_is_valid(user):
    tokens = generate_tokens(user)

    access = AccessToken(tokens["access"])

    assert access["user_id"] == str(user.id)

@pytest.mark.django_db
def test_refresh_token_is_valid(user):
    tokens = generate_tokens(user)

    refresh = RefreshToken(tokens["refresh"])

    assert refresh["user_id"] == str(user.id)

# ======================================================
# TwoFAToken Tests
# ======================================================

@pytest.mark.django_db
def test_twofa_token_type_and_user_claim(user):
    token = TwoFAToken.for_user(user)
    
    assert token["user_id"] == str(user.id)
    assert token["token_type"] == "2fa"

def test_twofa_token_lifetime():
    assert TwoFAToken.lifetime == timedelta(minutes=5)

# ======================================================
# generate_2fa_token Tests
# ======================================================
@pytest.mark.django_db
def test_generate_2fa_token_returns_string(user):
    token_str = generate_2fa_token(user)

    assert isinstance(token_str, str)

@pytest.mark.django_db
def test_generate_2fa_token_decodes_correctly(user):
    token_str = generate_2fa_token(user)

    token = TwoFAToken(token_str)

    assert token["user_id"] == str(user.id)
    assert token["token_type"] == "2fa"
    