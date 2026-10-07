"""
Vistas de la interfaz web de UNEMI Guide AI.

Cada vista prepara los datos en Python y los entrega a una plantilla de
``frontend/pages/``. Se sigue el patrón POST → Redirect → GET para que al
recargar la página no se reenvíen los formularios.

    /              InicioView      Página de presentación.
    /acceso/       AccesoView      Inicio de sesión y registro.
    /salir/        SalirView       Cierre de sesión (solo POST).
    /panel/        PanelView       Resumen del estudiante.
    /camara/       CamaraView      Reconocimiento de zona por foto.
    /ruta/         RutaView        Cálculo de la ruta más corta.
    /simulacion/   SimulacionView  Recorrido en 3D.
"""
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.dateparse import parse_datetime
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import TemplateView

from apps.routes.services import RutaNoEncontradaError
from apps.users import services as servicios_usuarios
from apps.vision.services import reconocer_zona
from apps.vision.utils import generar_miniatura_base64

from . import datos_demo, servicios
from .forms import FotoZonaForm, LoginForm, RegistroForm, SolicitudRutaForm
from .mixins import SesionRequeridaMixin
from .sesion import SesionNavegacion


class InicioView(TemplateView):
    """Página de presentación del proyecto."""

    template_name = "index.html"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["total_zonas"] = len(datos_demo.ZONAS)
        contexto["total_destinos"] = len(datos_demo.DESTINOS)
        return contexto


class AccesoView(View):
    """
    Inicio de sesión y registro en una misma página.

    El modo se elige con ``?modo=registro``; por defecto se muestra el
    inicio de sesión.
    """

    template_name = "login.html"

    def dispatch(self, request, *args, **kwargs):
        self.sesion = SesionNavegacion(request)
        if self.sesion.esta_autenticado:
            return redirect("web:panel")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        modo = "registro" if request.GET.get("modo") == "registro" else "login"
        return self._renderizar(request, modo, LoginForm(), RegistroForm())

    def post(self, request):
        if request.POST.get("accion") == "registro":
            return self._procesar_registro(request)
        return self._procesar_login(request)

    # ------------------------------------------------------------------
    def _procesar_login(self, request):
        formulario = LoginForm(request.POST, request=request)
        if not formulario.is_valid():
            return self._renderizar(request, "login", formulario, RegistroForm())

        usuario = formulario.usuario
        self.sesion.iniciar(usuario.datos_para_sesion())
        messages.success(request, f"¡Hola, {usuario.first_name}! Qué bueno verte.")
        return redirect(self._url_siguiente(request))

    def _procesar_registro(self, request):
        formulario = RegistroForm(request.POST)
        if not formulario.is_valid():
            return self._renderizar(request, "registro", LoginForm(), formulario)

        usuario = formulario.crear_usuario()  # Queda guardado en la base de datos.
        self.sesion.iniciar(usuario.datos_para_sesion())
        messages.success(request, f"¡Cuenta creada! Te damos la bienvenida, {usuario.first_name}.")
        return redirect("web:panel")

    def _url_siguiente(self, request):
        """Página a la que volver tras iniciar sesión (solo URLs internas)."""
        siguiente = request.POST.get("next") or request.GET.get("next")
        es_segura = url_has_allowed_host_and_scheme(
            siguiente, allowed_hosts={request.get_host()}, require_https=request.is_secure()
        )
        return siguiente if siguiente and es_segura else reverse("web:panel")

    def _renderizar(self, request, modo, formulario_login, formulario_registro):
        return render(
            request,
            self.template_name,
            {
                "modo": modo,
                "form_login": formulario_login,
                "form_registro": formulario_registro,
                "next": request.GET.get("next", request.POST.get("next", "")),
                "contrasena_demo": datos_demo.CONTRASENA_DEMO,
                "cuentas_de_prueba": datos_demo.CUENTAS_DE_PRUEBA,
            },
        )


class SalirView(View):
    """Cierra la sesión. Solo acepta POST para evitar cierres accidentales."""

    http_method_names = ["post"]

    def post(self, request):
        SesionNavegacion(request).cerrar()
        messages.info(request, "Cerraste sesión. ¡Vuelve pronto!")
        return redirect("web:inicio")


