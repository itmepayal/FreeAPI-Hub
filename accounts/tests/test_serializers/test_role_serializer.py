import pytest
from uuid import uuid4
from accounts.serializers.auth import (
    ChangeRoleSerializer,
)
from core.constants import ROLE_CHOICES

# =============================================================
# Role Change
# =============================================================

@pytest.mark.django_db
class TestChangeRoleSerializer:
    
    def test_valid(self):
        uid = uuid4()
        role = ROLE_CHOICES[0][0] if ROLE_CHOICES else "user"
        
        s = ChangeRoleSerializer(
            data={
                "user_id":uid,
                "role":role
            }
        )
        assert s.is_valid()
        
        s = ChangeRoleSerializer(data={"user_id":uid, "role":role})
        assert s.is_valid()
        
    def test_bad_uuid(self):
        s = ChangeRoleSerializer(data={"user_id": "bad", "role": "user"})
        assert not s.is_valid()