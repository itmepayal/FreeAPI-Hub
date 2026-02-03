# =============================================================
# Core Utilities
# =============================================================
from core.logging.logger import get_logger
from core.exceptions.base import ServiceException, InternalServerException

# =============================================================
# Base Service
# =============================================================
class BaseService:
    """
    Base class for all service-layer classes.

    NOTE:
    - ServiceException is always re-raised to preserve intent
    - Only truly unexpected errors are converted to InternalServerException
    """

    @classmethod
    def logger(cls):
        return get_logger(cls.__name__)
    