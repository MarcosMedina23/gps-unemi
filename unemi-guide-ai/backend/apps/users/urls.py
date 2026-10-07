"""
Rutas de la aplicación ``users``.

Prefijo global: /api/v1/usuarios/
"""
from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("registro/", views.RegistroUsuarioView.as_view(), name="registro"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("perfil/", views.PerfilUsuarioView.as_view(), name="perfil"),
]
