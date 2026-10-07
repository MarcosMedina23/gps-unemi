#!/usr/bin/env python
"""
Utilidad de línea de comandos de Django para el proyecto UNEMI Guide AI.

Uso típico (cuando el proyecto se conecte):
    python manage.py makemigrations
    python manage.py migrate
    python manage.py runserver
"""
import os
import sys


def main():
    """Configura el módulo de settings y ejecuta el comando solicitado."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar Django. ¿Está instalado y activo el "
            "entorno virtual? Ejecuta: pip install -r requirements.txt"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
