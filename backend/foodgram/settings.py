import os
from pathlib import Path

from django.core.management.utils import get_random_secret_key
from dotenv import load_dotenv

from .constants import PAGE_SIZE

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY', get_random_secret_key())

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'host.docker.internal']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_filters',
    'recipes.apps.RecipesConfig',
    'users.apps.UsersConfig',
    'link_shortner.apps.LinkShortnerConfig',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'djoser',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'foodgram.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'foodgram.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.getenv('POSTGRES_DB', os.path.join(BASE_DIR, 'db.sqlite3')),
        'USER': os.getenv('POSTGRES_USER', 'django'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', ''),
        'PORT': os.getenv('DB_PORT', 5432)
    },
}

AUTH_USER_MODEL = 'users.MyUser'

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

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static_backend')
STATIC_URL = '/static_backend/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': PAGE_SIZE,
}


CORS_ALLOWED_ORIGINS = [
    'http://localhost:80',
    'http://host.docker.internal:80',
]


CSRF_TRUSTED_ORIGINS = [
    'http://localhost',
    'http://127.0.0.1'
]

CORS_ALLOW_CREDENTIALS = True

DJOSER = {
    'SERIALIZERS': {
        'user_create': 'users.serializers.CustomUserCreateSerializer',
        'user': 'users.serializers.UserDetailSerializer'
    },
    'LOGIN_FIELD': 'email',
    'PERMISSIONS': {
        'user': ['rest_framework.permissions.AllowAny'],
        'user_create': ['rest_framework.permissions.AllowAny'],
        'user_list': ['rest_framework.permissions.AllowAny'],
        'token_create': ['rest_framework.permissions.AllowAny'],
        'token_destroy': ['rest_framework.permissions.IsAuthenticated'],
    },
}
