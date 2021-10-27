import os
from decimal import ROUND_HALF_EVEN

import environ
import moneyed
import sentry_sdk
from django.conf.locale.en import formats as en_formats
from django.conf.locale.pt import formats as pt_formats
from django.utils.translation import gettext_lazy as _
from moneyed.localization import _FORMATTER
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env = environ.Env()
environ.Env.read_env(env_file=os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default='#thisisarandomstringandshouldbereplacedinenv')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ENV = os.environ.get('ENV', 'production')
ALLOWED_HOSTS = ['*']

SITE_URL = env('SITE_URL', default='http://localhost:8000/')

INTERNAL_IPS = [
    '127.0.0.1',
]

# Application definition
INSTALLED_APPS = [
    'test_without_migrations',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_nose',

    'django_admin_inline_paginator',
    'debug_toolbar',
    'rest_framework',
    'rest_framework_recursive',
    'admin_honeypot',
    'mptt',
    'djmoney',

    'apps.account',
    'apps.geo',
    'apps.budget',
    'frontend',
    'common'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': False,
        'OPTIONS': {
            'loaders': [
                'apptemplates.Loader',
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
SECURE_SSL_REDIRECT = True if ENV != 'dev' else False

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
DATABASES = {
    'default': env.db()
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators
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


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/
LANGUAGE_CODE = 'pt'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
LANGUAGES = [
    ('pt', _('Portuguese')),
    ('en', _('English')),
]
# Locale
LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, '.static')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'assets'),
]
MEDIA_ROOT = os.path.join(BASE_DIR, '.media')
MEDIA_URL = '/media/'

# AWS Settings
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', None)
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', None)
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', None)
if AWS_STORAGE_BUCKET_NAME:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/'

# Cache
if env('REDIS_URL', default=None):
    CACHES = {
        "default": {
             "BACKEND": "redis_cache.RedisCache",
             "LOCATION": env('REDIS_URL'),
        }
    }


# Celery
CELERY_BROKER_URL = os.environ.get("REDIS_URL", None)
CELERY_TASK_SERIALIZER = 'json'
#CELERY_TASK_IGNORE_RESULT = True
CELERY_TASK_STORE_ERRORS_EVEN_IF_IGNORED = True
CELERY_RESULT_BACKEND = os.environ.get("REDIS_URL", None)
CELERY_TASK_ALWAYS_EAGER = ENV == 'dev'
#CELERY_BROKER_POOL_LIMIT = 30
#CELERY_BROKER_TRANSPORT_OPTIONS = {'socket_timeout': 3600}


# Django-money
RAW_CURRENCY = moneyed.add_currency(
    code='RAW',
    numeric='999',
    name='Raw currency',
    countries=[]
)
_FORMATTER.add_sign_definition(
    'default',
    RAW_CURRENCY,
    prefix=''
)
_FORMATTER.add_formatting_definition(
    'RAW_CURRENCY',
    group_size=3, group_separator=".", decimal_point=",",
    positive_sign="",  trailing_positive_sign="",
    negative_sign="-", trailing_negative_sign="",
    rounding_method=ROUND_HALF_EVEN
)

CURRENCIES = ('USD', 'AOA', 'CVE', 'XOF', 'MZN', 'STD')
CURRENCY_CHOICES = [
    ('USD', 'USD $'),
    ('AOA', 'AOA Kz'),
    ('CVE', 'CVE $'),
    ('XOF', 'XOF (CFA)'),
    ('MZN', 'MZN MT'),
    ('STD', 'STD Db')
]

#                              N/A        0-20%    20-40%     40-60%     60-80%     80-100%
TREEMAP_EXECUTION_COLORS = ['#dfdfde', '#f9ea95', '#fcddd2', '#e8d0d0', '#e0d4e8', '#cfe1ed']
TREEMAP_EXECUTION_COLORS_HOVER = {
    TREEMAP_EXECUTION_COLORS[0]: '#7a8381',
    TREEMAP_EXECUTION_COLORS[1]: '#e0bd05',
    TREEMAP_EXECUTION_COLORS[2]: '#f2571c',
    TREEMAP_EXECUTION_COLORS[3]: '#8c1717',
    TREEMAP_EXECUTION_COLORS[4]: '#66298c',
    TREEMAP_EXECUTION_COLORS[5]: '#0f69a3',
}

TWITTER_URL = 'https://twitter.com/ProPALOP'
FACEBOOK_URL = 'https://www.facebook.com/propalop.tl/'
INSTAGRAM_URL = 'https://www.instagram.com/propaloptlisc/'
YOUTUBE_URL = 'https://www.youtube.com/channel/UCqQShed9k1_1tQqqduF_tcg'

# SENTRY
SENTRY_DSN = env('SENTRY_DSN', default=None)
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration(), CeleryIntegration()],
        environment=ENV,
        traces_sample_rate=1.0,
        debug=True
    )

en_formats.DATETIME_FORMAT = "d b Y H:i:s"
pt_formats.DATETIME_FORMAT = "d b Y H:i:s"