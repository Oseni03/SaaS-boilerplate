from pathlib import Path
from django.core.management.utils import get_random_secret_key

import sys
import os
import datetime
import environ
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False),
)

# Take environment variables from .env file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production

SECRET_KEY = env("DJANGO_SECRET_KEY", default=get_random_secret_key())

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["127.0.00.1", "localhost", "api.localhost", "admin.localhost"])


DEVELOPMENT_MODE = env.bool("DEVELOPMENT_MODE", default=True)

# Application definition

INSTALLED_APPS = [
    "daphne",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    
    # Internal Apps 
    "apps.users",
    "apps.finances",
    "apps.notifications",
    "apps.websockets",
    
    # External Apps 
    "channels",
    'django_hosts',
    "rest_framework_simplejwt.token_blacklist",
    "storages",
    "djstripe",
    "widget_tweaks",
    # social apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
]

SITE_ID = 1

# Provider specific settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        # For each OAuth based provider, either add a ``SocialApp``
        # (``socialaccount`` app) containing the required client
        # credentials, or list them here:
        'APP': {
            'client_id': env("GOOGLE_AUTH_CLIENT_ID"),
            'secret': env("GOOGLE_AUTH_SECRET_KEY"),
            'key': env("GOOGLE_AUTH_KEY", default=""),
        },
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'OAUTH_PKCE_ENABLED': True,
    },
    'facebook': {
        'APP': {
            'client_id': env("FACEBOOK_AUTH_CLIENT_ID"),
            'secret': env("FACEBOOK_AUTH_SECRET_KEY"),
            'key': env("FACEBOOK_AUTH_KEY", default="")
        },
        'METHOD': 'oauth2',
        'SCOPE': ['email', 'public_profile'],
        'INIT_PARAMS': {'cookie': True},
        'FIELDS': [
            'id',
            'first_name',
            'last_name',
            'picture',
        ],
        'EXCHANGE_TOKEN': True,
        'VERIFIED_EMAIL': False,
        'GRAPH_API_URL': 'https://graph.facebook.com/v13.0',
    },
}


ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'


MIDDLEWARE = [
    # Django-hosts config
    'django_hosts.middleware.HostsRequestMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # allauth middleware
    "allauth.account.middleware.AccountMiddleware",
    # Django-hosts config
    'django_hosts.middleware.HostsResponseMiddleware',
]

ROOT_URLCONF = 'config.urls.main'
ROOT_HOSTCONF = "config.hosts"
DEFAULT_HOST = "main"
# PARENT_HOST = "localhost:8000"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
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


PASSWORD_HASHERS = env.list(
    "DJANGO_PASSWORD_HASHERS",
    default=[
        'django.contrib.auth.hashers.PBKDF2PasswordHasher',
        'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
        'django.contrib.auth.hashers.Argon2PasswordHasher',
        'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    ],
)


ASGI_APPLICATION = "config.asgi.application"
WSGI_APPLICATION = 'config.wsgi.application'

# Database
if DEVELOPMENT_MODE is True:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
elif len(sys.argv) > 0 and sys.argv[1] != "collectstatic":
    if env("DATABASE_URL", default="") is None:
        raise Exception("DATABASE_URL environment not defined")
    DATABASES = {
        "default": dj_database_url.parse(env("DATABASE_URL"))
    }

# Email Settings 
# EMAIL_BACKEND = "django_ses.SESBackend"
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = env("AWS_SES_FROM_EMAIL")

AWS_SES_ACCESS_KEY_ID = env("AWS_SES_ACCESS_KEY_ID")
AWS_SES_SECRET_ACCESS_KEY = env("AWS_SES_SECRET_ACCESS_KEY")
AWS_SES_REGION_NAME = env("AWS_SES_REGION_NAME")
AWS_SES_REGION_ENDPOINT = f"email.{AWS_SES_REGION_NAME}.amazonaws.com"
AWS_SES_FROM_EMAIL = env("AWS_SES_FROM_EMAIL")
USE_SES_V2 = True


DOMAIN = env("DOMAIN", default="localhost")
SITE_NAME = env("SITE_NAME", default="Saas Boilerplate")


# Password validation

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


AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
]


# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
if DEVELOPMENT_MODE is True:
    STATIC_URL = 'static/'
    # STATIC_ROOT = BASE_DIR / "static"
    MEDIA_URL = "media/"
    MEDIA_ROOT = BASE_DIR / "media"
    STATICFILES_DIRS = [
        BASE_DIR / "static",
        BASE_DIR / "media"
    ]
