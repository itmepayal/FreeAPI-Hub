# =============================================================
# User Roles
# =============================================================
# Defines the role levels for access control.
# Used in models, permissions, and role-based checks.
# =============================================================

ROLE_USER = "USER"           # Regular user with standard permissions
ROLE_ADMIN = "ADMIN"         # Admin user with elevated permissions
ROLE_SUPERADMIN = "SUPERADMIN"  # SuperAdmin with full system access

# Tuple choices for Django model fields or DRF serializers
ROLE_CHOICES = [
    (ROLE_USER, "User"),
    (ROLE_ADMIN, "Admin"),
    (ROLE_SUPERADMIN, "SuperAdmin"),
]
