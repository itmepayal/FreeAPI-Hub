# tests/test_serializers.py
import pytest

from accounts.serializers.auth import (
    OAuthCallbackSerializer,
)

# =============================================================
# OAuth
# =============================================================
@pytest.mark.django_db
class TestOAuth:
    
    def test_valid(self):
        s = OAuthCallbackSerializer(data={
            "code":"abc"
        })
        assert s.is_valid()
    
    def test_missing(self):
        s = OAuthCallbackSerializer(data={})
        assert not s.is_valid()