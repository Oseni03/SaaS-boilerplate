from pathlib import Path
from os import getenv, path
from django.core.management.utils import get_random_secret_key

import sys
import dotenv
import datetime
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

dotenv_file = BASE_DIR / ".env.local"

if path.isfile(dotenv_file):
    dotenv.load_dotenv(dotenv_file)

# Quick-start development settings - unsuitable for production

SECRET_KEY = getenv("DJANGO_SECRET_KEY", get_random_secret_key())

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = getenv("DEBUG", "False") == "True"

ALLOWED_HOSTS = getenv("DJANGO_ALLOWED_HOSTS", "127.0.00.1, localhost, api.localhost, admin.localhost").split(", ")


DEVELOPMENT_MODE = getenv("DEVELOPMENT_MODE", "False") == "True"

# Application definition

INSTALLED_APPS = [
    "daphne",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Internal Apps 
    "apps.users",
    # "apps.finances",
    "apps.notifications",
    
    # External Apps 
    'django_hosts',
    "rest_framework",
    "djoser",
    "storages",
    "social_django",
    "djstripe",
    "channels",
]

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
    # Django-hosts config
    'django_hosts.middleware.HostsResponseMiddleware',
]

ROOT_URLCONF = 'config.urls'
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


WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = "config.asgi.application"

# Database
if DEVELOPMENT_MODE is True:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
elif len(sys.argv) > 0 and sys.argv[1] != "collectstatic":
    if getenv("DATABASE_URL", None) is None:
        raise Exception("DATABASE_URL environment not defined")
    DATABASES = {
        "default": dj_database_url.parse(getenv("DATABASE_URL"))
    }

# Email Settings 
# EMAIL_BACKEND = "django_ses.SESBackend"
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = getenv("AWS_SES_FROM_EMAIL")

AWS_SES_ACCESS_KEY_ID = getenv("AWS_SES_ACCESS_KEY_ID")
AWS_SES_SECRET_ACCESS_KEY = getenv("AWS_SES_SECRET_ACCESS_KEY")
AWS_SES_REGION_NAME = getenv("AWS_SES_REGION_NAME")
AWS_SES_REGION_ENDPOINT = f"email.{AWS_SES_REGION_NAME}.amazonaws.com"
AWS_SES_FROM_EMAIL = getenv("AWS_SES_FROM_EMAIL")
USE_SES_V2 = True


DOMAIN = getenv("DOMAIN")
SITE_NAME = getenv("SITE_NAME")


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
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',
    "django.contrib.auth.backends.ModelBackend",
]

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = getenv("GOOGLE_AUTH_KEY")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = getenv("GOOGLE_AUTH_SECRET")
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]
SOCIAL_AUTH_GOOGLE_OAUTH2_EXTRA_DATA = ["first_name", "last_name"]

SOCIAL_AUTH_FACEBOOK_KEY = getenv("FACEBOOK_AUTH_KEY")
SOCIAL_AUTH_FACEBOOK_SECRET = getenv("FACEBOOK_AUTH_SECRET_KEY")
SOCIAL_AUTH_FACEBOOK_SCOPE = ["email"]
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    "fields": "email, first_name, last_name"
}

# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
if DEVELOPMENT_MODE is True:
    STATIC_URL = 'static/'
    STATIC_ROOT = BASE_DIR / "static"
    MEDIA_URL = "media/"
    MEDIA_ROOT = BASE_DIR / "media"
