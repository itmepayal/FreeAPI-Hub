# =============================================================
# Third-Party Imports
# =============================================================
import cloudinary
import cloudinary.uploader

# =============================================================
# Django Settings
# =============================================================
from django.conf import settings


# =============================================================
# Cloudinary Configuration
# =============================================================
"""
Centralized Cloudinary setup for media uploads.

Credentials are loaded securely from Django settings.
This configuration is applied globally on import.
"""

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,  
)
