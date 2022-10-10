"""
Django settings for PTD project.

Generated by 'django-admin startproject' using Django 4.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import os
import dj_database_url
from pathlib import Path
# from main.models import User

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY', 'pdk8bcv@oy$o4asp2100ymrv(0y$&qy5#oh-i($2s=j4fa4uvp')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(os.environ.get('DJANGO_DEBUG', '') != 'False')

ALLOWED_HOSTS = ['platinum-dragons.herokuapp.com', '127.0.0.1', 'localhost']
CSRF_TRUSTED_ORIGINS = ['https://platinum-dragons.herokuapp.com']

# Application definition
CORS_ORIGIN_WHITELIST = ('127.0.0.1:8000',)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'channels',
    'captcha',
    'tinymce',
    'django_crontab',
    "debug_toolbar",


    'main.apps.MainConfig',
    'chat.apps.ChatConfig',
    'services.apps.ServicesConfig',
    'tournaments.apps.TournamentsConfig'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

# White noise уменьшенный размер статических файлов
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

INTERNAL_IPS = [
    "127.0.0.1",
]

ROOT_URLCONF = 'PTD.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

# WSGI_APPLICATION = 'PTD.wsgi.application'
ASGI_APPLICATION = 'PTD.asgi.application'

# CHANNEL_LAYERS = {
#     "default": {
#         "BACKEND": "channels.layers.InMemoryChannelLayer"
#     }
# }

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.environ.get('REDIS_URL', 'redis://localhost:6379')],
        },
    },
}

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DB_NAME = os.environ.get('DB_NAME', 'ptd_base')
DB_USER = os.environ.get('DB_USER', 'PTDBaseUser')
DB_PASSWORD = os.environ.get('DB_NAME', 'Gelo228lox')
DATABASES = {}


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': 'localhost',
        # 'PORT': '8000',
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
#         'NAME': os.environ.get('POSTGRES_DB', 'db_name'),
#         'USER': os.environ.get('POSTGRES_USER', 'username'),
#         'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'password'),
#         'PORT': os.environ.get('POSTGRES_PORT', '5432'),
#     }
# }

db_from_env = dj_database_url.config(conn_max_age=5)
DATABASES['default'].update(db_from_env)

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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

AUTH_USER_MODEL = 'main.User'

AUTHENTICATION_BACKENDS = (
    'main.backends.AuthBackend',
    # 'django.contrib.auth.backends.ModelBackend'
)

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = []

# The absolute path to the directory where collectstatic will collect static files for deployment on Heroku.
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Sessions settings
SESSION_COOKIE_AGE = 1 * 24 * 60 * 60

# Tournament Status Messages
STATUS_MSG = {
    'open': 'Приём заявок',
    'low_spaces': 'Места на турнире заканчиваются',
    'soon_start': 'Турнир скоро начнется',
    'started': 'Турнир в процессе игры',
    'finished': 'Турнир заверщен',
    'failed': 'Турнир не состоялся',
}

# Cron Excercises
CRONJOBS = [
    ('0 0 * * *', 'main.cron.check_tournaments'),
    ('0 0 * * *', 'main.cron.clearsessions'),
]

# Caches
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BASE_DIR, 'ptd_cache'),
    }
}

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'smtp.mail.ru'
EMAIL_PORT = 2525
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'muhabrot@mail.ru')
EMAIL_HOST_PASSWORD = os.environ.get(
    'EMAIL_HOST_PASSWORD', 'cD0eEWTPg3gSwUCJKJ3e')

SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']
RECAPTCHA_PUBLIC_KEY = os.environ.get(
    'RECAPTCHA_PUBLIC_KEY', '6Le5PLIgAAAAAET5Foqsxi5OL2xpo-kQxca30XGF')
RECAPTCHA_PRIVATE_KEY = os.environ.get(
    'RECAPTCHA_PRIVATE_KEY', '6Le5PLIgAAAAADNd-a66kfmxhupP-jIPsj2VNFRo')
RECAPTCHA_REQUIRED_SCORE = 0.6
