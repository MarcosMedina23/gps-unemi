"""
Rutas de la aplicación ``routes``.

Prefijo global: /api/v1/rutas/
"""
from django.urls import path

from . import views

app_name = "routes"

urlpatterns = [
    path("calcular/", views.CalcularRutaView.as_view(), name="calcular"),
    path("historial/", views.HistorialRutasView.as_view(), name="historial"),
    path("<int:pk>/", views.RutaDetalleView.as_view(), name="detalle"),
]
