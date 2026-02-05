# =============================================================
# Django Signal Imports
# =============================================================
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps

# =============================================================
# User Post-Save Signal
# =============================================================
@receiver(post_save, sender=apps.get_model("accounts", "User"))
def create_user_relations(sender, instance, created, **kwargs):
    # -------------------------
    # Run only on user creation
    # -------------------------
    if not created:
        return

    # -------------------------
    # Lazy Model Resolution
    # -------------------------
    UserSecurity = apps.get_model("accounts", "UserSecurity")
    UserPresence = apps.get_model("accounts", "UserPresence")

    # -------------------------
    # Create Related Records
    # -------------------------
    UserSecurity.objects.get_or_create(user=instance)
    UserPresence.objects.get_or_create(user=instance)
