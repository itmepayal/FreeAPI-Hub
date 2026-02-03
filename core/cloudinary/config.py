import cloudinary.uploader
from django.conf import settings

# =============================================================
# Cloudinary Configuration
# =============================================================
# Configure Cloudinary SDK with credentials from Django settings.
# This allows uploading and managing media assets (images/videos)
# securely using the Cloudinary API throughout the project.
#
# Notes:
# - `cloud_name`, `api_key`, and `api_secret` are required credentials.
# - `secure=True` enforces HTTPS URLs for uploaded assets.
# - Credentials should be stored in environment variables and
#   accessed via Django settings for security.
# =============================================================
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)
