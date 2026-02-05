import pyotp  
import hashlib
import secrets
import urllib.parse
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from core.models.base import BaseModel
from core.constants.auth import LOGIN_TYPE_CHOICES, LOGIN_EMAIL_PASSWORD

# ----------------------
# Token Hash Helper
# ----------------------
def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

class UserSecurity(BaseModel):
    # ----------------------
    # User Info
    # ----------------------
    user = models.OneToOneField(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="security"
    )
    
    # ----------------------
    # Login Type
    # ----------------------
    login_type = models.CharField(max_length=50, choices=LOGIN_TYPE_CHOICES, default=LOGIN_EMAIL_PASSWORD, db_index=True)

    # ----------------------
    # Authentication Tokens
    # ----------------------
    forgot_password_token = models.CharField(max_length=255, blank=True, null=True)
    forgot_password_expiry = models.DateTimeField(blank=True, null=True)
    email_verification_token = models.CharField(max_length=255, blank=True, null=True)
    email_verification_expiry = models.DateTimeField(blank=True, null=True)

    # ----------------------
    # Two-Factor Authentication (TOTP)
    # ----------------------
    is_2fa_enabled = models.BooleanField(default=False)
    totp_secret = models.CharField(max_length=32, blank=True, null=True)
    
    # ----------------------
    # TOKEN GENERATORS
    # ----------------------
    def generate_forgot_password(self) -> str :
        raw_token = secrets.token_urlsafe(32)
        
        self.forgot_password_token = hash_token(raw_token)
        self.forgot_password_expiry = timezone.now() + timedelta(hours=settings.PASSWORD_RESET_EXPIRY_HOURS)

        self.save(update_fields=[
            "forgot_password_token",
            "forgot_password_expiry"
        ])
        
        return raw_token
    
    def generate_email_verification_token(self) -> str:
        raw_token = secrets.token_urlsafe(32)
        
        self.email_verification_token = hash_token(raw_token)
        self.email_verification_expiry = timezone.now() + timedelta(hours=settings.EMAIL_VERIFICATION_EXPIRY_HOURS)

        self.save(update_fields=[
            "email_verification_token",
            "email_verification_expiry"
        ])
        
        return raw_token
    
    def verify_forgot_password_token(self, token: str) -> bool:
        if not self.forgot_password_token:
            return False

        if not self.forgot_password_expiry:
            return False
        
        if timezone.now() > self.forgot_password_expiry:
            return False
        
        return hash_token(token) == self.forgot_password_token
        
    def verify_email_verification_token(self, token: str) -> bool:
        if not self.email_verification_token:
            return False
        
        if not self.email_verification_expiry:
            return False

        if timezone.now() > self.email_verification_expiry:
            return False

        return hash_token(token) == self.email_verification_token
    
    # ----------------------
    # TOKEN CLEANUP
    # ----------------------
    def clear_forgot_password_token(self):
        self.forgot_password_token = None
        self.forgot_password_expiry = None
        self.save(update_fields=[
            "forgot_password_token",
            "forgot_password_expiry"
        ])
    
    def clear_email_verification_token(self):
        self.email_verification_token = None
        self.email_verification_expiry = None
        self.save(update_fields=[
            "email_verification_token",
            "email_verification_expiry"
        ])
    
    # ----------------------
    # TOTP (Two-Factor Authentication)
    # ----------------------
    def generate_totp_secret(self):
        self.totp_secret = pyotp.random_base32()
        self.save(update_fields=['totp_secret'])
        return self.totp_secret

    def get_totp_uri(self):
        issuer = urllib.parse.quote(settings.TOTP_ISSUER_NAME)
        email = urllib.parse.quote(self.user.email)
        return (
            f"otpauth://totp/{issuer}:{email}"
            f"?secret={self.totp_secret}&issuer={issuer}"
        )

    def verify_totp(self, token):
        if not self.totp_secret:
            return False
        totp = pyotp.TOTP(self.totp_secret)
        return totp.verify(token, valid_window=1)

    # ----------------------
    # String Representation
    # ----------------------
    def __str__(self):
        return f"Security<{self.user.email}>"

    class Meta:
        indexes = [
            models.Index(fields=["login_type", "is_2fa_enabled"]),
        ]