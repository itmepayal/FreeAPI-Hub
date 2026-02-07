from django.db import models
from django.utils import timezone
from datetime import timedelta
from core.models.base import BaseModel

class UserPresence(BaseModel):
    # ----------------------
    # User Info
    # ----------------------
    user = models.OneToOneField(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="presence"
    )
    
    # ----------------------
    # Realtime Presence 
    # ----------------------
    is_online = models.BooleanField(default=False, db_index=True)
    last_seen = models.DateTimeField(blank=True, null=True,  db_index=True)
    status_message = models.CharField(max_length=255, blank=True, default="Hey there! I am using config Hub.")
    
    # ----------------------
    # Online Presence Helpers
    # ----------------------
    def mark_online(self):
        self.is_online = True
        self.last_seen = timezone.now()
        self.save(update_fields=["is_online", "last_seen"])

    def mark_offline(self):
        self.is_online = False
        self.last_seen = timezone.now()
        self.save(update_fields=["is_online", "last_seen"])

    def heartbeat(self):
        self.last_seen = timezone.now()
        self.save(update_fields=["last_seen"])

    # ----------------------
    # Helpers
    # ----------------------
    @property
    def is_recently_active(self):
        if not self.last_seen:
            return False
        return timezone.now() - self.last_seen < timedelta(seconds=120)

    # ----------------------
    # String Representation
    # ----------------------
    def __str__(self):
        return f"Presence<{self.user.email}:{self.is_online}>"

    class Meta:
        indexes = [
            models.Index(fields=["is_online", "last_seen"]),
        ]
        