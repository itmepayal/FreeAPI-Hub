# =============================================================
# Django Admin Imports
# =============================================================
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

# =============================================================
# Local App Imports
# =============================================================
from accounts.models import User
from accounts.models.user_security import UserSecurity
from accounts.models.user_presence import UserPresence


# =============================================================
# Inline Admin: User Security
# =============================================================
class UserSecurityInline(admin.StackedInline):
    """
    Displays security-related user data in User admin page.
    Sensitive fields are read-only for safety.
    """

    model = UserSecurity
    can_delete = False
    extra = 0

    # -------------------------
    # Read-only Fields
    # -------------------------
    readonly_fields = (
        "masked_refresh_token",
        "forgot_password_token",
        "forgot_password_expiry",
        "email_verification_token",
        "email_verification_expiry",
        "totp_secret",
    )

    # -------------------------
    # Custom Display Methods
    # -------------------------
    def masked_refresh_token(self, obj):
        """
        Safely display a partial refresh token hash
        (first 6 characters only).
        """
        if obj.refresh_token_hash:
            return f"{obj.refresh_token_hash[:6]}..."
        return "-"

    masked_refresh_token.short_description = "Refresh Token"


# =============================================================
# Inline Admin: User Presence
# =============================================================
class UserPresenceInline(admin.StackedInline):
    """
    Displays user presence information such as last seen time.
    """

    model = UserPresence
    can_delete = False
    extra = 0
    readonly_fields = ("last_seen",)


# =============================================================
# User Admin Configuration
# =============================================================
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin configuration for User model.
    Extends Django's BaseUserAdmin.
    """

    model = User

    # -------------------------
    # Custom List Display Fields
    # -------------------------
    def is_online(self, obj):
        """Return user's online status from presence model."""
        return getattr(obj.presence, "is_online", False)

    is_online.boolean = True
    is_online.short_description = "Online"

    def two_factor(self, obj):
        """Return whether 2FA is enabled for the user."""
        return getattr(obj.security, "is_2fa_enabled", False)

    two_factor.boolean = True
    two_factor.short_description = "2FA"

    # -------------------------
    # Admin List Page Config
    # -------------------------
    list_display = (
        "email",
        "username",
        "role",
        "is_verified",
        "is_online",
        "two_factor",
        "is_staff",
        "is_active",
    )

    list_filter = (
        "role",
        "is_verified",
        "is_staff",
        "is_active",
    )

    search_fields = ("email", "username")
    ordering = ("email",)

    # -------------------------
    # Admin Detail Page Config
    # -------------------------
    fieldsets = (
        (None, {
            "fields": ("email", "username", "password", "avatar")
        }),
        (_("Permissions"), {
            "fields": (
                "role",
                "is_verified",
                "is_staff",
                "is_superuser",
                "is_active",
                "groups",
                "user_permissions",
            )
        }),
        (_("Important dates"), {
            "fields": ("last_login",)
        }),
    )

    # -------------------------
    # Admin Create User Page
    # -------------------------
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email",
                "username",
                "password1",
                "password2",
                "role",
                "is_staff",
                "is_verified",
            ),
        }),
    )

    # -------------------------
    # Inline Models
    # -------------------------
    inlines = (
        UserSecurityInline,
        UserPresenceInline,
    )

    # -------------------------
    # Read-only Fields
    # -------------------------
    readonly_fields = ("last_login",)

    # -------------------------
    # Django Auth Settings
    # -------------------------
    filter_horizontal = ("groups", "user_permissions")
