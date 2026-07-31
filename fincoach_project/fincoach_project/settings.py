"""
Django settings for the FinCoach project.

Beginner note: this file is the "control panel" for the whole project.
It tells Django which apps exist, where templates/static files live,
and how the database is configured. You generally only touch this
when adding a new app or changing project-wide behavior.
"""

from pathlib import Path

# BASE_DIR points to the project's root folder. Every other path in this
# file is built relative to it, so the project works no matter where
# it's copied to on someone's computer.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep this secret in real deployment!
# For local development this placeholder is fine. Before deploying,
# generate a real one and load it from an environment variable instead
# of hardcoding it here.
SECRET_KEY = "django-insecure-REPLACE-THIS-BEFORE-DEPLOYING"

# DEBUG shows detailed error pages — great while building, but this
# MUST be False before this ever goes live publicly.
DEBUG = True

ALLOWED_HOSTS = []  # add your domain here when deploying

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "simulator",  # our Life Simulator app
    "financial_helper",
    "tracker",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "fincoach_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # project-level "templates" folder, for things shared across apps
        # (like base.html), on top of each app's own templates/ folder.
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "fincoach_project.wsgi.application"

# Using SQLite for now: a single file, zero setup, perfect for
# development and demos. Swap this for PostgreSQL later if/when
# the app needs to handle many simultaneous users.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
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

# Redirect users after login/logout
LOGIN_REDIRECT_URL = "/simulator/home/"
LOGOUT_REDIRECT_URL = "/simulator/"
LOGIN_URL = "/simulator/login/"

# Static files (CSS, JavaScript, 3D model files, brand assets)
STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# FinCoach brand colors, kept in one place so templates/CSS can reference
# them consistently. (Plain Python dict — imported into templates via a
# context processor later if we need it in many places.)
# ---------------------------------------------------------------------------
FINCOACH_COLORS = {
    "primary": "#4DC49B",
    "primary_dark": "#488C74",
    "white": "#FFFFFF",
    "deep_green": "#21815F",
    "accent": "#9FC35C",
    "text": "#000000",
}
