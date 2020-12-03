import os
import environ
import moneyed
from moneyed.localization import _FORMATTER
from decimal import ROUND_HALF_EVEN
from django.utils.translation import gettext_lazy as _

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

INTERNAL_IPS = [
    '127.0.0.1',
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

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
AWS_ACCESS_KEY_ID=os.environ.get('AWS_ACCESS_KEY_ID', None)
AWS_SECRET_ACCESS_KEY=os.environ.get('AWS_SECRET_ACCESS_KEY', None)
AWS_STORAGE_BUCKET_NAME=os.environ.get('AWS_STORAGE_BUCKET_NAME', None)
if AWS_STORAGE_BUCKET_NAME:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'


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

TREEMAP_EXECUTION_COLORS = ['#f2cc05', '#f2571c', '#8c1717', '#66298c', '#0f69a3']
