from urllib.parse import quote

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from accounts.managers import UserManager

from core.models.base import BaseModel
from core.constants import ROLE_CHOICES, ROLE_USER

class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    # ----------------------
    # Basic User Info
    # ----------------------
    email = models.EmailField(unique=True, db_index=True)
    username = models.CharField(max_length=150)
    avatar = models.URLField(blank=True, null=True)

    # ----------------------
    # Role 
    # ----------------------
    role = models.CharField(
        max_length=50, 
        choices=ROLE_CHOICES, 
        default=ROLE_USER,
        db_index=True
    )

    # ----------------------
    # Account Status Flags
    # ----------------------
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # ----------------------
    # User Model Config
    # ----------------------
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    # ----------------------
    # Avatar URL
    # ----------------------
    @property
    def avatar_url(self):
        if self.avatar and self.avatar.startswith(("http://", "https://")):
            return self.avatar
        if self.username:
            name = self.username
        elif self.email:
            name = self.email.split("@")[0]
        else:
            name = "user"
        encoded = quote(name)

        return f"https://ui-avatars.com/api/?name={encoded}"

    # ----------------------
    # String Representation
    # ----------------------
    def __str__(self):
        return self.email or ""
    