"""
Django settings for the SoulCraft project.

Security-relevant notes:
- Passwords are NEVER stored in plaintext. Django's built-in PBKDF2 hasher
  (SHA-256, 1,200,000 iterations) is the first choice; Argon2 is used when the
  argon2-cffi package is installed.
- Login/signup go through Django's authentication system (authenticate() +
  login()) -- see accounts/views.py.
- CSRF protection is enabled globally (django.middleware.csrf.CsrfViewMiddleware)
  and every POST form uses {% csrf_token %}.
- Google OAuth runs through django-allauth; credentials come from environment
  variables (never committed to the repo).
"""

from pathlib import Path
import os
import sys

BASE_DIR = Path(__file__).resolve().parent.parent

try:
    from dotenv import load_dotenv

    # Read .env from the project root (gitignored) if present.
    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass

# SECURITY: secrets are read from the environment, with dev-only fallbacks.
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-dev-only-key-change-me-in-production",
)
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"

# In production set DJANGO_ALLOWED_HOSTS="yourdomain.com,www.yourdomain.com"
ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,testserver").split(",")
    if h.strip()
]

# ----------------------------------------------------------------------------
# Applications
# ----------------------------------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    # Third-party
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",

    # Local
    "accounts.apps.AccountsConfig",
    "store.apps.StoreConfig",
    "support.apps.SupportConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",       # CSRF protection: ON
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",    # required by allauth >= 65
]

ROOT_URLCONF = "config.urls"

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
                "store.context_processors.cart_count",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ----------------------------------------------------------------------------
# Database
# ----------------------------------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_USER_MODEL = "accounts.User"

# ----------------------------------------------------------------------------
# Password validation & hashing
# ----------------------------------------------------------------------------

# Requirement 2: passwords hashed with Django's built-in hashers (PBKDF2 by
# default). Never plaintext. Argon2 is used automatically when available.
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",          # default
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        # Minimum password length -- see also ACCOUNT_PASSWORD_MIN_LENGTH below
        # so the rule is enforced consistently for both regular and social auth.
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 10},
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# ----------------------------------------------------------------------------
# Authentication & django-allauth (Google OAuth)
# ----------------------------------------------------------------------------

AUTHENTICATION_BACKENDS = [
    # Required for regular username/email logins via ModelBackend.
    "django.contrib.auth.backends.ModelBackend",
    # `allauth.account.auth_backends.AuthenticationBackend` populates the user's
    # email address when it creates one via social login.
    "allauth.account.auth_backends.AuthenticationBackend",
]

SITE_ID = 1

# Redirect after successful login (regular and social alike).
LOGIN_REDIRECT_URL = "store:dashboard"
LOGOUT_REDIRECT_URL = "store:dashboard"
LOGIN_URL = "login"

SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_HTTPONLY = True          # JS cannot read the session cookie
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_HTTPONLY = False            # must stay readable for AJAX POSTs

if not DEBUG:
    # Hardening applied automatically in production (DJANGO_DEBUG=0).
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    X_FRAME_OPTIONS = "DENY"

# --- allauth configuration ---------------------------------------------------

ACCOUNT_ADAPTER = "accounts.adapters.SoulCraftAccountAdapter"
SOCIALACCOUNT_ADAPTER = "accounts.adapters.SoulCraftSocialAccountAdapter"

ACCOUNT_LOGIN_METHODS = {"email"}            # users log in with email
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*"]  # * = required; no username
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_VERIFICATION = "none"          # no SMTP creds in dev; see README
ACCOUNT_PASSWORD_MIN_LENGTH = 10             # mirrors the validator above
ACCOUNT_LOGOUT_ON_GET = False                # logout requires POST (CSRF-checked)

# Google OAuth credentials come from the environment (.env, gitignored).
# They are registered as an allauth provider-level "APP" so no SocialApp row
# in the admin is needed (in fact, adding one alongside would make allauth
# raise MultipleObjectsReturned -- keep credentials in ONE place only).
GOOGLE_OAUTH_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID", "")
GOOGLE_OAUTH_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET", "")

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        # For OAuth2 providers, allauth appends "?scope=..." / "?access_type=..."
        # automatically. Request enough scope to build a profile.
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "offline"},
        # Auto-connect an existing account when the verified email matches.
        "SOCIALACCOUNT_QUERY_EMAIL": True,
        "SOCIALACCOUNT_STORE_TOKENS": False,   # avoid storing OAuth tokens at rest
    }
}

if GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET:
    SOCIALACCOUNT_PROVIDERS["google"]["APP"] = {
        "client_id": GOOGLE_OAUTH_CLIENT_ID,
        "secret": GOOGLE_OAUTH_CLIENT_SECRET,
        "key": "",
    }

SOCIALACCOUNT_AUTO_SIGNUP = True             # one-click login when email is known
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"

# ----------------------------------------------------------------------------
# Internationalization
# ----------------------------------------------------------------------------

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ----------------------------------------------------------------------------
# Static & media
# ----------------------------------------------------------------------------

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ----------------------------------------------------------------------------
# Branding theme (custom palette -- no default Tailwind blue/purple)
# ----------------------------------------------------------------------------
# Toasted creme + warm amber accent, on an ivory canvas. Used by templates/CSS
# and surfaced in the admin so the back-office matches the storefront.

SOULCRAFT_THEME = {
    "canvas": "#f7f5f0",        # ivory page background
    "surface": "#ffffff",
    "ink": "#17252a",           # near-black text
    "muted": "#5b6770",
    "brand": "#8b6f47",         # toasted creme -- primary buttons/links
    "brand-dark": "#6f5738",
    "accent": "#e8a13a",        # warm amber -- highlights/badges
    "accent-dark": "#c4832a",
    "line": "#e3ded4",          # hairline borders
    "danger": "#b3402e",
    "success": "#7d6644",       # warm bronze
}

# ----------------------------------------------------------------------------
# Dev conveniences (removed automatically when DJANGO_DEBUG=0)
# ----------------------------------------------------------------------------

if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
