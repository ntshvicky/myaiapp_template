import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-me')
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
ALLOWED_HOSTS = [host.strip() for host in os.environ.get('ALLOWED_HOSTS', '127.0.0.1,localhost,testserver,.vercel.app').split(',') if host.strip()]

AUTH_USER_MODEL = 'accounts.UserProfile'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/'     # or wherever you want users to land
LOGOUT_REDIRECT_URL = '/accounts/login/'

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'services.chatbot',
    'services.webpage_analysis',
    'services.image_generator',
    'services.video_generator',
    'services.music_generator',
    'services.document_chat',
    'services.content_writer',
    'services.email_manager',
    'services.resume_analysis',
    'services.image_chat',
    'services.compare_images',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',   # serve static files in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myaiapp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'myaiapp.wsgi.application'
ASGI_APPLICATION = 'myaiapp.asgi.application'

import sys
import dj_database_url

# DATABASE_URL env var wins (Vercel Postgres / Neon / Supabase / Railway)
_DATABASE_URL = os.environ.get("DATABASE_URL", "")

if _DATABASE_URL:
    DATABASES = {"default": dj_database_url.parse(_DATABASE_URL, conn_max_age=600)}
else:
    DATABASE_ENGINE = os.environ.get("DATABASE_ENGINE", "sqlite").lower()
    if DATABASE_ENGINE == "mysql":
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.mysql",
                "NAME": os.environ.get("MYSQL_DATABASE", "myaiapp_db"),
                "USER": os.environ.get("MYSQL_USER", "root"),
                "PASSWORD": os.environ.get("MYSQL_PASSWORD", ""),
                "HOST": os.environ.get("MYSQL_HOST", "localhost"),
                "PORT": os.environ.get("MYSQL_PORT", "3306"),
            }
        }
    else:
        # SQLite — store in /tmp on serverless so the filesystem is writable
        _DB_PATH = Path("/tmp/db.sqlite3") if os.environ.get("VERCEL") else BASE_DIR / "db.sqlite3"
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": _DB_PATH,
            }
        }

if "test" in sys.argv:
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise — serve static files in production without collectstatic
_IS_VERCEL = bool(os.environ.get("VERCEL"))
if _IS_VERCEL:
    # Use finders so WhiteNoise serves from STATICFILES_DIRS directly
    WHITENOISE_USE_FINDERS = True
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
else:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files: use /tmp on Vercel (serverless FS is read-only), local otherwise
MEDIA_URL = '/media/'
MEDIA_ROOT = Path("/tmp/media") if _IS_VERCEL else BASE_DIR / 'media'