class PanelView(SesionRequeridaMixin, TemplateView):
    """Panel principal con el resumen de actividad del estudiante."""

    template_name = "dashboard.html"

    # Cuántas carreras se muestran en el apartado "Carreras que más usan la app".
    LIMITE_RANKING_CARRERAS = 5

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        historial = [
            {**ruta, "fecha": parse_datetime(ruta["fecha"])} for ruta in self.sesion.historial
        ]
        zona_actual = None
        if self.sesion.zona_reconocida_id:
            zona_actual = datos_demo.buscar_zona(self.sesion.zona_reconocida_id)

        contexto.update(
            {
                "historial": historial,
                "zona_actual": zona_actual,
                "ruta_actual": self.sesion.ruta_actual,
                "zonas": datos_demo.ZONAS,
                # Ranking de carreras de los estudiantes registrados.
                "ranking_carreras": servicios_usuarios.estadisticas_por_carrera(
                    limite=self.LIMITE_RANKING_CARRERAS
                ),
                "total_estudiantes": servicios_usuarios.total_estudiantes(),
                "estadisticas": {
                    "rutas": len(historial),
                    "metros": round(sum(ruta["distancia_metros"] for ruta in historial)),
                    "destinos": len(datos_demo.DESTINOS),
                },
            }
        )
        return contexto


class CamaraView(SesionRequeridaMixin, View):
    """Sube o toma una foto y reconoce la zona del campus."""

    template_name = "camera.html"

    def get(self, request):
        return self._renderizar(request, FotoZonaForm())

    def post(self, request):
        formulario = FotoZonaForm(request.POST, request.FILES)
        if not formulario.is_valid():
            return self._renderizar(request, formulario)

        imagen = formulario.cleaned_data["imagen"]
        resultado = reconocer_zona(imagen)
        zona = datos_demo.buscar_zona_por_codigo(resultado["zona"]["codigo"])

        if not resultado["reconocida"] or zona is None:
            messages.error(request, "No pudimos reconocer la zona. Intenta con otra foto.")
            return redirect("web:camara")

        self.sesion.reconocimiento = {
            "zona_id": zona.id,
            "confianza": resultado["confianza"],
            "modo": resultado["modo"],
            "miniatura": generar_miniatura_base64(imagen),
        }
        messages.success(request, f"Zona reconocida: {zona.nombre}.")
        return redirect("web:camara")

    def _renderizar(self, request, formulario):
        reconocimiento = self.sesion.reconocimiento
        zona = datos_demo.buscar_zona(reconocimiento["zona_id"]) if reconocimiento else None
        return render(
            request,
            self.template_name,
            {"form": formulario, "reconocimiento": reconocimiento, "zona": zona},
        )


class RutaView(SesionRequeridaMixin, View):
    """Elige un destino y calcula la ruta más corta (Dijkstra)."""

    template_name = "route.html"

    def get(self, request):
        # Si ya hay una ruta calculada, el formulario la muestra seleccionada.
        ruta = self.sesion.ruta_actual or {}
        formulario = SolicitudRutaForm(
            initial={
                "origen": ruta.get("zona_origen_id")
                or self.sesion.zona_reconocida_id
                or datos_demo.ZONAS[0].id,
                "destino": ruta.get("destino_id"),
            }
        )
        return self._renderizar(request, formulario)

    def post(self, request):
        formulario = SolicitudRutaForm(request.POST)
        if not formulario.is_valid():
            return self._renderizar(request, formulario)

        reconocimiento = self.sesion.reconocimiento or {}
        try:
            ruta = servicios.calcular_ruta(
                formulario.cleaned_data["zona_origen"],
                formulario.cleaned_data["destino_obj"],
                confianza=reconocimiento.get("confianza"),
            )
        except (KeyError, RutaNoEncontradaError):
            messages.error(request, "No encontramos un camino hacia ese destino.")
            return redirect("web:ruta")

        self.sesion.registrar_ruta(ruta)
        messages.success(request, f"Ruta lista: {ruta['distancia_metros']:.0f} m hasta tu destino.")
        return redirect(f"{reverse('web:ruta')}#resultado")

    def _renderizar(self, request, formulario):
        tipo = request.GET.get("tipo", "").upper()
        ruta = self.sesion.ruta_actual
        destino_elegido = formulario["destino"].value()

        return render(
            request,
            self.template_name,
            {
                "form": formulario,
                "destinos": datos_demo.filtrar_destinos(tipo),
                "destino_elegido": str(destino_elegido or ""),
                "tipos": datos_demo.TIPOS_DESTINO,
                "tipo_activo": tipo,
                "ruta": ruta,
                "mapa": servicios.construir_mapa_2d(ruta),
            },
        )


class SimulacionView(SesionRequeridaMixin, TemplateView):
    """Recorrido 3D de la ruta actual (Three.js dibuja lo que Python decide)."""

    template_name = "simulation.html"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        ruta = self.sesion.ruta_actual
        contexto["ruta"] = ruta
        contexto["escena"] = servicios.construir_escena_3d(ruta)
        return contexto
