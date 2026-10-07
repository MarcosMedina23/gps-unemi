"""
Configuración principal de Django para UNEMI Guide AI.

IMPORTANTE: Este archivo contiene valores FICTICIOS pensados para la fase
académica del proyecto. Antes de publicar el sistema se deben reemplazar
las credenciales y la SECRET_KEY por valores reales (idealmente leídos
desde variables de entorno) y poner DEBUG = False.
"""
import os
from pathlib import Path

# ------------------------------------------------------------------
# Modo demostración
# ------------------------------------------------------------------
# True  -> Funciona SIN PostgreSQL, con un archivo SQLite (ideal para presentar).
# False -> Se usa PostgreSQL (requiere el servidor y "python manage.py migrate").
# Se cambia con la variable de entorno UNEMI_MODO_DEMO=0.
MODO_DEMO = os.environ.get("UNEMI_MODO_DEMO", "1") == "1"

# ------------------------------------------------------------------
# Rutas base
# ------------------------------------------------------------------
# BASE_DIR apunta a la carpeta "backend/".
BASE_DIR = Path(__file__).resolve().parent.parent

# FRONTEND_DIR apunta a la carpeta "frontend/" (plantillas y estáticos).
FRONTEND_DIR = BASE_DIR.parent / "frontend"

# ------------------------------------------------------------------
# Seguridad
# ------------------------------------------------------------------
# Clave de ejemplo. NUNCA usar en producción.
SECRET_KEY = "django-insecure-unemi-guide-ai-clave-de-ejemplo-cambiar"

# Modo desarrollo activado mientras el proyecto está en construcción.
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# ------------------------------------------------------------------
# Aplicaciones instaladas
# ------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
]

# Aplicaciones propias del proyecto (carpeta backend/apps/).
LOCAL_APPS = [
    "apps.users",
    "apps.zones",
    "apps.routes",
    "apps.vision",
    "apps.web",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ------------------------------------------------------------------
# Middleware
# ------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Las páginas de la interfaz viven en frontend/pages/.
        "DIRS": [FRONTEND_DIR / "pages"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.web.context_processors.navegacion",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ------------------------------------------------------------------
# Base de datos (PostgreSQL)
# ------------------------------------------------------------------
# Credenciales ficticias: aún no existe una base de datos real.
# El esquema equivalente está en database/init.sql.
DATABASE_POSTGRESQL = {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": "unemi_guide_ai",
    "USER": "unemi_admin",
    "PASSWORD": "cambiar_esta_clave",
    "HOST": "localhost",
    "PORT": "5432",
}

# En modo demo se usa SQLite: un único archivo, sin instalar nada. Ahí se
# GUARDAN las cuentas registradas (contraseñas cifradas) para que sigan
# existiendo al reiniciar el servidor. Se crea con "python manage.py migrate".
# Las zonas, destinos y rutas de la interfaz siguen en apps/web/datos_demo.py.
DATABASE_DEMO = {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": BASE_DIR / "unemi_demo.sqlite3",
}

DATABASES = {"default": DATABASE_DEMO if MODO_DEMO else DATABASE_POSTGRESQL}

# ------------------------------------------------------------------
# Autenticación
# ------------------------------------------------------------------
# Se usa un modelo de usuario personalizado (apps/users/models.py).
AUTH_USER_MODEL = "users.Usuario"

# La interfaz web (apps.web) funciona en MODO DEMOSTRACIÓN: guarda la
# sesión en archivos temporales en lugar de la base de datos, así puede
# presentarse sin PostgreSQL.
SESSION_ENGINE = "django.contrib.sessions.backends.file"
MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"
LOGIN_URL = "web:acceso"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ------------------------------------------------------------------
# Django REST Framework
# ------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

# ------------------------------------------------------------------
# Internacionalización (Ecuador)
# ------------------------------------------------------------------
LANGUAGE_CODE = "es-ec"
TIME_ZONE = "America/Guayaquil"
USE_I18N = True
USE_TZ = True

# ------------------------------------------------------------------
# Archivos estáticos y multimedia
# ------------------------------------------------------------------
STATIC_URL = "static/"
# CSS, JS e imágenes de la interfaz viven en frontend/assets/.
STATICFILES_DIRS = [FRONTEND_DIR / "assets"]

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ------------------------------------------------------------------
# Configuración del módulo de visión artificial (YOLOv8)
# ------------------------------------------------------------------
# Ruta donde se ubicará el modelo entrenado. Aún no existe.
VISION_MODEL_PATH = BASE_DIR / "apps" / "vision" / "weights" / "unemi_zonas.pt"

# Confianza mínima para aceptar una detección como válida (0 a 1).
VISION_CONFIDENCE_THRESHOLD = 0.60

# Tamaño máximo permitido para las fotos subidas (en megabytes).
VISION_MAX_IMAGE_SIZE_MB = 5
