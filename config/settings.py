"""Configuración mínima: la aplicación no guarda datos, así que no usa base de datos."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# En producción real la clave vendría de un secreto; aquí se lee del entorno.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "clave-solo-para-desarrollo-no-usar-en-produccion")
DEBUG = os.environ.get("DJANGO_DEBUG", "0") == "1"
# '*' simplifica la práctica (localhost, IP de la VM, nombre del contenedor).
# En un despliegue real se limitaría a los dominios propios.
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    "representacion",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": ["django.template.context_processors.request"]},
    }
]

WSGI_APPLICATION = "config.wsgi.application"

# Sin modelos ni sesiones: no hace falta base de datos.
DATABASES = {}

LANGUAGE_CODE = "es"
TIME_ZONE = "America/Tegucigalpa"
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