else:
    AWS_S3_ACCESS_KEY_ID = env("AWS_S3_ACCESS_KEY_ID")
    AWS_S3_SECRET_ACCESS_KEY = env("AWS_S3_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME")
    AWS_S3_ENDPOINT_URL = f"https://${AWS_S3_REGION_NAME}.digitaloceanspaces.com"
    AWS_S3_OBJECT_PARAMETERS = {
        "CacheControl": "max-age=86400",
    }
    AWS_DEFAULT_ACL = "public-read"
    AWS_LOCATION = "static"
    AWS_MEDIA_LOCATION = "media"
    AWS_S3_CUSTOM_DOMAIN = env("AWS_S3_CUSTOM_DOMAIN", default=None)
    STORAGES = {
        "default": {"BACKEND": "custom_storages.CustomS3Boto3Storage"},
        "staticfiles": {"BACKEND": "storages.backends.s3boto3.S3StaticStorage"},
    }
    
    AWS_QUERYSTRING_EXPIRE = env("AWS_QUERYSTRING_EXPIRE", default=60 * 60 * 24)
    AWS_CLOUDFRONT_KEY = os.environ.get('AWS_CLOUDFRONT_KEY', '').encode('ascii')
    AWS_CLOUDFRONT_KEY_ID = os.environ.get('AWS_CLOUDFRONT_KEY_ID', None)

# Default primary key field type

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

HASHID_FIELD_SALT = env("HASHID_FIELD_SALT", default=get_random_secret_key())

AUTH_USER_MODEL = "users.User"

LOGIN_REDIRECT_URL = "/users/profile/"

LOGIN_URL = "/users/login/"

RATELIMIT_IP_META_KEY = "common.utils.get_client_ip"

NOTIFICATIONS_STRATEGIES = ["InAppNotificationStrategy"]

ADMINS = [DEFAULT_FROM_EMAIL]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
            "include_html": True,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': env('DJANGO_LOG_LEVEL', default='INFO'),
    },
    'loggers': {
        '*': {
            'handlers': ['console'],
            'level': env('DJANGO_LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
    },
}


OTP_AUTH_ISSUER_NAME = SITE_NAME
OTP_AUTH_TOKEN_COOKIE = 'otp_token'
OTP_AUTH_TOKEN_LIFETIME_MINUTES = datetime.timedelta(minutes=env('OTP_AUTH_TOKEN_LIFETIME_MINUTES', default=5))
OTP_VALIDATE_PATH = "/auth/validate-otp"


RATELIMIT_IP_META_KEY = "common.utils.get_client_ip"


STRIPE_TEST_PUBLIC_KEY = env("STRIPE_TEST_PUBLIC_KEY")
STRIPE_PUBLISHABLE_KEY = env("STRIPE_PUBLISHABLE_KEY")
STRIPE_LIVE_MODE = env.bool("STRIPE_LIVE_MODE", default=False)
DJSTRIPE_WEBHOOK_SECRET = env("DJSTRIPE_WEBHOOK_SECRET")  # We don't use this, but it must be set
DJSTRIPE_USE_NATIVE_JSONFIELD = False
DJSTRIPE_FOREIGN_KEY_TO_FIELD = "id"
DJSTRIPE_WEBHOOK_VALIDATION="retrieve_event" # verify_signature
# DJSTRIPE_SUBSCRIBER_MODEL = "users.Profile"
STRIPE_CHECKS_ENABLED = env.bool("STRIPE_CHECKS_ENABLED", default=True)
if not STRIPE_CHECKS_ENABLED:
    SILENCED_SYSTEM_CHECKS.append("djstripe.C001")
SUBSCRIPTION_ENABLE = env.bool("SUBSCRIPTION_ENABLE", default=True)
SUBSCRIPTION_HAS_TRIAL_PERIOD_OR_FREE = env.bool("SUBSCRIPTION_HAS_TRIAL_PERIOD_OR_FREE", default=True)
SUBSCRIPTION_TRIAL_PERIOD_DAYS = env.int("SUBSCRIPTION_TRIAL_PERIOD_DAYS", default=7)
SUBSCRIPTION_TRIAL_OR_FREE_PRODUCT_ID = env("SUBSCRIPTION_TRIAL_PRODUCT_ID", default=None)


TASKS_BASE_HANDLER = env("TASKS_BASE_HANDLER", default="common.tasks.Task")
WORKERS_EVENT_BUS_NAME = env("WORKERS_EVENT_BUS_NAME", default=None)
AWS_ENDPOINT_URL = env("AWS_ENDPOINT_URL", default=None)
TASKS_LOCAL_URL = env("TASKS_LOCAL_URL", default=None)

UPLOADED_DOCUMENT_SIZE_LIMIT = env.int("UPLOADED_DOCUMENT_SIZE_LIMIT", default=10 * 1024 * 1024)
USER_DOCUMENTS_NUMBER_LIMIT = env.int("USER_DOCUMENTS_NUMBER_LIMIT", default=10)


# # Channels configurations
if DEVELOPMENT_MODE is True:
    CHANNEL_LAYERS = {
        "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"},
    }
else:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [(
                    env("REDIS_IP_ADDRESS"), 
                    env("REDIS_PORT"), 
                )],
            },
        },
    }