else:
    AWS_S3_ACCESS_KEY_ID = getenv("AWS_S3_ACCESS_KEY_ID")
    AWS_S3_SECRET_ACCESS_KEY = getenv("AWS_S3_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = getenv("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_REGION_NAME = getenv("AWS_S3_REGION_NAME")
    AWS_S3_ENDPOINT_URL = f"https://${AWS_S3_REGION_NAME}.digitaloceanspaces.com"
    AWS_S3_OBJECT_PARAMETERS = {
        "CacheControl": "max-age=86400",
    }
    AWS_DEFAULT_ACL = "public-read"
    AWS_LOCATION = "static"
    AWS_MEDIA_LOCATION = "media"
    AWS_S3_CUSTOM_DOMAIN = getenv("AWS_S3_CUSTOM_DOMAIN", default=None)
    STORAGES = {
        "default": {"BACKEND": "custom_storages.CustomS3Boto3Storage"},
        "staticfiles": {"BACKEND": "storages.backends.s3boto3.S3StaticStorage"},
    }

# Default primary key field type

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

HASHID_FIELD_SALT = getenv("HASHID_FIELD_SALT", get_random_secret_key())

AUTH_USER_MODEL = "users.User"

RATELIMIT_IP_META_KEY = "common.utils.get_client_ip"

SUBSCRIPTION_TRIAL_PERIOD_DAYS = getenv("SUBSCRIPTION_TRIAL_PERIOD_DAYS", default=7)

NOTIFICATIONS_STRATEGIES = ["InAppNotificationStrategy"]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': getenv('DJANGO_LOG_LEVEL', default='INFO'),
    },
    'loggers': {
        '*': {
            'handlers': ['console'],
            'level': getenv('DJANGO_LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
    },
}


DJOSER = {
    "TOKEN_MODEL": None,
    "SOCIAL_AUTH_REDIRECT_URIS": getenv('REDIRECT_URLS').split(",")
}

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        # "rest_framework.permissions.IsAuthenticated",
        "rest_framework.permissions.AllowAny",
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    "PAGE_SIZE": 20,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
}


OTP_AUTH_ISSUER_NAME = getenv("OTP_AUTH_ISSUER_NAME", default="")
OTP_AUTH_TOKEN_COOKIE = 'otp_auth_token'
OTP_AUTH_TOKEN_LIFETIME_MINUTES = datetime.timedelta(minutes=getenv('OTP_AUTH_TOKEN_LIFETIME_MINUTES', default=5))
OTP_VALIDATE_PATH = "/auth/validate-otp"


RATELIMIT_IP_META_KEY = "common.utils.get_client_ip"


STRIPE_TEST_PUBLIC_KEY = getenv("STRIPE_TEST_PUBLIC_KEY")
STRIPE_TEST_SECRET_KEY = getenv("STRIPE_TEST_SECRET_KEY")
STRIPE_LIVE_MODE = getenv("STRIPE_LIVE_MODE", "True") == "True"
DJSTRIPE_WEBHOOK_SECRET = getenv("DJSTRIPE_WEBHOOK_SECRET")  # We don't use this, but it must be set
DJSTRIPE_USE_NATIVE_JSONFIELD = False
DJSTRIPE_FOREIGN_KEY_TO_FIELD = "id"
DJSTRIPE_WEBHOOK_VALIDATION='retrieve_event' # "verify_signature"
STRIPE_CHECKS_ENABLED = getenv("STRIPE_CHECKS_ENABLED", default=True)
if not STRIPE_CHECKS_ENABLED:
    SILENCED_SYSTEM_CHECKS.append("djstripe.C001")


TASKS_BASE_HANDLER = getenv("TASKS_BASE_HANDLER", default="common.tasks.Task")
WORKERS_EVENT_BUS_NAME = getenv("WORKERS_EVENT_BUS_NAME", default=None)
AWS_ENDPOINT_URL = getenv("AWS_ENDPOINT_URL", default=None)
TASKS_LOCAL_URL = getenv("TASKS_LOCAL_URL", default=None)

UPLOADED_DOCUMENT_SIZE_LIMIT = getenv("UPLOADED_DOCUMENT_SIZE_LIMIT", default=10 * 1024 * 1024)
USER_DOCUMENTS_NUMBER_LIMIT = getenv("USER_DOCUMENTS_NUMBER_LIMIT", default=10)


CHANNEL_LAYERS = {
    "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"},
}

# CHANNEL_LAYERS = {
#     "default": {
#         "BACKEND": "channels_redis.core.RedisChannelLayer",
#         "CONFIG": {
#             "hosts": [("127.0.0.1", 6379)],
#         },
#     },
# }