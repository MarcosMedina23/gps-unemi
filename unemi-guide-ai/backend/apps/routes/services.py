"""
Servicio de cálculo de rutas de UNEMI Guide AI.

Modela el campus como un grafo ponderado no dirigido:

    * Nodo   -> zona del campus o pasillo/cruce.
    * Arista -> camino peatonal entre dos nodos.
    * Peso   -> distancia en metros (euclidiana entre coordenadas).

La ruta más corta se obtiene con el algoritmo de Dijkstra usando una cola
de prioridad (``heapq``), con complejidad O((V + E) log V).

Este módulo es Python puro: no depende de Django ni de la base de datos,
por lo que puede probarse de forma aislada.
"""
from __future__ import annotations

import heapq
import math
from collections.abc import Iterable, Iterator
from dataclasses import asdict, dataclass

from .mapa_campus import CONEXIONES, PASILLOS

# Velocidad promedio de una persona caminando (metros por minuto).
VELOCIDAD_CAMINATA_M_MIN = 80

# Por debajo de este seno del ángulo (~15°) un cambio de dirección se
# considera "seguir recto" y no un giro.
UMBRAL_GIRO = 0.26


class RutaNoEncontradaError(Exception):
    """Se lanza cuando no existe camino entre el origen y el destino."""


@dataclass(frozen=True)
class Nodo:
    """Punto del grafo del campus."""

    clave: str
    nombre: str
    x: float
    z: float
    es_zona: bool = True

    def distancia_a(self, otro: Nodo) -> float:
        """Distancia euclidiana (en metros) hasta otro nodo."""
        return math.hypot(otro.x - self.x, otro.z - self.z)


@dataclass(frozen=True)
class PasoRuta:
    """Indicación individual que se muestra al estudiante."""

    orden: int
    x: float
    z: float
    instruccion: str


@dataclass(frozen=True)
class ResultadoRuta:
    """Ruta más corta calculada entre dos nodos."""

    nodos: tuple[Nodo, ...]
    pasos: tuple[PasoRuta, ...]
    distancia_metros: float

    @property
    def tiempo_estimado_min(self) -> int:
        """Minutos aproximados caminando (mínimo 1)."""
        return max(1, math.ceil(self.distancia_metros / VELOCIDAD_CAMINATA_M_MIN))

    def puntos_como_dicts(self) -> list[dict]:
        """Pasos en formato JSON (el mismo que guarda el modelo Ruta)."""
        return [asdict(paso) for paso in self.pasos]


class GrafoCampus:
    """Grafo ponderado no dirigido que representa los caminos del campus."""

    def __init__(self) -> None:
        self._nodos: dict[str, Nodo] = {}
        self._adyacencia: dict[str, dict[str, float]] = {}

    # ------------------------------------------------------------------
    # Construcción
    # ------------------------------------------------------------------
    def agregar_nodo(self, nodo: Nodo) -> None:
        """Registra un nodo (si ya existía, se reemplaza)."""
        self._nodos[nodo.clave] = nodo
        self._adyacencia.setdefault(nodo.clave, {})

    def conectar(self, clave_a: str, clave_b: str) -> None:
        """Crea un camino bidireccional; el peso es la distancia real."""
        nodo_a, nodo_b = self.obtener_nodo(clave_a), self.obtener_nodo(clave_b)
        distancia = nodo_a.distancia_a(nodo_b)
        self._adyacencia[clave_a][clave_b] = distancia
        self._adyacencia[clave_b][clave_a] = distancia

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------
    def obtener_nodo(self, clave: str) -> Nodo:
        """Devuelve el nodo con esa clave o lanza KeyError con un mensaje claro."""
        try:
            return self._nodos[clave]
        except KeyError:
            raise KeyError(f"El nodo '{clave}' no existe en el grafo del campus.") from None

    @property
    def nodos(self) -> tuple[Nodo, ...]:
        return tuple(self._nodos.values())

    def aristas(self) -> Iterator[tuple[Nodo, Nodo]]:
        """Recorre cada camino una sola vez (sin duplicar A-B y B-A)."""
        vistas: set[frozenset[str]] = set()
        for clave_a, vecinos in self._adyacencia.items():
            for clave_b in vecinos:
                par = frozenset((clave_a, clave_b))
                if par not in vistas:
                    vistas.add(par)
                    yield self._nodos[clave_a], self._nodos[clave_b]

    # ------------------------------------------------------------------
    # Algoritmo de Dijkstra
    # ------------------------------------------------------------------
    def ruta_mas_corta(self, clave_origen: str, clave_destino: str) -> ResultadoRuta:
        """
        Calcula la ruta más corta entre dos nodos con Dijkstra.

        Raises:
            KeyError: si alguno de los nodos no existe.
            RutaNoEncontradaError: si no hay camino posible.
        """
        self.obtener_nodo(clave_origen)
        self.obtener_nodo(clave_destino)

        distancias: dict[str, float] = {clave_origen: 0.0}
        previo: dict[str, str] = {}
        visitados: set[str] = set()
        cola: list[tuple[float, str]] = [(0.0, clave_origen)]

        while cola:
            distancia_actual, clave_actual = heapq.heappop(cola)
            if clave_actual in visitados:
                continue
            visitados.add(clave_actual)

            if clave_actual == clave_destino:
                break

            for vecino, peso in self._adyacencia[clave_actual].items():
                nueva_distancia = distancia_actual + peso
                if nueva_distancia < distancias.get(vecino, math.inf):
                    distancias[vecino] = nueva_distancia
                    previo[vecino] = clave_actual
                    heapq.heappush(cola, (nueva_distancia, vecino))

        if clave_destino not in distancias:
            raise RutaNoEncontradaError(
                f"No existe un camino entre '{clave_origen}' y '{clave_destino}'."
            )

        camino = self._reconstruir_camino(previo, clave_origen, clave_destino)
        return ResultadoRuta(
            nodos=camino,
            pasos=generar_instrucciones(camino),
            distancia_metros=round(distancias[clave_destino], 2),
        )

    def _reconstruir_camino(
        self, previo: dict[str, str], origen: str, destino: str
    ) -> tuple[Nodo, ...]:
        """Recorre el diccionario ``previo`` desde el destino hasta el origen."""
        claves = [destino]
        while claves[-1] != origen:
            claves.append(previo[claves[-1]])
        return tuple(self._nodos[clave] for clave in reversed(claves))


