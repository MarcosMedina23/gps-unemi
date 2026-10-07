"""
Rutas de la aplicación ``zones``.

Prefijo global: /api/v1/zonas/

Se usa un SimpleRouter de DRF para generar automáticamente las rutas
de los ViewSets.
"""
from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import views

app_name = "zones"

router = SimpleRouter()
# "destinos" se registra primero para que no choque con /zonas/{id}/.
router.register("destinos", views.DestinoViewSet, basename="destino")
router.register("", views.ZonaViewSet, basename="zona")

urlpatterns = [
    path("reconocer/", views.ReconocerZonaView.as_view(), name="reconocer"),
    path("", include(router.urls)),
]
