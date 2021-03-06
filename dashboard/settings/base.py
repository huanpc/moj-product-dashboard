"""
Django settings for dashboard project.

Generated by 'django-admin startproject' using Django 1.9.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""
import os
import sys
from datetime import date
import logging.config

from django_gov.settings import (
    REST_FRAMEWORK, API_VERSION, SWAGGER_SETTINGS, PING_JSON_KEYS,
    HEALTHCHECKS, AUTODISCOVER_HEALTHCHECKS, CORS_ORIGIN_ALLOW_ALL)

FINANCE_GROUP_NAME = 'Finance'

APPLICATION_CONTEXT = {
    'proposition_title': 'MoJ Product Tracker',
    'phase': 'alpha',
    'product_type': 'service',
    'feedback_url': '',
    'GA_KEY': os.environ.get('GA_KEY'),
}

# access to the dashboard is IP restricted, so there is no
# way to validate the schema from swagger.io
SWAGGER_SETTINGS['VALIDATOR_URL'] = None

# earliest start date to sync tasks from float.com
FLOAT_TASK_SYNC_STARTING_POINT = date(2015, 1, 1)

# starting point to calculate people cost based on
# tasks from float.com and rates in the dashboard.
# this is useful where we do not want to deal with
# recalculation of historical costs before the dashbaord
# is in use, which involves entering a lot of historical
# data such as old rates, old additional costs, and probable
# reconcilation with already published official figures.
PEOPLE_COST_CALCATION_STARTING_POINT = date(2016, 10, 1)

# used to work out the start date of a sync job from float.com.
# when syncing tasks, we have a start date in the past rather
# than today. this will make sure changes on historical tasks# get updated.
FLOAT_TASK_SYNC_START_FROM_DAYS_PRIOR_TO_TODAY = 90

# default number of weeks
DEFAULT_TASK_SYNC_WEEKS = 104


# Build paths inside the product like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
location = lambda x: os.path.abspath(os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..', x))

sys.path.insert(0, location('apps'))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'CHANGE_ME')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = [
    os.environ.get('ALLOWED_HOSTS', 'localhost'),
]

BASE_URL = os.environ.get('BASE_URL', 'http://localhost:8000')


def expand_admins_to_list(envvar):
    if not envvar:
        return []
    admins = envvar.replace("[['", "").replace("']]", "").split("'], ['")
    return [a.split("', '") for a in admins]


ADMINS = expand_admins_to_list(os.environ.get('ADMINS', []))

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'djcelery',
    'axes',
    'webpack_loader',

    'moj_template',
    'django_gov',
    'rest_framework_swagger',

    'dashboard.apps.dashboard.apps.DashboardConfig',
    'dashboard_auth',
    'reports',  # Optional - allows upload and download of xls reports
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

]

ROOT_URLCONF = 'dashboard.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [location('templates'), ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'dashboard.apps.dashboard.context_processors.application',
            ],
        },
    },
]

WSGI_APPLICATION = 'dashboard.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DB_NAME', 'dashboard'),
        'USER': os.environ.get('DB_USERNAME', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', ''),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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


AUTHENTICATION_BACKENDS = (
    'dashboard_auth.backends.ModelBackend',
)


# Django Axes settings

AXES_LOGIN_FAILURE_LIMIT = 5
AXES_LOCK_OUT_AT_FAILURE = True
AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP = True
AXES_LOCKOUT_TEMPLATE = 'admin/lockout.html'
AXES_COOLOFF_TIME = 1

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = False

USE_TZ = True

DATE_FORMAT = 'd/m/Y'

DATE_INPUT_FORMATS = [
    '%d/%m/%Y', '%Y-%m-%d'
]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_ROOT = location('static')
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    location('assets'),
)

FLOAT_API_TOKEN = os.environ.get('FLOAT_API_TOKEN')
FLOAT_URL = os.environ.get('FLOAT_URL')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'basic': {'format': '%(asctime)s - %(levelname)s - %(message)s'},
        'simple': {'format': '%(message)s'},
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'basic'
        },
        'command': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'WARN',
            'class': 'logging.FileHandler',
            'filename': 'output.log',
            'formatter': 'basic'
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'INFO'
        },
        'cache': {
            'handlers': ['console', 'file'],
            'level': 'INFO'
        },
        'command': {
            'handlers': ['command'],
            'level': 'INFO'
        }
    }
}
logging.config.dictConfig(LOGGING)


# RAVEN SENTRY CONFIG
if 'SENTRY_DSN' in os.environ:
    RAVEN_CONFIG = {
        'dsn': os.environ.get('SENTRY_DSN')
    }

    INSTALLED_APPS += [
        'raven.contrib.django.raven_compat',
    ]

    MIDDLEWARE_CLASSES = [
        'raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware',
    ] + MIDDLEWARE_CLASSES

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'IGNORE_EXCEPTIONS': True,
        }
    }
}
DJANGO_REDIS_LOG_IGNORED_EXCEPTIONS = True

CELERY_ACCEPT_CONTENT = ['yaml']
CELERY_TASK_SERIALIZER = 'yaml'
CELERY_RESULT_SERIALIZER = 'yaml'

CELERY_TIMEZONE = 'Europe/London'

CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend'

BROKER_TRANSPORT_OPTIONS = {
    'region': 'eu-west-1',
    'queue_name_prefix': os.environ.get('CELERY_QUEUE_PREFIX', 'dev-'),
    'polling_interval': 1,
    'visibility_timeout': 3600}

BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'sqs://')

if all([os.environ.get('SMTP_USER'),
        os.environ.get('SMTP_PASS'),
        os.environ.get('SMTP_HOST')]):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get('SMTP_HOST')
    EMAIL_HOST_USER = os.environ.get('SMTP_USER')
    EMAIL_HOST_PASSWORD = os.environ.get('SMTP_PASS')
    EMAIL_USE_TLS = True
    EMAIL_PORT = 587
    EMAIL_TIMEOUT = 10
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_EMAIL_FROM',
                                        'webmaster@localhost')
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


WEBPACK_LOADER = {
    'DEFAULT': {
        'CACHE': not DEBUG,
        'BUNDLE_DIR_NAME': location('assets/dist/'),
        'STATS_FILE': location('assets/dist/webpack-stats.json'),
        'IGNORE': ['.+\.hot-update.js', '.+\.map']
    }
}

SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

SESSION_EXPIRE_AT_BROWSER_CLOSE = not DEBUG
SESSION_COOKIE_AGE = 10 * 60

# .local.py overrides all the common settings.
try:
    from .local import *
except ImportError:
    pass