# ----------------------------------------------------------------------
# Generación de instrucciones en lenguaje natural
# ----------------------------------------------------------------------
def _direccion_cardinal(desde: Nodo, hacia: Nodo) -> str:
    """Punto cardinal dominante del tramo (recuerda: Z negativo = norte)."""
    dx, dz = hacia.x - desde.x, hacia.z - desde.z
    if abs(dx) >= abs(dz):
        return "este" if dx > 0 else "oeste"
    return "sur" if dz > 0 else "norte"


def _tipo_de_giro(anterior: Nodo, actual: Nodo, siguiente: Nodo) -> str:
    """
    Determina si en ``actual`` se gira a la derecha, a la izquierda o se
    sigue recto, usando el producto cruz de los dos tramos.

    Con X hacia el este y Z hacia el sur (como una pantalla vista desde
    arriba), un producto cruz positivo indica un giro horario: derecha.
    """
    v1 = (actual.x - anterior.x, actual.z - anterior.z)
    v2 = (siguiente.x - actual.x, siguiente.z - actual.z)
    producto_cruz = v1[0] * v2[1] - v1[1] * v2[0]
    seno = producto_cruz / (math.hypot(*v1) * math.hypot(*v2))

    if abs(seno) < UMBRAL_GIRO:
        return "recto"
    return "derecha" if seno > 0 else "izquierda"


def generar_instrucciones(camino: tuple[Nodo, ...]) -> tuple[PasoRuta, ...]:
    """Convierte la secuencia de nodos en pasos legibles para el usuario."""
    origen, destino = camino[0], camino[-1]

    if len(camino) == 1:
        return (PasoRuta(1, origen.x, origen.z, f"Ya te encuentras en {origen.nombre}."),)

    primer_tramo = origen.distancia_a(camino[1])
    pasos = [
        PasoRuta(
            1,
            origen.x,
            origen.z,
            f"Desde {origen.nombre}, camina {primer_tramo:.0f} m hacia el "
            f"{_direccion_cardinal(origen, camino[1])}.",
        )
    ]

    for indice in range(1, len(camino) - 1):
        anterior, actual, siguiente = camino[indice - 1 : indice + 2]
        tramo = actual.distancia_a(siguiente)
        giro = _tipo_de_giro(anterior, actual, siguiente)

        if giro == "recto":
            texto = f"Al pasar por {actual.nombre}, continúa recto {tramo:.0f} m."
        else:
            texto = f"En {actual.nombre}, gira a la {giro} y avanza {tramo:.0f} m."
        pasos.append(PasoRuta(indice + 1, actual.x, actual.z, texto))

    pasos.append(
        PasoRuta(len(camino), destino.x, destino.z, f"Has llegado a {destino.nombre}.")
    )
    return tuple(pasos)


# ----------------------------------------------------------------------
# Fábrica del grafo del campus
# ----------------------------------------------------------------------
def construir_grafo_campus(zonas: Iterable[tuple[str, str, float, float]]) -> GrafoCampus:
    """
    Arma el grafo completo del campus.

    Args:
        zonas: Iterable de tuplas ``(codigo, nombre, x, z)``. Puede venir de
            la base de datos (modelo Zona) o de los datos de demostración.
    """
    grafo = GrafoCampus()
    for codigo, nombre, x, z in zonas:
        grafo.agregar_nodo(Nodo(codigo, nombre, float(x), float(z), es_zona=True))
    for clave, nombre, x, z in PASILLOS:
        grafo.agregar_nodo(Nodo(clave, nombre, x, z, es_zona=False))
    for clave_a, clave_b in CONEXIONES:
        grafo.conectar(clave_a, clave_b)
    return grafo
