import pytest
from uuid import uuid4
from accounts.serializers.auth import OAuthCallbackSerializer, EmptySerializer
from core.constants import ROLE_USER, ROLE_CHOICES

# =============================================================
# Valid Input Test
# =============================================================
def test_valid_input():
    data = {
        'code' : "123456"
    }
    oauth = OAuthCallbackSerializer(data=data)
    assert oauth.is_valid()
    assert oauth.validated_data['code'] == "123456"

# =============================================================
# Field Validation Tests
# =============================================================
def test_missing_field():
    oauth = OAuthCallbackSerializer(data={})
    assert not oauth.is_valid()
    assert "code" in oauth.errors
    

def test_null_code():
    data = {'code': None}
    oauth = OAuthCallbackSerializer(data=data)
    assert not oauth.is_valid()
    assert "code" in oauth.errors

def test_empty_string():
    data = {'code': ""}
    oauth = OAuthCallbackSerializer(data=data)
    assert not oauth.is_valid()
    assert "code" in oauth.errors

# =============================================================
# Valid Input Test
# =============================================================
def test_empty_serializer_valid_input():
    oauth = EmptySerializer(data={})
    assert oauth.is_valid()

def test_empty_serializer_none_input():
    oauth = EmptySerializer(data=None)
    assert not oauth.is_valid()
    assert oauth.errors

def test_empty_serializer_validated_data_empty():
    oauth = EmptySerializer(data={})
    assert oauth.is_valid()
    