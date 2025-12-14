from pathlib import Path
from datetime import timedelta
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

load_dotenv(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = 'django-insecure-@n#1)ra@2u%0ive72f166h@@b#7dw(cv+u2u3-y90srw-vm4)q'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
     "unfold",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',   
    'drf_yasg',         
    'project',
    'myapi',
    'jobs',  
    'profiles',
    'rest_framework.authtoken',
    'chat',
    'channels',
    'choices_manager',  
    'import_export'
]

#SITE_ID = 1

# --- Allauth + Email Verification + Social Auth REMOVED COMPLETELY ---

REST_AUTH = {
    'USE_JWT': True,
    'JWT_AUTH_HTTPONLY': False,
    'USER_DETAILS_SERIALIZER': 'myapi.serializers.UserDetailsSerializer',
}

LOGIN_REDIRECT_URL = '/auth/success/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

MIDDLEWARE = [ 
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://192.168.1.7:3000",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://206.189.134.117"
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://192.168.1.7:3000",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://206.189.134.117"
]

CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = 'IhrHub.urls'

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

WSGI_APPLICATION = 'IhrHub.wsgi.application'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ihrhubnew',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.environ.get('DATABASE_NAME', 'AASDB'),
#         'USER': os.environ.get('DATABASE_USER', 'postgres'),
#         'PASSWORD': os.environ.get('DATABASE_PASSWORD', 'postgres'),
#         'HOST': os.environ.get('DATABASE_HOST', 'db'),
#         'PORT': os.environ.get('DATABASE_PORT', '5432'),
#     }
# }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': "JWT Authorization header using the Bearer scheme. Example: 'Bearer <your_token>'",
        }
    },
    'USE_SESSION_AUTH': False,
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    ),
}


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

ASGI_APPLICATION = "IhrHub.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}

UNFOLD ={
    'ADMIN_SITE_HEADER': 'IhrHub Administration',
    'ADMIN_SITE_TITLE': 'IhrHub Admin',
    'ADMIN_INDEX_TITLE': 'Welcome to IhrHub Admin Panel',
}