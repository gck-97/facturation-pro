"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 5.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""
import os
import dj_database_url
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-*cjljq5k3hbne0(b98jsf!$%145$(mw0dc^1ki)pwynd6_)w4a'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['facturation-pro.onrender.com', 'localhost', '127.0.0.1']

CSRF_TRUSTED_ORIGINS = ['https://facturation-pro.onrender.com']

# Application definition

INSTALLED_APPS = [
    'colorfield', 
    'django.contrib.humanize',
    'core.apps.CoreConfig',
    'company_settings.apps.CompanySettingsConfig',
    'documents.apps.DocumentsConfig',
    'products.apps.ProductsConfig',
    'clients.apps.ClientsConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
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
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Si la variable d'environnement DATABASE_URL existe (sur Render), on l'utilise.
if 'DATABASE_URL' in os.environ:
    DATABASES['default'] = dj_database_url.config(conn_max_age=600)


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

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# config/settings.py
# ... (tout le reste de votre fichier settings.py) ...

# STATIC_URL = 'static/' # Cette ligne devrait déjà exister
# DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField' # Cette ligne devrait déjà exister

# --- Configuration des fichiers médias (pour les uploads utilisateurs comme le logo) ---
import os # Assurez-vous que os est importé (normalement il l'est déjà en haut du fichier)

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media') # BASE_DIR est normalement déjà défini en haut de settings.py

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'login' # 'login' sera le nom de notre future URL de connexion

# NOUVELLES LIGNES
LOGIN_REDIRECT_URL = '/' # Redirige vers la racine du site, qui est maintenant notre tableau de bord
LOGOUT_REDIRECT_URL = '/login/' # Où aller après une déconnexion



STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        # MODIFIEZ/AJOUTEZ CE BACKEND
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}