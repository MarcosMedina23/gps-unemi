"""
Configuración WSGI de UNEMI Guide AI.

Expone la variable ``application`` que usan los servidores WSGI.
En desarrollo basta con ``python manage.py runserver``.
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()
