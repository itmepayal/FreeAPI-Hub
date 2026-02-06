# =============================================================
# Django REST Framework
# =============================================================
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

# =============================================================
# Local App Services & Serializers
# =============================================================
from accounts.services.auth import UserService
from accounts.serializers.auth import UpdateAvatarSerializer, UserSerializer

# =============================================================
# Core Response Utility
# =============================================================
from core.utils.responses import api_response


# =============================================================
# Current User View
# =============================================================
class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Step 1 — Fetch profile via service layer
        data = UserService.get_current_user_profile(request.user)

        # Step 2 — Return structured response
        return api_response(
            message="User profile fetched successfully.",
            data={"user": data},
            status_code=status.HTTP_200_OK,
        )


# =============================================================
# Update Avatar View
# =============================================================
class UpdateAvatarView(GenericAPIView):
    serializer_class = UpdateAvatarSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        # Step 1 — Validate incoming data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Step 2 — Extract avatar file
        avatar_file = serializer.validated_data["avatar"]

        # Step 3 — Update avatar via service layer
        avatar_url = UserService.update_avatar(
            request.user,
            avatar_file,
        )

        # Step 4 — Return standardized response
        return api_response(
            message="Avatar updated successfully.",
            data={"avatar_url": avatar_url},
            status_code=status.HTTP_200_OK,
        )
