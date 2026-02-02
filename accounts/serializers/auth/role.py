from rest_framework import serializers
from core.constants.roles import ROLE_CHOICES

class ChangeRoleSerializer(serializers.Serializer):
    """
    Serializer for changing a user's role.
    """
    user_id = serializers.UUIDField(required=True, help_text="User ID to change role")
    role = serializers.ChoiceField(choices=ROLE_CHOICES, required=True, help_text="New role")
    
    