# =============================================================
# Django REST Framework Imports
# =============================================================
from rest_framework import serializers

# =============================================================
# Core Imports
# =============================================================
from core.constants.roles import ROLE_CHOICES

# =============================================================
# Role Management Serializer
# =============================================================
class ChangeRoleSerializer(serializers.Serializer):
    """
    Serializer used to change a user's role.
    Intended for admin or system-level role updates.
    """

    user_id = serializers.UUIDField(
        required=True,
        help_text="Unique identifier of the user whose role will be updated",
    )

    role = serializers.ChoiceField(
        choices=ROLE_CHOICES,
        required=True,
        help_text="New role to assign to the user",
    )
