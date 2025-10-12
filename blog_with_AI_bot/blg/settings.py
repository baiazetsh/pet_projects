#settings.py
from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-iz#r+8v28-@evxh+g3)01$82r)en-pf53fnm7irkxsi&7dv41@'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

#ALLOWED_HOSTS = ['*']
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'web']



# Application definition

INSTALLED_APPS = [
    
    'django_prometheus',
    'rest_framework',
    'channels',
    'django_celery_results',
    'zz.apps.ZzConfig',
    'users.apps.UsersConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

ROOT_URLCONF = 'blg.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'blg.wsgi.application'

ASGI_APPLICATION = "blg.asgi.application"

# Redis для хранения сообщений каналов
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("redis", 6379)],  # или докер-контейнер
          
        },
    },
}


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = "America/New_York"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [ BASE_DIR / "static" ]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
USE_I18N = True
LANGUAGE_CODE = 'en-us'  # или 'ru', 'fr', и т.д.
LANGUAGES = [
    ('en', 'English'),
    ('ru', 'Русский'),
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
# settings.py

LLM_MODEL = "gemma3:1b"
LLM_URL = "http://ollama:11434" #for Docker
#LLM_URL = os.getenv("LLM_URL", "http://localhost:11434") # for local work

GROK_NAME_MODEL = "grok-4-fast-non-reasoning"
GROK_API_KEY = os.getenv("GROK_API_KEY")
GROK_URL = os.getenv("GROK_URL", "https://api.x.ai/v1/chat/completions")


CELERY_BROKER_URL = "redis://redis:6379/0"
#CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"
#CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/0"
CELERY_RESULT_BACKEND = "redis://redis:6379/1"

CELERY_IMPORTS = ('zz.tasks',)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"

#MINI_SERVER_URL = os.getenv("MINI_SERVER_URL", "http://10.0.0.240:11434")
#MINI_SERVER_URL = "http://host.docker.internal:11434"
MINI_SERVER_URL = "http://mini_server:11434"


# !!! Только для тестов, чтобы задачи выполнялись сразу
#CELERY_TASK_ALWAYS_EAGER = True

# Включить/выключить Celery для ботов

#USE_CELERY = False #→ использует threading с функцией generate_bot_reply_sync
USE_CELERY = True #→ использует Celery с задачей generate_bot_reply_task

TOPIC_SOURCES = [
    "hackernews",  # по умолчанию — только HN; расширим позже
    # "reddit",
    # "twitter",
    # "vc_ru",
    # "pikabu",
]
TOPIC_MIN_SCORE = 50
TOPIC_MIN_COMMENTS = 10
TOPIC_FETCH_LIMIT = 50

TOPIC_GENERATION_SOURCE = "local"   # 'local' | 'ollama' | 'grok'
TOPIC_GENERATION_BATCH = 10


