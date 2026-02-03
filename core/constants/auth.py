# =============================================================
# Authentication Login Types
# =============================================================
# Defines the different methods a user can log in with.
# These are used in user models, serializers, and service logic.
# =============================================================

LOGIN_EMAIL_PASSWORD = "EMAIL_PASSWORD"  # Standard email & password login
LOGIN_GOOGLE = "GOOGLE"                  # Login via Google OAuth
LOGIN_GITHUB = "GITHUB"                  # Login via GitHub OAuth

# Tuple choices for Django model fields or DRF serializers
LOGIN_TYPE_CHOICES = [
    (LOGIN_EMAIL_PASSWORD, "Email & Password"),
    (LOGIN_GOOGLE, "Google"),
    (LOGIN_GITHUB, "GitHub"),
]
