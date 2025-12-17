from pathlib import Path
from datetime import timedelta
import os
from dotenv import load_dotenv

# --------------------------------------------------
# BASE DIR & ENV
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, ".env"))

# --------------------------------------------------
# CORE SETTINGS (DEV)
# --------------------------------------------------
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "dev-insecure-secret-key-change-later"
)

DEBUG = True

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "206.189.134.117",
]

# --------------------------------------------------
# APPLICATIONS
# --------------------------------------------------
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
    'rest_framework.authtoken',
    'drf_yasg',

    'channels',
    'import_export',

    # Local apps
    'project',
    'myapi',
    'jobs',
    'profiles',
    'chat',
    'support',
    'choices_manager',
]

# --------------------------------------------------
# MIDDLEWARE (ORDER MATTERS)
# --------------------------------------------------
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # should be near top
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',  # needed for CSRF cookies
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # active here
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# --------------------------------------------------
# CORS / CSRF (DEV FRIENDLY)
# --------------------------------------------------
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://192.168.1.7:3000",
    "http://206.189.134.117",
]

CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS
CORS_ALLOW_CREDENTIALS = True

# --------------------------------------------------
# URLS / TEMPLATES
# --------------------------------------------------
ROOT_URLCONF = 'IhrHub.urls'

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

WSGI_APPLICATION = 'IhrHub.wsgi.application'
ASGI_APPLICATION = 'IhrHub.asgi.application'

# --------------------------------------------------
# DATABASE (DEV – LOCAL POSTGRES)
# --------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'ihrhubnew'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres'),
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# --------------------------------------------------
# PASSWORD VALIDATION
# --------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --------------------------------------------------
# LANGUAGE / TIME
# --------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Colombo'
USE_I18N = True
USE_TZ = True

# --------------------------------------------------
# STATIC FILES
# --------------------------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_STORAGE = (
    'whitenoise.storage.CompressedManifestStaticFilesStorage'
)

# --------------------------------------------------
# MEDIA FILES
# --------------------------------------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --------------------------------------------------
# DJANGO REST FRAMEWORK (DEV)
# --------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    ),
}

# --------------------------------------------------
# JWT (DEV)
# --------------------------------------------------
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
}

# --------------------------------------------------
# SWAGGER
# --------------------------------------------------
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': "Bearer <JWT>",
        }
    },
    'USE_SESSION_AUTH': False,
}

# --------------------------------------------------
# CHANNELS (DEV ONLY)
# --------------------------------------------------
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}

# --------------------------------------------------
# DEFAULT PK FIELD
# --------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --------------------------------------------------
# UNFOLD ADMIN
# --------------------------------------------------
UNFOLD = {
    'ADMIN_SITE_HEADER': 'IhrHub Administration',
    'ADMIN_SITE_TITLE': 'IhrHub Admin',
    'ADMIN_INDEX_TITLE': 'Welcome to IhrHub Admin Panel',
}

CSRF_COOKIE_HTTPONLY = False  # frontend needs access to CSRF cookie
