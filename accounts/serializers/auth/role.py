# =============================================================
# Django REST Framework
# =============================================================
from rest_framework import serializers

# =============================================================
# Role Constants
# =============================================================
from core.constants import ROLE_CHOICES

# =============================================================
# Change Role Serializer
# =============================================================
class ChangeRoleSerializer(serializers.Serializer):
    """
    Handles role update requests for a user.

    Use Case:
    - Admin role reassignment
    - Back-office user management
    - Permission escalation/demotion
    """

    # ---------------------------------------------------------
    # Target User Identifier
    # ---------------------------------------------------------
    user_id = serializers.UUIDField(
        required=True,
        help_text="User ID whose role will be changed",
    )

    # ---------------------------------------------------------
    # New Role Value
    # ---------------------------------------------------------
    role = serializers.ChoiceField(
        choices=ROLE_CHOICES,
        required=True,
        help_text="New role to assign",
    )
