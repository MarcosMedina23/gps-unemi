"""
Procesadores de contexto: variables disponibles en TODAS las plantillas.

Registrado en settings.TEMPLATES["OPTIONS"]["context_processors"].
"""
from .sesion import SesionNavegacion

# Menú principal: (nombre de la URL, texto visible).
# La navbar se construye desde aquí, no a mano en cada plantilla.
ENLACES_PUBLICOS = (
    ("inicio", "Inicio"),
)
ENLACES_PRIVADOS = (
    ("panel", "Mi panel"),
    ("camara", "Reconocer zona"),
    ("ruta", "Mi ruta"),
    ("simulacion", "Vista 3D"),
)


def navegacion(request):
    """Usuario actual y enlaces del menú con el enlace activo marcado."""
    sesion = SesionNavegacion(request)
    url_actual = getattr(request.resolver_match, "url_name", None)
    enlaces = ENLACES_PUBLICOS + (ENLACES_PRIVADOS if sesion.esta_autenticado else ())

    return {
        "usuario_actual": sesion.usuario,
        "enlaces_navegacion": [
            {"url_name": f"web:{nombre}", "texto": texto, "activo": nombre == url_actual}
            for nombre, texto in enlaces
        ],
    }
