import pytest
from django.contrib.auth import get_user_model

from accounts.services.auth.change_role_service import ChangeRoleService
from core.constants import ROLE_SUPERADMIN
from core.exceptions import (
    PermissionDeniedException,
    ResourceNotFoundException,
    InactiveUserException,
    OperationNotAllowedException,
)

User = get_user_model()

@pytest.mark.django_db
def test_change_role_success():
    actor = User.objects.create(
        email="admin@example.com",
        role="admin",
        is_active=True,
    )

    target = User.objects.create(
        email="user@example.com",
        role="user",
        is_active=True,
    )

    result = ChangeRoleService.execute(
        actor=actor,
        user_id=target.id,
        new_role="manager",
    )

    target.refresh_from_db()

    assert result["success"] is True
    assert target.role == "manager"

@pytest.mark.django_db
def test_change_role_self_modification_not_allowed():
    actor = User.objects.create(
        email="admin@example.com",
        role="admin",
        is_active=True,
    )
    
    with pytest.raises(PermissionDeniedException):
        ChangeRoleService.execute(
            actor=actor,
            user_id=actor.id,
            new_role="manager",
        )

@pytest.mark.django_db
def test_change_role_user_not_found():
    actor = User.objects.create(
        email="admin@example.com",
        role="admin",
        is_active=True,
    )

    with pytest.raises(ResourceNotFoundException):
        ChangeRoleService.execute(
            actor=actor,
            user_id=99999,
            new_role="manager",
        )
        
@pytest.mark.django_db
def test_change_role_inactive_user():
    actor = User.objects.create(
        email="admin@example.com",
        role="admin",
        is_active=True,
    )

    target = User.objects.create(
        email="inactive@example.com",
        role="user",
        is_active=False,
    )

    with pytest.raises(InactiveUserException):
        ChangeRoleService.execute(
            actor=actor,
            user_id=target.id,
            new_role="manager",
        )
        
@pytest.mark.django_db
def test_change_role_superadmin_not_allowed():
    actor = User.objects.create(
        email="admin@example.com",
        role="admin",
        is_active=True,
    )

    target = User.objects.create(
        email="superadmin@example.com",
        role=ROLE_SUPERADMIN,
        is_active=True,
    )

    with pytest.raises(OperationNotAllowedException):
        ChangeRoleService.execute(
            actor=actor,
            user_id=target.id,
            new_role="manager",
        )
