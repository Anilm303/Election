from pathlib import Path
import os
import shutil
import tempfile

import dj_database_url


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
DEBUG = os.getenv("DEBUG", "False" if os.getenv("VERCEL") else "True").lower() == "true"

allowed_hosts = [
    h.strip()
    for h in os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost,.vercel.app").split(",")
    if h.strip()
]

for vercel_host_var in ("VERCEL_URL", "VERCEL_BRANCH_URL", "VERCEL_PROJECT_PRODUCTION_URL"):
    vercel_host = os.getenv(vercel_host_var)
    if vercel_host:
        allowed_hosts.append(vercel_host.replace("https://", "").replace("http://", ""))

ALLOWED_HOSTS = list(dict.fromkeys(allowed_hosts))

csrf_trusted_origins = [
    o.strip()
    for o in os.getenv(
        "CSRF_TRUSTED_ORIGINS",
        "http://127.0.0.1:8000,http://localhost:8000,https://*.vercel.app",
    ).split(",")
    if o.strip()
]

for vercel_host_var in ("VERCEL_URL", "VERCEL_BRANCH_URL", "VERCEL_PROJECT_PRODUCTION_URL"):
    vercel_host = os.getenv(vercel_host_var)
    if vercel_host:
        vercel_origin = vercel_host.replace("https://", "https://").replace("http://", "http://")
        if not vercel_origin.startswith("http://") and not vercel_origin.startswith("https://"):
            vercel_origin = f"https://{vercel_origin}"
        csrf_trusted_origins.append(vercel_origin)

CSRF_TRUSTED_ORIGINS = list(dict.fromkeys(csrf_trusted_origins))

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "crispy_forms",
    "crispy_bootstrap5",
    "django_filters",
    "rosetta",
    "voting",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "voting.middleware.EnsureSchemaMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "evoting.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "evoting.wsgi.application"

DATABASE_URL = (
    os.getenv("DATABASE_URL")
    or os.getenv("POSTGRES_URL_NON_POOLING")
    or os.getenv("POSTGRES_URL")
    or os.getenv("POSTGRES_PRISMA_URL")
)

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(DATABASE_URL, conn_max_age=600, ssl_require=not DEBUG)
    }
else:
    sqlite_name = BASE_DIR / "db.sqlite3"
    if os.getenv("VERCEL"):
        # Use OS temp dir (Vercel: /tmp) because deployment filesystem is read-only.
        sqlite_name = Path(tempfile.gettempdir()) / "db.sqlite3"
        source_sqlite = BASE_DIR / "db.sqlite3"
        if source_sqlite.exists() and not sqlite_name.exists():
            try:
                shutil.copy2(source_sqlite, sqlite_name)
            except OSError:
                # If copy fails, Django will initialize a new SQLite DB at /tmp.
                pass
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": sqlite_name,
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}
WHITENOISE_USE_FINDERS = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "voting.CustomUser"
AUTHENTICATION_BACKENDS = [
    "voting.auth_backends.UsernameOrEmailBackend",
]
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "home"
LOGIN_URL = "login"

# ============ REST Framework Configuration ============
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
    },
}

# ============ JWT Configuration ============
from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
}

# ============ CORS Configuration ============
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]
if not DEBUG:
    CORS_ALLOWED_ORIGINS.extend([
        f"https://{host}" for host in ALLOWED_HOSTS if not host.startswith(".")
    ])

# ============ Crispy Forms Configuration ============
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# ============ reCAPTCHA Configuration ============
RECAPTCHA_PUBLIC_KEY = os.getenv("RECAPTCHA_PUBLIC_KEY", "")
RECAPTCHA_PRIVATE_KEY = os.getenv("RECAPTCHA_PRIVATE_KEY", "")
SILENCED_SYSTEM_CHECKS = ["captcha.recaptcha_test_key_error"]

# ============ Email Configuration ============
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() == "true"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@evoting.com")

# ============ OTP Configuration ============
OTP_TOTP_ISSUER = "E-Voting System"
OTP_TIMEOUT = 300  # 5 minutes
OTP_LENGTH = 6
OTP_ALPHANUMERIC = False

# ============ Security Settings ============
MAX_LOGIN_ATTEMPTS = 5
LOGIN_ATTEMPT_TIMEOUT = 900  # 15 minutes in seconds
MAX_OTP_ATTEMPTS = 3

# ============ Media Files ============
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ============ Internationalization ============
LOCALE_PATHS = [
    BASE_DIR / "locale",
]

LANGUAGES = [
    ("en", "English"),
    ("ne", "Nepali"),
]

# ============ Logging Configuration ============
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "evoting.log",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
        },
        "voting": {
            "handlers": ["console", "file"],
            "level": "DEBUG" if DEBUG else "INFO",
        },
    },
}

# Create logs directory if it doesn't exist
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# ============ Session & Security ============
SESSION_ENGINE = "django.contrib.sessions.backends.db"  # Store sessions in database
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"  # Changed from Strict to allow proper session handling
SESSION_SAVE_EVERY_REQUEST = True  # Update session on every request to extend expiry
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
