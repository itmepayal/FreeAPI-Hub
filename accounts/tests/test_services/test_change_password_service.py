# =============================================================
# Pytest: ChangePasswordService
# =============================================================

import pytest
from django.contrib.auth.hashers import check_password

# =============================================================
# Local Models & Services
# =============================================================
from accounts.models import User
from accounts.services.auth import ChangePasswordService

# =============================================================
# Core Exceptions
# =============================================================
from core.exceptions import (
    InactiveUserException,
    ValidationException,
    InternalServerException,
)

# =============================================================
# Test Case 1: Successful Password Change
# =============================================================
@pytest.mark.django_db
def test_change_password_success():
    # Step 1 — Create an active user
    user = User.objects.create(
        username="testuser_success",
        email="success@example.com",
        is_verified=False,
        is_active=True,
    )

    # Step 2 — Define old and new passwords
    old_password = "OldPassword@123"
    new_password = "NewStrongPassword@123"

    # Step 3 — Set the initial password
    user.set_password(old_password)
    user.save()

    # Step 4 — Execute the password change service
    ChangePasswordService.change_password(
        user=user,
        new_password=new_password,
    )

    # Step 5 — Reload user data from database
    user.refresh_from_db()

    # Step 6 — Assertions
    # New password should be valid
    assert check_password(new_password, user.password)

    # Old password should no longer be valid
    assert not check_password(old_password, user.password)


# =============================================================
# Test Case 2: Inactive User
# =============================================================
@pytest.mark.django_db
def test_change_password_inactive_user():
    # Step 1 — Create an inactive user
    user = User.objects.create(
        username="testuser_inactive",
        email="inactive@example.com",
        is_verified=False,
        is_active=False,
    )

    # Step 2 — Attempt to change password and expect exception
    with pytest.raises(InactiveUserException):
        ChangePasswordService.change_password(
            user=user,
            new_password="StrongPassword@123",
        )


# =============================================================
# Test Case 3: Weak Password Validation
# =============================================================
@pytest.mark.django_db
def test_change_password_weak_password():
    # Step 1 — Create an active user
    user = User.objects.create(
        username="testuser_weak_pwd",
        email="weak@example.com",
        is_verified=False,
        is_active=True,
    )

    # Step 2 — Attempt password change with weak password
    with pytest.raises(ValidationException):
        ChangePasswordService.change_password(
            user=user,
            new_password="123",  
        )


# =============================================================
# Test Case 4: Password Persistence
# =============================================================
@pytest.mark.django_db
def test_change_password_persisted_in_database():
    # Step 1 — Create an active user
    user = User.objects.create(
        username="testuser_persist",
        email="persist@example.com",
        is_verified=False,
        is_active=True,
    )

    new_password = "PersistedPassword@123"

    # Step 2 — Change password
    ChangePasswordService.change_password(
        user=user,
        new_password=new_password,
    )

    # Step 3 — Fetch fresh instance from DB
    refreshed_user = User.objects.get(id=user.id)

    # Step 4 — Verify password persistence
    assert check_password(new_password, refreshed_user.password)
