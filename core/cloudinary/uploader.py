# =============================================================
# Cloudinary Uploader Utility
# =============================================================
# Centralized helper for uploading files to Cloudinary.
# Handles default upload options, logging, and error abstraction.
# =============================================================

# =============================================================
# Standard Library
# =============================================================
import logging

# =============================================================
# Third-Party
# =============================================================
import cloudinary.uploader

# =============================================================
# Core Configuration
# =============================================================
from core.cloudinary.config import cloudinary

# =============================================================
# Logger Configuration
# =============================================================
logger = logging.getLogger(__name__)

# =============================================================
# Upload Helper
# =============================================================
def upload_to_cloudinary(
    file,
    folder="default",
    use_filename=True,
    unique_filename=True,
    overwrite=False,
):
    try:
        # Step 1 — Upload file to Cloudinary with provided options
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            use_filename=use_filename,
            unique_filename=unique_filename,
            overwrite=overwrite,
        )

        # Step 2 — Return secure HTTPS URL of uploaded file
        return result["secure_url"]

    except Exception as exc:
        # Step 3 — Log original exception for debugging
        logger.exception("Cloudinary upload failed")

        # Step 4 — Raise clean service-level error
        raise RuntimeError("Cloudinary upload failed") from exc
