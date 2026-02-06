# =============================================================
# STANDARD LIBRARY
# =============================================================
from pathlib import Path
from datetime import timedelta
from decouple import Config, RepositoryEnv 
import dj_database_url
import os
# Purpose: Handles file paths, time durations, environment config loading,
# database URL parsing, and OS-level operations. Standard for production-ready Django.

# =============================================================
# ENV FILE CONFIGURATION
# =============================================================
env_file = os.environ.get("ENV_FILE")

if env_file and Path(env_file).exists():
    config = Config(repository=RepositoryEnv(env_file))
elif Path(".env.local").exists():
    config = Config(repository=RepositoryEnv(".env.local"))
elif Path(".env").exists():
    config = Config(repository=RepositoryEnv(".env"))
else:
    config = Config(repository=os.environ)

ENV = config("ENV", default="local")
# Purpose: Dynamically load environment variables from .env files or system environment.
# Allows flexible config for local, staging, or production.

# =============================================================
# BASE DIRECTORY
# =============================================================
BASE_DIR = Path(__file__).resolve().parent.parent
# Purpose: Root directory reference for static/media files, templates, DB files.

# =============================================================
# SECURITY & DEBUG
# =============================================================
if ENV == "local":
    SECRET_KEY = config(
        "SECRET_KEY",
        default="%msg!8p+m5(%l$ljg6n7)b7opv&-1w%a@ao)_vb-s%tvcl6lu=",
        cast=str
    )
else:
    SECRET_KEY = config("SECRET_KEY")

DEBUG = ENV == "local"

ALLOWED_HOSTS = (
    config("ALLOWED_HOSTS", default="localhost,127.0.0.1").split(",")
    if DEBUG else
    config("ALLOWED_HOSTS", default="freeapi-hub.up.railway.app").split(",")
)
# Purpose: Security keys and host restrictions.
# DEBUG enabled only locally; production hosts are restricted.

# =============================================================
# INSTALLED APPS
# =============================================================
INSTALLED_APPS = [
    # ASGI server
    "daphne",

    # Django core apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party apps
    "corsheaders",                     # Handles CORS headers for frontend
    "rest_framework",                  # DRF for API building
    "drf_spectacular",                 # OpenAPI/Swagger docs
    "rest_framework_simplejwt.token_blacklist", 
    "channels",                        # WebSocket / ASGI support

    # Local apps
    "accounts",
]
# Purpose: Registers apps for Django to recognize.

# =============================================================
# CORS SETTINGS
# =============================================================
CORS_ALLOW_CREDENTIALS = True

if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]
# Purpose: Allows frontend clients to interact with backend APIs.
# Strict in production; relaxed in development.

# =============================================================
# AUTHENTICATION
# =============================================================
AUTH_USER_MODEL = "accounts.User"
# Purpose: Custom user model for email-based auth and 2FA.

# =============================================================
# MIDDLEWARE
# =============================================================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Static files handling
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",  
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
# Purpose: Handles security, sessions, CORS, CSRF, authentication, and clickjacking protection.

# =============================================================
# REST FRAMEWORK SETTINGS
# =============================================================
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_THROTTLE_CLASSES": ("rest_framework.throttling.UserRateThrottle",),
    "EXCEPTION_HANDLER": "core.exceptions.handlers.global_exception_handler",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}
# Purpose: Sets authentication, rate-limiting, filtering, pagination, and OpenAPI schema.

# =============================================================
# SIMPLE JWT SETTINGS
# =============================================================
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken", "accounts.helpers.TwoFAToken"),
}
# Purpose: JWT configuration for secure stateless authentication.

# =============================================================
# SPECTACULAR / OPENAPI
# =============================================================
SPECTACULAR_SETTINGS = {
    'TITLE': 'FreeAPI docs',
    'DESCRIPTION': 'Professional API documentation for FreeAPI Hub',
    'VERSION': 'v1',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': r'/api/v1/',
    'COMPONENT_SPLIT_REQUEST': True,
}
# Purpose: Auto-generates API documentation with DRF Spectacular.

