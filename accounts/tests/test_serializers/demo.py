# import pytest
# from uuid import uuid4

# from accounts.serializers.role import ChangeRoleSerializer
# from core.constants import ROLE_CHOICES


# # ======================================================
# # Helpers
# # ======================================================

# VALID_ROLE = ROLE_CHOICES[0][0]   # first valid role value


# # ======================================================
# # Valid Case
# # ======================================================

# def test_change_role_serializer_valid():
#     data = {
#         "user_id": str(uuid4()),
#         "role": VALID_ROLE,
#     }

#     s = ChangeRoleSerializer(data=data)

#     assert s.is_valid(), s.errors
#     assert s.validated_data["role"] == VALID_ROLE


# # ======================================================
# # user_id Validation
# # ======================================================

# def test_change_role_serializer_invalid_uuid():
#     s = ChangeRoleSerializer(data={
#         "user_id": "not-a-uuid",
#         "role": VALID_ROLE,
#     })

#     assert not s.is_valid()
#     assert "user_id" in s.errors


# def test_change_role_serializer_missing_user_id():
#     s = ChangeRoleSerializer(data={
#         "role": VALID_ROLE
#     })

#     assert not s.is_valid()
#     assert "user_id" in s.errors


# def test_change_role_serializer_null_user_id():
#     s = ChangeRoleSerializer(data={
#         "user_id": None,
#         "role": VALID_ROLE
#     })

#     assert not s.is_valid()
#     assert "user_id" in s.errors


# # ======================================================
# # role Validation
# # ======================================================

# def test_change_role_serializer_invalid_role():
#     s = ChangeRoleSerializer(data={
#         "user_id": str(uuid4()),
#         "role": "superadmin",  # not in choices
#     })

#     assert not s.is_valid()
#     assert "role" in s.errors


# def test_change_role_serializer_missing_role():
#     s = ChangeRoleSerializer(data={
#         "user_id": str(uuid4())
#     })

#     assert not s.is_valid()
#     assert "role" in s.errors


# def test_change_role_serializer_null_role():
#     s = ChangeRoleSerializer(data={
#         "user_id": str(uuid4()),
#         "role": None
#     })

#     assert not s.is_valid()
#     assert "role" in s.errors


# # ======================================================
# # Choice Boundary Test
# # ======================================================

# @pytest.mark.parametrize(
#     "role_value",
#     [choice[0] for choice in ROLE_CHOICES]
# )
# def test_change_role_serializer_all_valid_roles(role_value):
#     s = ChangeRoleSerializer(data={
#         "user_id": str(uuid4()),
#         "role": role_value,
#     })

#     assert s.is_valid(), f"Role failed: {role_value}"

