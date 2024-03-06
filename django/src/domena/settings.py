"""
Django settings for domena project.

Generated by 'django-admin startproject' using Django 4.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os

from pathlib import Path
from datetime import timedelta
from rest_framework.settings import api_settings

from .plugins import PLUGINS
from devices.plugin_loader import scan_for_plugin

import logging
import json

# a server version
SERVER_VERSION="0.5"

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


ROOT_API_PATH=os.getenv("FETCH_API_ROOT_PATH")


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
if os.environ.get("DJANGO_MODE")=='DEBUG':
    DEBUG = True
else:
    DEBUG = False

ALLOWED_HOSTS = ["zerotwo.konar.pwr.edu.pl","staging.zerotwo.tenere.konar.pwr.edu.pl"]
CORS_ALLOWED_ORIGINS = ["https://zerotwo.konar.pwr.edu.pl", "https://staging.zerotwo.tenere.konar.pwr.edu.pl"]
CSRF_TRUSTED_ORIGINS=["https://zerotwo.konar.pwr.edu.pl", "https://staging.zerotwo.tenere.konar.pwr.edu.pl"]

INTERNAL_IPS = [
    "127.0.0.1",
    "tailwind",
    "web"
]

if os.environ.get("DJANGO_MODE")=='DEBUG':
    ALLOWED_HOSTS.extend([os.environ.get('IP_ADDR'),"localhost"])
    CORS_ALLOWED_ORIGINS.extend(["http://"+os.environ.get('IP_ADDR') ,"http://localhost"])
    CSRF_TRUSTED_ORIGINS.extend(["http://"+os.environ.get('IP_ADDR'),"http://localhost"])

# Application definition
    
PLUGINS_LIST=scan_for_plugin()

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'dbbackup',
    'auth02',
    'devices',
    'nodeacl',
    'nodes',
    'importer',
    'rest_framework',
    'knox',
    'allauth',
    'allauth.account',
    'tailwind',
    'theme'
] + PLUGINS_LIST+['mqtt']

if os.environ.get("DJANGO_MODE")=='DEBUG':
    INSTALLED_APPS.append('django_browser_reload')
    

TAILWIND_APP_NAME = 'theme'

TAILWIND_CSS_PATH = 'css/dist/styles.css'


MQTT_SERVER="mqtt"
MQTT_USER=os.environ.get('MQTT_USER')
MQTT_PASSWORD=os.environ.get('MQTT_PASSWORD')
MQTT_PORT=int(os.environ.get('MQTT_PORT'))
MQTT_KEEPALIVE =int(os.environ.get('MQTT_KEEPALIVE'))

DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': '/app/backups'}

AUTH_USER_MODEL = 'auth02.O2User' 

NODES_IMPORT_PATH="/app/nodes/imported/"


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware'
    ]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
]

AUTHENTICATION_BACKENDS=["allauth.account.auth_backends.AuthenticationBackend"
                         ,"django.contrib.auth.backends.ModelBackend"]

if os.environ.get("DJANGO_MODE")=='DEBUG':
    MIDDLEWARE.append("django_browser_reload.middleware.BrowserReloadMiddleware")

if bool(os.getenv("USE_EAUTH")):
    INSTALLED_APPS.append('allauth.socialaccount')

    SOCIALACCOUNT_LOGIN_ON_GET=True
    ACCOUNT_DEFAULT_HTTP_PROTOCOL="https"

    try:
        with open("/app/auth.json","r") as data:
            auths=json.load(data)
            for serv in auths.keys():
                INSTALLED_APPS.append('allauth.socialaccount.providers.'+str(serv))

            SOCIALACCOUNT_PROVIDERS=auths
    except OSError:
        logging.error("Cannot open auth.json file!")

ACCOUNT_AUTHENTICATION_METHOD="username"
ACCOUNT_CHANGE_EMAIL=True
ACCOUNT_EMAIL_VERIFICATION='none'


ROOT_URLCONF = 'domena.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'domena.context_pre.menu_items'
            ],
        },
    },
]

WSGI_APPLICATION = 'domena.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME':os.environ.get('POSTGRES_DB'),
        'USER':os.environ.get('POSTGRES_USER'),
        'PASSWORD':os.environ.get('POSTGRES_PASSWORD'),
        'HOST':'db',
        'PORT':os.environ.get('POSTGRES_PORT')
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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


LOGIN_REDIRECT_URL="/"

ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS=True

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = os.environ.get('TIME_ZONE')

USE_I18N = True

USE_TZ = True

DEFAULT_SESSION_TIME=360

api_settings.DATETIME_FORMAT='iso-8601'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'knox.auth.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        )
}

REST_KNOX = {
  'SECURE_HASH_ALGORITHM': 'cryptography.hazmat.primitives.hashes.SHA512',
  'AUTH_TOKEN_CHARACTER_LENGTH': 64,
  'TOKEN_TTL': timedelta(hours=10),
  'USER_SERIALIZER': 'knox.serializers.UserSerializer',
  'TOKEN_LIMIT_PER_USER': None,
  'AUTO_REFRESH': False,
  'EXPIRY_DATETIME_FORMAT': api_settings.DATETIME_FORMAT,
}



# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


STATIC_ROOT = str("/web/static")
# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = "/static/"
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = ["/app/static/","/app/theme/static/"]
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str("/web/media")
# https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = "/media/"
