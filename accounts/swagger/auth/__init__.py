# =============================================================
# Import all auth-related swagger schemas
# =============================================================
from .login import login_schema
from .logout import logout_schema
from .register import register_schema
from .refresh_token import refresh_token_schema
from .verify_email import verify_email_schema

# =============================================================
# Explicitly define the public API for easier imports
# =============================================================
__all__ = [
    "login_schema",
    "logout_schema",
    "register_schema",
    "refresh_token_schema",
    "verify_email_schema",
]
