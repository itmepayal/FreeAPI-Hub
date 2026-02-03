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
# Core Utilities
# =============================================================
from core.utils.responses import api_response

# =============================================================
# Current User Views
# =============================================================
class CurrentUserView(APIView):
    """
    API endpoint to retrieve the profile of the currently authenticated user.

    Responsibilities:
    1. Ensure the request is authenticated (`IsAuthenticated`).
    2. Delegate fetching and serialization of user profile to `UserService`.
    3. Return structured API response with serialized user data.

    Design Notes:
    - Uses service layer for all business logic.
    - Returns data in a consistent response format.
    - Safe for frontend consumption to display user info.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Handle GET request to fetch current user's profile.

        Steps:
        1. Verify that the user is authenticated (handled by DRF permissions).
        2. Call `UserService.get_current_user_profile` to fetch serialized profile data.
        3. Return API response with status 200 and user profile.

        Args:
            request: DRF request object with authenticated user.

        Returns:
            Response: DRF Response with message and serialized user profile.

        Raises:
            ServiceException: If fetching or serialization fails (propagated via global exception handler).
        """
        # Fetch user profile using service layer
        data = UserService.get_current_user_profile(request.user)

        # Return profile data in structured API response
        return api_response(
            message="User profile fetched successfully.",
            data={"user": data},
            status_code=status.HTTP_200_OK,
        )


class UpdateAvatarView(GenericAPIView):
    """
    API endpoint to update the authenticated user's avatar image.

    Responsibilities:
    1. Ensure the request is authenticated (`IsAuthenticated`).
    2. Validate the incoming avatar file using `UpdateAvatarSerializer`.
    3. Delegate avatar upload and storage to `UserService.update_avatar`.
    4. Return structured API response with new avatar URL.

    Design Notes:
    - Handles file uploads safely (supports Cloudinary or other media backends).
    - Uses service layer for all business logic (upload, DB update, logging).
    - Returns data in consistent API response format for frontend display.
    """
    serializer_class = UpdateAvatarSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        """
        Handle PATCH request to update user's avatar.

        Steps:
        1. Validate incoming request data using `UpdateAvatarSerializer`.
        2. Extract the avatar file from validated data.
        3. Call `UserService.update_avatar` to upload the avatar and update the user record.
        4. Return structured API response with new avatar URL.

        Args:
            request: DRF request object with authenticated user and avatar file.

        Returns:
            Response: DRF Response with success message and new avatar URL.

        Raises:
            ValidationError: If serializer validation fails (handled by DRF automatically).
            ExternalServiceException: If avatar upload fails (propagated via service layer).
        """
        # 1. Validate incoming avatar file
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        avatar_file = serializer.validated_data["avatar"]

        # 2. Call service layer to update avatar and get new URL
        avatar_url = UserService.update_avatar(request.user, avatar_file)

        # 3. Return updated avatar URL in structured API response
        return api_response(
            message="Avatar updated successfully.",
            data={"avatar_url": avatar_url},
            status_code=status.HTTP_200_OK,
        )
