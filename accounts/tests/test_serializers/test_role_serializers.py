import pytest
from uuid import uuid4
from accounts.serializers.auth import ChangeRoleSerializer
from core.constants import ROLE_USER, ROLE_CHOICES

# =============================================================
# Valid Input Test
# =============================================================
def test_valid_input():
    """
    Test that the serializer is valid when provided
    correct user_id (UUID) and a valid role.
    """
    payload = {
        "user_id": str(uuid4()),  
        "role": ROLE_USER         
    }
    s = ChangeRoleSerializer(data=payload)
    assert s.is_valid()


# =============================================================
# user_id Field Validation Tests
# =============================================================
def test_invalid_uuid():
    """
    user_id is invalid (not a UUID string).
    Serializer should be invalid and contain 'user_id' error.
    """
    payload = {
        "user_id": "fake-uuid",
        "role": ROLE_USER
    }
    s = ChangeRoleSerializer(data=payload)
    assert not s.is_valid()
    assert 'user_id' in s.errors


def test_missing_user_id():
    """
    user_id is missing entirely.
    Serializer should be invalid and contain 'user_id' error.
    """
    payload = {
        "role": ROLE_USER
    }
    s = ChangeRoleSerializer(data=payload)
    assert not s.is_valid()
    assert 'user_id' in s.errors


def test_null_user_id():
    """
    user_id is explicitly null.
    Serializer should be invalid and contain 'user_id' error.
    """
    payload = {
        "user_id": None,
        "role": ROLE_USER
    }
    s = ChangeRoleSerializer(data=payload)
    assert not s.is_valid()
    assert 'user_id' in s.errors


# =============================================================
# role Field Validation Tests
# =============================================================
def test_invalid_role():
    """
    role value is not in ROLE_CHOICES.
    Serializer should be invalid and contain 'role' error.
    """
    payload = {
        "user_id": str(uuid4()),
        "role": "INVALID-ROLE"
    }
    s = ChangeRoleSerializer(data=payload)
    assert not s.is_valid()
    assert 'role' in s.errors


def test_missing_role():
    """
    role field is missing entirely.
    Serializer should be invalid and contain 'role' error.
    """
    payload = {
        "user_id": str(uuid4()),
    }
    s = ChangeRoleSerializer(data=payload)
    assert not s.is_valid()
    assert 'role' in s.errors


def test_null_role():
    """
    role field is explicitly null.
    Serializer should be invalid and contain 'role' error.
    """
    payload = {
        "user_id": str(uuid4()),
        "role": None
    }
    s = ChangeRoleSerializer(data=payload)
    assert not s.is_valid()
    assert 'role' in s.errors


# =============================================================
# Parametrized Test for All Valid Roles
# =============================================================
@pytest.mark.parametrize('role', [r[0] for r in ROLE_CHOICES])
def test_all_valid_roles(role):
    """
    Ensure that all roles in ROLE_CHOICES are accepted
    by the serializer as valid input.
    """
    payload = {
        "user_id": str(uuid4()),
        "role": role
    }
    s = ChangeRoleSerializer(data=payload)
    assert s.is_valid()
