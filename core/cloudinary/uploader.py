import cloudinary.uploader
import logging

logger = logging.getLogger(__name__)

def upload_to_cloudinary(
    file,
    folder="default",
    use_filename=True,
    unique_filename=True,
    overwrite=False
):
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
        raise RuntimeError("Cloudinary upload failed") from e
