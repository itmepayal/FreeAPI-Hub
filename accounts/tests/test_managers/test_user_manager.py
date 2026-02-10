import pytest
from django.contrib.auth import get_user_model

from core.constants import ROLE_SUPERADMIN

User = get_user_model()

# ======================================================
# Constants
# ======================================================

EMAIL = "manager@test.com"
USERNAME = "manageruser"
PASSWORD = "StrongPass123"

# ======================================================
# create_user Tests
# ======================================================
@pytest.mark.django_db
def test_create_user_missing_email():
    with pytest.raises(ValueError):
        User.objects.create_user(
            email="",
            username=USERNAME,
            password=PASSWORD
        )
        
@pytest.mark.django_db
def test_create_user_missing_username():
    with pytest.raises(ValueError):
        User.objects.create_user(
            email=EMAIL,
            username="",
            password=PASSWORD
        )

@pytest.mark.django_db
def test_create_user_password_set():
    user = User.objects.create_user(
        email=EMAIL,
        username=USERNAME,
        password=PASSWORD
    )
    assert user.check_password(PASSWORD)

@pytest.mark.django_db
def test_create_user_unusable_password_when_none():
    user = User.objects.create_user(
        email="nopass@test.com",
        username="nopass",
        password=None
    )
    assert user.has_usable_password() is False

@pytest.mark.django_db
def test_create_user_email_normalized():
    user = User.objects.create_user(
        email="TEST@Example.COM",
        username="norm",
        password="pass"
    )
    assert user.email == "TEST@example.com"

# ======================================================
# create_user Tests
# ======================================================

@pytest.mark.django_db
def test_create_user_defaults():
    user = User.objects.create_user(
        email="normal@test.com",
        username="normal",
        password="pass"
    )
    
    assert user.is_staff is False
    assert user.is_superuser is False

@pytest.mark.django_db
def test_create_user_respects_extra_fields():
    user = User.objects.create_user(
        email="staff@test.com",
        username="staff",
        password="pass",
        is_staff=True
    )

    assert user.is_staff is True

# ======================================================
# create_superuser Tests
# ======================================================

@pytest.mark.django_db
def test_create_superuser_success():
    admin = User.objects.create_superuser(
        email="admin@test.com",
        username="admin",
        password="adminpass"
    )
    
    assert admin.is_staff is True
    assert admin.is_superuser is True
    assert admin.is_verified is True
    assert admin.role == ROLE_SUPERADMIN
    
@pytest.mark.django_db
def test_create_superuser_staff_false_error():
    with pytest.raises(ValueError):
        User.objects.create_superuser(
            email="bad@test.com",
            username="bad",
            password="pass",
            is_staff=False
        )
        
@pytest.mark.django_db
def test_create_superuser_false_error():
    with pytest.raises(ValueError):
        User.objects.create_superuser(
            email="bad2@test.com",
            username="bad2",
            password="pass",
            is_superuser=False
        )
    

# ======================================================
# active() Queryset Test
# ======================================================
@pytest.mark.django_db

def test_active_manager_method():
    active = User.objects.create_user(
        email="active@test.com",
        username="active",
        password="pass",
        is_active=True
    )
    
    inactive = User.objects.create_user(
        email="inactive@test.com",
        username="inactive",
        password="pass",
        is_active=False
    )

    qs = User.objects.active()
    
    assert active in qs
    assert inactive not in qs