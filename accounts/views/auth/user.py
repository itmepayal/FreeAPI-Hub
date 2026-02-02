# =============================================================
# Django REST Framework
# =============================================================
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

# =============================================================
# Local App Services
# =============================================================
from accounts.services.auth import UserService
from accounts.serializers.auth import UpdateAvatarSerializer

# =============================================================
# Core Utilities
# =============================================================
from core.utils.responses import api_response

# =============================================================
# Current User Views
# =============================================================

class CurrentUserView(APIView):
    """
    Retrieve the profile of the currently authenticated user.

    Key Points:
    - Requires authentication (`IsAuthenticated` permission).
    - Delegates user data fetching to `UserService.get_current_user_profile`.
    - Returns profile data in a consistent API response structure.
    - Safe for frontend consumption to display user info.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Handle GET request to fetch current user's profile.
        """
        # Fetch user profile using service layer
        data = UserService.get_current_user_profile(request.user)

        # Return profile data in consistent API response
        return api_response(
            message="User profile fetched successfully.",
            data=data,
            status_code=status.HTTP_200_OK,
        )


class UpdateAvatarView(GenericAPIView):
    """
    Update the authenticated user's avatar image.

    Key Points:
    - Requires authentication (`IsAuthenticated` permission).
    - Validates incoming avatar file via `UpdateAvatarSerializer`.
    - Delegates avatar storage and processing to `UserService.update_avatar`.
    - Returns updated avatar URL in response for frontend display.
    - Supports file uploads (e.g., Cloudinary or media storage backend).
    """
    serializer_class = UpdateAvatarSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Handle POST request to update user's avatar.
        """
        # Validate incoming avatar file
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        avatar_file = serializer.validated_data["avatar"]

        # Call service layer to update avatar and get new URL
        avatar_url = UserService.update_avatar(request.user, avatar_file)

        # Return updated avatar URL in consistent API response
        return api_response(
            message="Avatar updated successfully.",
            data={"avatar_url": avatar_url},
            status_code=status.HTTP_200_OK,
        )
