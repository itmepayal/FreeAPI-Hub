# ==========================================================
# conftest.py — Pytest Global Fixtures
# ==========================================================
import pytest
from unittest.mock import MagicMock, patch
from datetime import timedelta
from django.utils import timezone

# ==========================================================
# Local Models
# ==========================================================
from accounts.models import User, UserSecurity

# ==========================================================
# Fixture: Fake Request Object
# ==========================================================
@pytest.fixture
def fake_request():
    req = MagicMock()
    req.META = {
        "REMOTE_ADDR": "127.0.0.1",
        "HTTP_USER_AGENT": "pytest-agent"
    }
    return req

# ==========================================================
# Fixture: Validate Data
# ==========================================================
@pytest.fixture
def validated_data():
    return{
        "username":"tester",
        "email": "test@example.com",
        "password":"StrongPass@123"
    }

# ==========================================================
# Fixture: User Factory
# ==========================================================
@pytest.fixture
def user_factory(db):
    def create_user(**overrides):
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "StrongPass123!",
            "is_verified": True,
            "is_active": True,
        }
        data.update(overrides)
        user = User.objects.create_user(**data)
        UserSecurity.objects.get_or_create(user=user)
        return user
    return create_user

# ==========================================================
# Fixture: Security Flag Helper
# ==========================================================
@pytest.fixture
def set_security_flags():
    def _set(user, **flags):
        security = UserSecurity.objects.get(user=user)
        for key, value in flags.items():
            setattr(security, key, value)
        security.save()
        user.refresh_from_db()
        return security
    return _set

# ==========================================================
# Fixture: Time Helpers
# ==========================================================
@pytest.fixture
def future_time():
    return timezone.now() + timedelta(hours=1)

@pytest.fixture
def past_time():
    return timezone.now() - timedelta(hours=1)

# ==========================================================
# Fixture: 2FA Test Users
# ==========================================================
@pytest.fixture
def twofa_user(user_factory):
    return user_factory(
        username="twofa_user",
        email="twofa@test.com",
        password="Pass123!",
        is_verified=True,
    )

@pytest.fixture
def security_2fa_enabled(twofa_user):
    security = twofa_user.security
    security.is_2fa_enabled = True
    security.totp_secret = "SECRET"
    security.save()
    return security

@pytest.fixture
def security_2fa_disabled(twofa_user):
    security = twofa_user.security
    security.is_2fa_enabled = False
    security.totp_secret = None
    security.save()
    return security

# ==========================================================
# Mock Fixtures — Auth / Registration / Email / Tokens
# ==========================================================
@pytest.fixture
def mock_authenticate():
    with patch("accounts.services.auth.login_service.authenticate") as m:
        yield m

@pytest.fixture
def mock_tokens():
    with patch(
        "accounts.services.auth.login_service.generate_tokens",
        return_value={"access": "access123", "refresh": "refresh123"},
    ) as m:
        yield m

@pytest.fixture
def mock_2fa_token():
    with patch(
        "accounts.services.auth.login_service.generate_2fa_token",
        return_value="temp2fa123",
    ) as m:
        yield m

@pytest.fixture
def mock_get_ip():
    with patch(
        "accounts.services.auth.register_service.get_client_ip",
        return_value="1.2.3.4"
    ) as m:
        yield m

@pytest.fixture
def mock_send_email():
    with patch(
        "accounts.services.auth.register_service.send_email"
    ) as m:
        yield m

@pytest.fixture
def mock_on_commit():
    with patch(
        "accounts.services.auth.register_service.transaction.on_commit"
    ) as m:
        yield m

@pytest.fixture
def mock_create_user():
    with patch(
        "accounts.services.auth.register_service.User.objects.create_user"
    ) as m:
        yield m

@pytest.fixture
def mock_security_get():
    with patch(
        "accounts.services.auth.register_service.UserSecurity.objects.get_or_create"
    ) as m:
        yield m

@pytest.fixture
def mock_presence():
    with patch(
        "accounts.services.auth.register_service.UserPresence.objects.get_or_create"
    ) as m:
        yield m

@pytest.fixture
def mock_hash_token():
    with patch(
        "accounts.services.auth.verify_email_service.hash_token"
    ) as m:
        yield m

@pytest.fixture
def mock_totp_valid():
    return MagicMock(return_value=True)

@pytest.fixture
def mock_totp_invalid():
    return MagicMock(return_value=False)

@pytest.fixture
def mock_totp_setup_methods():
    with patch.object(
        UserSecurity,
        "generate_totp_secret",
        return_value="SECRET123"
    ) as m_secret, patch.object(
        UserSecurity,
        "get_totp_uri",
        return_value="otpauth://uri"
    ) as m_uri:
        yield m_secret, m_uri

@pytest.fixture
def mock_refresh_token():
    mock_refresh = MagicMock()
    mock_refresh.access_token = "access123"
    mock_refresh.__str__ = lambda self: "refresh123"

    with patch(
        "accounts.services.auth.two_factor_service.RefreshToken.for_user",
        return_value=mock_refresh
    ) as m:
        yield m
