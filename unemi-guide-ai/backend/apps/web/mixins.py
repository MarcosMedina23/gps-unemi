"""
Mixins reutilizables para las vistas web.
"""
from urllib.parse import urlencode

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

from .sesion import SesionNavegacion


class SesionRequeridaMixin:
    """
    Protege una vista: si el usuario no ha iniciado sesión, lo envía a la
    página de acceso y recuerda la página a la que quería ir (``?next=``).
    """

    def dispatch(self, request, *args, **kwargs):
        self.sesion = SesionNavegacion(request)
        if not self.sesion.esta_autenticado:
            messages.info(request, "Inicia sesión para continuar.")
            parametros = urlencode({"next": request.get_full_path()})
            return redirect(f"{reverse('web:acceso')}?{parametros}")
        return super().dispatch(request, *args, **kwargs)
