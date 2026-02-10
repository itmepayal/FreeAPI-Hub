import pytest
from accounts.serializers.auth import Enable2FASerializer

class DummyUser:
    def __init__(self, authenticated=True):
        self.is_authenticated = authenticated

class DummyRequest:
    def __init__(self, user):
        self.user = user

# =============================================================
# Valid token test
# =============================================================
@pytest.mark.parametrize("token", ["123456"])
def test_enable_2fa_valid(token):
    data = {"token": token}
    context = {"request": DummyRequest(DummyUser())}
    serializer = Enable2FASerializer(data=data, context=context)
    assert serializer.is_valid()
    assert serializer.validated_data['token'] == token

# =============================================================
# Invalid token tests
# =============================================================
@pytest.mark.parametrize("token", ["abc123", "12345", "1234567", "", "12 4567"])
def test_enable_2fa_invalid_tokens(token):
    data = {"token": token}
    context = {"request": DummyRequest(DummyUser())}
    serializer = Enable2FASerializer(data=data, context=context)
    assert not serializer.is_valid()
    assert "token" in serializer.errors

# =============================================================
# Unauthenticated user test
# =============================================================
def test_enable_2fa_unauthenticated():
    data = {"token": "123456"} 
    context = {"request": DummyRequest(DummyUser(authenticated=False))}
    serializer = Enable2FASerializer(data=data, context=context)
    assert not serializer.is_valid()
    assert serializer.errors 
