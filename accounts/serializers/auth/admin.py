# =============================================================
# Django REST Framework
# =============================================================
from rest_framework import serializers

# =============================================================
# Core Constants
# =============================================================
from core.constants import ROLE_CHOICES

# =============================================================
# Change Role Serializer
# =============================================================
class ChangeRoleSerializer(serializers.Serializer):
    # ---------------------------------------------------------
    # Target User Identifier
    # ---------------------------------------------------------
    user_id = serializers.UUIDField(
        required=True,
        help_text="Unique identifier of the user whose role will be updated",
    )

    # ---------------------------------------------------------
    # New Role Assignment
    # ---------------------------------------------------------
    role = serializers.ChoiceField(
        choices=ROLE_CHOICES,
        required=True,
        help_text="New role to assign to the user",
    )
