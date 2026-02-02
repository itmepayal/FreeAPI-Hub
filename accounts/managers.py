# =============================================================
# Python Standard Library
# =============================================================
import time

# =============================================================
# Django
# =============================================================
from django.contrib.auth.models import BaseUserManager

# =============================================================
# Local App / Constants
# =============================================================
from core.constants.roles import ROLE_SUPERADMIN

# =============================================================
# Custom User Manager
# =============================================================
# Handles user creation logic for the custom User model.
# Provides helper methods to create normal users, superusers,
# and filter active users.
# =============================================================

class UserManager(BaseUserManager):
    """
    Custom manager for User model.
    
    Responsibilities:
    - Create standard users (`create_user`)
    - Create superusers (`create_superuser`)
    - Provide helper methods for filtering (e.g., active users)
    - Ensure required fields (email, username) are provided
    - Normalize email and handle password hashing
    """

    def _create_user(self, email, username, password=None, **extra_fields):
        """
        Core user creation method (internal).

        Steps:
        1. Validate that email and username are provided.
        2. Normalize email (lowercase domain part).
        3. Instantiate user model with provided fields.
        4. Hash password if provided.
        5. Save user to the database using the appropriate DB alias.
        """
        if not email:
            raise ValueError("Email must be provided")
        if not username:
            raise ValueError("Username must be provided")
        
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        
        if password:
            user.set_password(password)
        
        user.save(using=self._db)
        return user

    def create_user(self, email, username, password=None, **extra_fields):
        """
        Create a standard user.

        Default flags:
        - is_staff = False
        - is_superuser = False

        Usage:
        >>> User.objects.create_user(email="test@example.com", username="testuser", password="pass123")
        """
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, username, password, **extra_fields)

    def create_superuser(self, email, username, password=None, **extra_fields):
        """
        Create a superuser with full admin privileges.

        Default flags:
        - role = ROLE_SUPERADMIN
        - is_staff = True
        - is_superuser = True
        - is_verified = True (email verified by default)

        Usage:
        >>> User.objects.create_superuser(email="admin@example.com", username="admin", password="adminpass")
        """
        extra_fields.setdefault("role", ROLE_SUPERADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified", True)
        return self._create_user(email, username, password, **extra_fields)

    def active(self):
        """
        Return queryset of active users only.

        Usage:
        >>> User.objects.active()
        """
        return self.filter(is_active=True)
