# =============================================================
# Cloudinary Uploader Utility
# =============================================================
# This module provides a wrapper function to upload files to Cloudinary.
# It centralizes the upload logic, applies default options, and handles errors.
# =============================================================

import cloudinary.uploader
import logging

# Ensure Cloudinary configuration is loaded before using the uploader
from core.cloudinary.config import cloudinary  

logger = logging.getLogger(__name__)

def upload_to_cloudinary(
    file,
    folder="default",
    use_filename=True,
    unique_filename=True,
    overwrite=False
):
    """
    Upload a file to Cloudinary and return its secure URL.

    Args:
        file: File object, path, or file-like object to upload.
        folder (str): Cloudinary folder to store the file in (default: "default").
        use_filename (bool): Use the original filename for the uploaded file.
        unique_filename (bool): Ensure filename uniqueness by appending a random string.
        overwrite (bool): Overwrite existing file with the same public_id if True.

    Returns:
        str: Secure HTTPS URL of the uploaded file.

    Raises:
        RuntimeError: If the upload fails for any reason. The original exception
                        is logged for debugging.
    """
    try:
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            use_filename=use_filename,
            unique_filename=unique_filename,
            overwrite=overwrite
        )
        return result["secure_url"]

    except Exception as e:
        logger.exception("Cloudinary upload failed")
        # Re-raise a clean RuntimeError for service-level handling
        raise RuntimeError("Cloudinary upload failed") from e
