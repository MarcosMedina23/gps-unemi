"""
Servicios de la capa web.

Conectan los datos de demostración con el motor de rutas
(``apps.routes.services``) y preparan la información que necesitan las
plantillas: el mapa 2D (SVG) y la escena 3D (Three.js).
"""
from __future__ import annotations

from functools import lru_cache

from django.utils import timezone

from apps.routes.services import GrafoCampus, construir_grafo_campus

from .datos_demo import ZONAS, DestinoDemo, ZonaDemo

# Margen (en metros) alrededor del campus en el mapa 2D. El horizontal es
# mayor para que quepan los nombres de las zonas de los extremos.
MARGEN_MAPA_X = 24
MARGEN_MAPA_Z = 10


@lru_cache(maxsize=1)
def obtener_grafo() -> GrafoCampus:
    """Grafo del campus construido una sola vez y reutilizado (caché)."""
    return construir_grafo_campus((zona.codigo, zona.nombre, zona.x, zona.z) for zona in ZONAS)


def calcular_ruta(
    zona_origen: ZonaDemo, destino: DestinoDemo, confianza: float | None = None
) -> dict:
    """
    Calcula la ruta más corta con Dijkstra y la devuelve en un formato
    serializable (para guardarla en la sesión).
    """
    resultado = obtener_grafo().ruta_mas_corta(zona_origen.codigo, destino.zona.codigo)
    pasos = resultado.puntos_como_dicts()

    # El último paso se enriquece con la ubicación exacta del destino.
    pasos[-1]["instruccion"] = (
        f"Estás en {destino.zona.nombre}. Busca «{destino.nombre}» "
        f"({destino.piso_display.lower()}): {destino.referencia}"
    )

    return {
        "zona_origen_id": zona_origen.id,
        "zona_origen_nombre": zona_origen.nombre,
        "destino_id": destino.id,
        "destino_nombre": destino.nombre,
        "destino_zona_nombre": destino.zona.nombre,
        "distancia_metros": float(resultado.distancia_metros),
        "tiempo_estimado_min": resultado.tiempo_estimado_min,
        "nodos": [nodo.clave for nodo in resultado.nodos],
        "pasos": pasos,
        "confianza": confianza,
        "fecha": timezone.now().isoformat(),
    }


def construir_mapa_2d(ruta: dict | None) -> dict:
    """
    Prepara los elementos del mapa SVG del campus.

    Se usan directamente las coordenadas (x, z) del campus como
    coordenadas (x, y) del SVG; el ``viewBox`` se ajusta a los límites.
    """
    grafo = obtener_grafo()
    claves_en_ruta = set(ruta["nodos"]) if ruta else set()

    xs = [nodo.x for nodo in grafo.nodos]
    zs = [nodo.z for nodo in grafo.nodos]
    minimo_x, minimo_z = min(xs) - MARGEN_MAPA_X, min(zs) - MARGEN_MAPA_Z
    ancho = max(xs) - min(xs) + 2 * MARGEN_MAPA_X
    alto = max(zs) - min(zs) + 2 * MARGEN_MAPA_Z

    polilinea = ""
    if ruta:
        polilinea = " ".join(f"{paso['x']},{paso['z']}" for paso in ruta["pasos"])

    return {
        "view_box": f"{minimo_x} {minimo_z} {ancho} {alto}",
        "aristas": [
            {"x1": a.x, "y1": a.z, "x2": b.x, "y2": b.z} for a, b in grafo.aristas()
        ],
        "nodos": [
            {
                "x": nodo.x,
                "y": nodo.z,
                "etiqueta_y": nodo.z + 7,  # El texto va debajo del punto.
                "nombre": nodo.nombre,
                "es_zona": nodo.es_zona,
                "en_ruta": nodo.clave in claves_en_ruta,
            }
            for nodo in grafo.nodos
        ],
        "polilinea": polilinea,
    }


def construir_escena_3d(ruta: dict | None) -> dict:
    """
    Describe la escena que dibuja ``frontend/assets/js/simulation.js``.

    Se entrega a la plantilla con el filtro ``json_script``, de modo que
    JavaScript solo dibuja: todos los datos los decide Python.
    """
    origen_id = ruta["zona_origen_id"] if ruta else None
    destino_zona_nombre = ruta["destino_zona_nombre"] if ruta else None

    return {
        "zonas": [
            {
                "codigo": zona.codigo,
                "nombre": zona.nombre,
                "x": zona.x,
                "z": zona.z,
                "altura": zona.altura,
                "es_origen": zona.id == origen_id,
                "es_destino": zona.nombre == destino_zona_nombre,
            }
            for zona in ZONAS
        ],
        "pasillos": [
            {"x1": a.x, "z1": a.z, "x2": b.x, "z2": b.z} for a, b in obtener_grafo().aristas()
        ],
        "ruta": [
            {"x": paso["x"], "z": paso["z"], "instruccion": paso["instruccion"]}
            for paso in ruta["pasos"]
        ]
        if ruta
        else [],
    }
