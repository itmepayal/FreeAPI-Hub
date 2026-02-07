# =============================================================
# Django
# =============================================================
from django.contrib.auth.models import BaseUserManager

# =============================================================
# Local App / Constants
# =============================================================
from core.constants import ROLE_SUPERADMIN

# =============================================================
# Custom User Manager
# =============================================================

class UserManager(BaseUserManager):
    def _create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("Email must be provided")
        if not username:
            raise ValueError("Username must be provided")
        
        email = self.normalize_email(email.strip())
        user = self.model(email=email, username=username, **extra_fields)
        
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        
        user.save(using=self._db)
        return user

    def create_user(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, username, password, **extra_fields)

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("role", ROLE_SUPERADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified", True)
        
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, username, password, **extra_fields)

    def active(self):
        """
        Return queryset of active users only.

        Usage:
        >>> User.objects.active()
        """
        return self.filter(is_active=True)
