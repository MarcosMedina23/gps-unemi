"""
Enrutador principal de UNEMI Guide AI.

Mapa del sitio:
    /                           -> Interfaz web (apps.web, plantillas Django)
    /admin/                     -> Panel de administración de Django
    /api/v1/usuarios/           -> API: registro, login y perfil
    /api/v1/zonas/              -> API: zonas, destinos y reconocimiento por foto
    /api/v1/rutas/              -> API: cálculo e historial de rutas

La API REST queda lista para una futura app móvil; la interfaz web no
la necesita porque llama a los servicios de Python directamente.
"""
from django.contrib import admin
from django.urls import include, path

API_PREFIX = "api/v1/"

urlpatterns = [
    path("admin/", admin.site.urls),
    path(f"{API_PREFIX}usuarios/", include("apps.users.urls")),
    path(f"{API_PREFIX}zonas/", include("apps.zones.urls")),
    path(f"{API_PREFIX}rutas/", include("apps.routes.urls")),
    path("", include("apps.web.urls")),
]