# =============================================================
# URL & ASGI
# =============================================================
ROOT_URLCONF = "config.urls"
ASGI_APPLICATION = "config.asgi.application"

# Purpose: Configures URL routing and ASGI server entry point for WebSockets.

# =============================================================
# TEMPLATES
# =============================================================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
            ],
        },
    },
]
# Purpose: Template rendering for Django views.

# =============================================================
# EMAIL SETTINGS (SENDGRID)
# =============================================================
EMAIL_BACKEND = config("EMAIL_BACKEND", default="core.email.backend.SendGridBackend")
SENDGRID_API_KEY = config("SENDGRID_API_KEY")
EMAIL_FROM = config("EMAIL_FROM")
SENDGRID_EMAIL_VERIFICATION_TEMPLATE_ID = config("SENDGRID_EMAIL_VERIFICATION_TEMPLATE_ID")
SENDGRID_PASSWORD_RESET_TEMPLATE_ID = config("SENDGRID_PASSWORD_RESET_TEMPLATE_ID")
# Purpose: Configures SendGrid for sending emails and templates.

# =============================================================
# EMAIL & AUTH TOKEN EXPIRY
# =============================================================
EMAIL_VERIFICATION_EXPIRY_HOURS = config("EMAIL_VERIFICATION_EXPIRY_HOURS", default=24, cast=int)
PASSWORD_RESET_EXPIRY_HOURS = config("PASSWORD_RESET_EXPIRY_HOURS", default=1, cast=int)
# Purpose: Token expiry durations for email verification and password reset.

# =============================================================
# TWO-FACTOR AUTH (TOTP)
# =============================================================
TOTP_ISSUER_NAME = config("TOTP_ISSUER_NAME", default="FreeAPI")
# Purpose: TOTP issuer name for authenticator apps.

# =============================================================
# FRONTEND URL
# =============================================================
FRONTEND_URL = config("FRONTEND_URL", default="http://localhost:5173")
# Purpose: Frontend URL used in email links and redirects.

# =============================================================
# THIRD-PARTY INTEGRATIONS
# =============================================================
# Google OAuth
GOOGLE_CLIENT_ID = config("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = config("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = config("GOOGLE_REDIRECT_URI")

# GitHub OAuth
GITHUB_CLIENT_ID = config("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = config("GITHUB_CLIENT_SECRET")
GITHUB_REDIRECT_URI = config("GITHUB_REDIRECT_URI")

# Cloudinary
CLOUDINARY_CLOUD_NAME = config("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = config("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = config("CLOUDINARY_API_SECRET")

# Payment keys
STRIPE_PUBLIC_KEY = config("STRIPE_PUBLIC_KEY")
STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY")
RAZORPAY_KEY_ID = config("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = config("RAZORPAY_KEY_SECRET")
# Purpose: External service credentials for OAuth, media, and payments.

# =============================================================
# DATABASE
# =============================================================
if ENV == "local":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": dj_database_url.parse(
            config("DATABASE_URL"),
            conn_max_age=600,
            ssl_require=True,
        )
    }
# Purpose: SQLite for local dev; production uses Postgres via DATABASE_URL.

# =============================================================
# CHANNELS / WEBSOCKETS
# =============================================================
if ENV == "local":
    CHANNEL_LAYERS = {
        "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"},
    }
else:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {"hosts": [config("REDIS_URL", default="redis://127.0.0.1:6379")]},
        },
    }
# Purpose: WebSocket backend; Redis in production, in-memory in local dev.

# =============================================================
# PASSWORD VALIDATORS
# =============================================================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
# Purpose: Enforces strong password policies.

# =============================================================
# INTERNATIONALIZATION
# =============================================================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
# Purpose: Standard i18n and timezone settings.

# =============================================================
# STATIC & MEDIA FILES
# =============================================================
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
# Purpose: Storage paths for static and uploaded media.

# =============================================================
# STATIC FILES STORAGE (WHITENOISE)
# =============================================================
STORAGES = {
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
# Purpose: Efficient static file serving with compression and caching.

# =============================================================
# DEFAULT PRIMARY KEY FIELD
# =============================================================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
# Purpose: Default PK type for new models; avoids collisions in large apps.
