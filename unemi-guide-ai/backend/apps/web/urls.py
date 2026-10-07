"""
Rutas de la interfaz web.

Prefijo global: / (raíz del sitio).
"""
from django.urls import path

from . import views

app_name = "web"

urlpatterns = [
    path("", views.InicioView.as_view(), name="inicio"),
    path("acceso/", views.AccesoView.as_view(), name="acceso"),
    path("salir/", views.SalirView.as_view(), name="salir"),
    path("panel/", views.PanelView.as_view(), name="panel"),
    path("camara/", views.CamaraView.as_view(), name="camara"),
    path("ruta/", views.RutaView.as_view(), name="ruta"),
    path("simulacion/", views.SimulacionView.as_view(), name="simulacion"),
]
