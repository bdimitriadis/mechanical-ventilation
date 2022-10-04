"""
Django settings for hmv project.

Generated by 'django-admin startproject' using Django 2.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = <SECRET_KEY>

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'centers',
    'patients',
    'crispy_forms',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'centers.middleware.PasswordChangeMiddleware',
]

ROOT_URLCONF = 'hmv.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            ],
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


WSGI_APPLICATION = 'hmv.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': <DATABASE_ENGINE>  # e.g. 'django.db.backends.mysql',
        'NAME': <DATABASE_NAME>,
        'USER': <DATABASE_USER>,
        'PASSWORD': <DATABASE_PASSWORD>,
        'HOST': <HOST>,
        'PORT': <PORT>  # e.g. '3306',
        'OPTIONS': {
            'sql_mode': 'traditional',
        },
    }
}

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
    {
        'NAME': 'hmv.password_validators.ComplexPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'el-GR'
LANGUAGES = (
    ('el', _('Greek')),
)

TIME_ZONE = 'Europe/Athens'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DATE_INPUT_FORMATS = (
    '%d.%m.%Y', '%d.%m.%Y', '%d.%m.%y',  # '25.10.2006', '25.10.2006', '25.10.06'
    '%d-%m-%Y', '%d/%m/%Y', '%d/%m/%y',  # '25-10-2006', '25/10/2006', '25/10/06'
    '%d %b %Y',  # '25 Oct 2006',
    '%d %B %Y',  # '25 October 2006',
)

DATE_FORMAT = '%d.%m.%Y'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
CRISPY_TEMPLATE_PACK = 'bootstrap4'
LOGIN_REDIRECT_URL = '/search_add'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 1800
SESSION_SAVE_EVERY_REQUEST = True
# IMPORT_EXPORT_USE_TRANSACTIONS = False
DEFAULT_FROM_EMAIL = <FROM_EMAIL>
SERVER_EMAIL = <SERVER_EMAIL>
EMAIL_USE_TLS = <TRUE_OR_FALSE>
EMAIL_HOST = <EMAIL_HOST>
EMAIL_HOST_USER = <EMAIL_HOST_USER>
EMAIL_HOST_PASSWORD = <EMAIL_HOST_PASSWORD>
EMAIL_PORT = <EMAIL_PORT>

SITE_ROOT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] "
            "%(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'django_log': {
            'level': 'WARN',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': SITE_ROOT + "/django_log",
            'maxBytes': 50000000,
            'backupCount': 2,
            'formatter': 'standard',
        },
        'security_log': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': SITE_ROOT + "/security_log",
            'maxBytes': 50000000,
            'backupCount': 2,
            'formatter': 'standard',
        },
        'server_log': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': SITE_ROOT + "/server_log",
            'maxBytes': 50000000,
            'backupCount': 2,
            'formatter': 'standard',
        },
        'requests_log': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': SITE_ROOT + "/requests_log",
            'maxBytes': 50000000,
            'backupCount': 2,
            'formatter': 'standard',
        },
        'template_log': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': SITE_ROOT + "/template_log",
            'maxBytes': 50000000,
            'backupCount': 2,
            'formatter': 'standard',
        },
        'db_log': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': SITE_ROOT + "/db_log",
            'maxBytes': 50000000,
            'backupCount': 2,
            'formatter': 'standard',
        },
        'patients_app_log': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': SITE_ROOT + "/patients_app_log",
            'maxBytes': 50000000,
            'backupCount': 2,
            'formatter': 'standard',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'django_log'],
            'propagate': True,
            'level': 'WARN',
        },
        'django.request': {
            'handlers': ['console', 'requests_log'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.security.*': {
            'handlers': ['console', 'security_log'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['console', 'server_log'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.template': {
            'handlers': ['console', 'template_log'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console', 'db_log'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'patients': {
            'handlers': ['console', 'patients_app_log'],
            'level': 'DEBUG',
        },
    }
}
