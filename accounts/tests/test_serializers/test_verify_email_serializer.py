import pytest

from accounts.serializers.auth import (
    VerifyEmailSerializer,
)

# =============================================================
# Verify Email
# =============================================================

@pytest.mark.django_db
class TestVerifyEmailSerializer:
    
    def test_valid_token(self):
        s = VerifyEmailSerializer(data={"token": "abc"})
        assert s.is_valid()

    def test_missing_token(self):
        s = VerifyEmailSerializer(data={})
        assert not s.is_valid()
        assert "token" in s.errors
    