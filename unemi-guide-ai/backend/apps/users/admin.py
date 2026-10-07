"""
Panel de administración de usuarios (/admin/).

Permite consultar el registro completo de cuentas creadas, filtrarlas por
carrera, rol o fecha de registro y buscarlas por nombre o correo.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """Administración del modelo de usuario personalizado."""

    list_display = ("email", "get_full_name", "carrera", "rol", "date_joined", "is_active")
    list_filter = ("carrera", "rol", "es_nuevo_ingreso", "is_active", "date_joined")
    search_fields = ("email", "first_name", "last_name", "cedula")
    ordering = ("-date_joined",)
    date_hierarchy = "date_joined"

    fieldsets = UserAdmin.fieldsets + (
        (
            "Datos UNEMI",
            {"fields": ("cedula", "rol", "carrera", "semestre", "es_nuevo_ingreso")},
        ),
    )
