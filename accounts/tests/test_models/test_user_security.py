import pytest
from datetime import timedelta
from unittest.mock import patch, MagicMock

from django.conf import settings
from django.utils import timezone
from freezegun import freeze_time

from accounts.models import UserSecurity
from accounts.models.user_security import hash_token

from core.constants import LOGIN_EMAIL_PASSWORD, LOGIN_TYPE_CHOICES

from accounts.tests.factories.user_factory import UserFactory

@pytest.mark.django_db
class TestUserSecurityModel:
    """Unit tests for UserSecurity model"""
    
    @pytest.fixture
    def user_security(self):
        user = UserFactory()
        return user.security
    
    # ------------------------------------------------------------------
    # BASIC MODEL BEHAVIOR
    # ------------------------------------------------------------------
    def test_user_security_creation(self, user_security):
        assert user_security.user is not None
        assert user_security.login_type == LOGIN_EMAIL_PASSWORD
        assert user_security.is_2fa_enabled is False
        assert user_security.totp_secret is None
        
    def test_str_representation(self, user_security):
        assert str(user_security) == f"Security<{user_security.user.email}>"
        
    @pytest.mark.parametrize("login_type", [choice[0] for choice in LOGIN_TYPE_CHOICES])
    def test_login_type_choices(self, user_security, login_type):
        user_security.login_type = login_type
        user_security.save()
        user_security.refresh_from_db()
        assert user_security.login_type == login_type
        
    # ------------------------------------------------------------------
    # FORGOT PASSWORD TOKEN
    # ------------------------------------------------------------------
    @freeze_time("2024-01-01 12:00:00")
    def test_generate_forgot_password_token(self, user_security):
        raw_token = user_security.generate_forgot_password()
        user_security.refresh_from_db()
        
        assert raw_token
        assert user_security.forgot_password_token is not None
        assert user_security.forgot_password_expiry == timezone.now() + timedelta(hours=settings.PASSWORD_RESET_EXPIRY_HOURS)

    @freeze_time("2024-01-01 12:00:00")
    def test_verify_forgot_password_token_valid(self, user_security):
        raw_token = user_security.generate_forgot_password()
        assert user_security.verify_forgot_password_token(raw_token) is True
        
    @freeze_time("2024-01-01 12:00:00")
    def test_verify_forgot_password_token_invalid_or_missing(self, user_security):
        user_security.generate_forgot_password()
        
        assert user_security.verify_forgot_password_token("wrong-token") is False
        
        user_security.forgot_password_token = None
        user_security.save()
        assert user_security.verify_forgot_password_token("any-token") is False
        
    @freeze_time("2024-01-01 12:00:00")
    def test_verify_forgot_password_token_expired(self, user_security):
        raw_token = user_security.generate_forgot_password()
        
        with freeze_time("2024-01-02 13:00:00"):
            assert user_security.verify_forgot_password_token(raw_token) is False
            
    def test_clear_forgot_password_token(self, user_security):
        user_security.generate_forgot_password()
        user_security.clear_forgot_password_token()
        user_security.refresh_from_db()
        
        assert user_security.forgot_password_token is None
        assert user_security.forgot_password_expiry is None
    
    # ------------------------------------------------------------------
    # EMAIL VERIFICATION TOKEN
    # ------------------------------------------------------------------
    
    @freeze_time("2024-01-01 12:00:00")
    def test_generate_email_verification_token(self, user_security):
        raw_token = user_security.generate_email_verification_token()
        user_security.refresh_from_db()
        
        assert raw_token
        assert user_security.email_verification_expiry == timezone.now() + timedelta(hours=settings.EMAIL_VERIFICATION_EXPIRY_HOURS)
    
    @freeze_time("2024-01-01 12:00:00")
    def test_verify_email_verification_token_valid(self, user_security):
        raw_token = user_security.generate_email_verification_token()
        assert user_security.verify_email_verification_token(raw_token) is True
    
    def test_clear_email_verification_token(safe, user_security):
        user_security.generate_email_verification_token()
        user_security.clear_email_verification_token()
        user_security.refresh_from_db()
        
        assert user_security.email_verification_token is None
        assert user_security.email_verification_expiry is None
    
    # ------------------------------------------------------------------
    # TOTP / 2FA
    # ------------------------------------------------------------------
    def test_generate_totp_secret(self, user_security):
        secret = user_security.generate_totp_secret()
        user_security.refresh_from_db()

        assert secret == user_security.totp_secret
        assert len(secret) == 32
        
    @patch("accounts.models.user_security.pyotp.TOTP")
    def test_verify_totp_success(self, mock_totp_class, user_security):
        mock_totp = MagicMock()
        mock_totp.verify.return_value = True
        mock_totp_class.return_value = mock_totp
        
        user_security.totp_secret = "JBSWY3DPEHPK3PXP"
        user_security.save()
        
        assert user_security.verify_totp("123456") is True
        mock_totp.verify.assert_called_once_with("123456", valid_window=1)
        
    def test_verify_totp_without_secret(self, user_security):
        user_security.totp_secret = None
        user_security.save()
        
        assert user_security.verify_totp("123456") is False
        
    # ------------------------------------------------------------------
    # DATABASE & SECURITY UTILITIES
    # ------------------------------------------------------------------
    
    def test_database_indexes(self):
        indexes = [idx.fields for idx in UserSecurity._meta.indexes]
        assert ['login_type', 'is_2fa_enabled'] in indexes
    
    def test_hash_token_function(self):
        token = "test-token"
        hashed = hash_token(token)
        
        assert isinstance(hashed, str)
        assert len(hashed) == 64
        assert hash_token(token) == hashed
        assert hash_token("other-token") != hashed
        