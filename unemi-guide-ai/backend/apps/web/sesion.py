"""
Envoltorio de la sesión de Django para la navegación del estudiante.

Centraliza en un solo lugar las claves que se guardan en ``request.session``
para que las vistas no manipulen diccionarios "a mano":

    usuario         -> datos del usuario que inició sesión.
    reconocimiento  -> última zona reconocida por foto.
    ruta_actual     -> última ruta calculada (la usa la simulación 3D).
    historial       -> resumen de las últimas rutas consultadas.
"""
from __future__ import annotations


class SesionNavegacion:
    """Acceso tipado y documentado a los datos de la sesión."""

    CLAVE_USUARIO = "usuario"
    CLAVE_RECONOCIMIENTO = "reconocimiento"
    CLAVE_RUTA_ACTUAL = "ruta_actual"
    CLAVE_HISTORIAL = "historial"

    MAXIMO_HISTORIAL = 5

    def __init__(self, request):
        self._sesion = request.session

    # ------------------------------------------------------------------
    # Usuario
    # ------------------------------------------------------------------
    @property
    def usuario(self) -> dict | None:
        return self._sesion.get(self.CLAVE_USUARIO)

    @property
    def esta_autenticado(self) -> bool:
        return self.usuario is not None

    def iniciar(self, datos_usuario: dict) -> None:
        """Guarda al usuario y renueva la clave de sesión (evita *session fixation*)."""
        self._sesion.cycle_key()
        self._sesion[self.CLAVE_USUARIO] = datos_usuario

    def cerrar(self) -> None:
        """Elimina todos los datos de la sesión."""
        self._sesion.flush()

    # ------------------------------------------------------------------
    # Reconocimiento de zona
    # ------------------------------------------------------------------
    @property
    def reconocimiento(self) -> dict | None:
        return self._sesion.get(self.CLAVE_RECONOCIMIENTO)

    @reconocimiento.setter
    def reconocimiento(self, datos: dict) -> None:
        self._sesion[self.CLAVE_RECONOCIMIENTO] = datos

    @property
    def zona_reconocida_id(self) -> int | None:
        datos = self.reconocimiento
        return datos["zona_id"] if datos else None

    # ------------------------------------------------------------------
    # Rutas
    # ------------------------------------------------------------------
    @property
    def ruta_actual(self) -> dict | None:
        return self._sesion.get(self.CLAVE_RUTA_ACTUAL)

    @property
    def historial(self) -> list[dict]:
        return self._sesion.get(self.CLAVE_HISTORIAL, [])

    def registrar_ruta(self, ruta: dict) -> None:
        """Guarda la ruta como actual y añade un resumen al historial."""
        self._sesion[self.CLAVE_RUTA_ACTUAL] = ruta

        resumen = {
            clave: ruta[clave]
            for clave in (
                "zona_origen_nombre",
                "destino_nombre",
                "distancia_metros",
                "tiempo_estimado_min",
                "fecha",
            )
        }
        historial = [resumen, *self.historial][: self.MAXIMO_HISTORIAL]
        self._sesion[self.CLAVE_HISTORIAL] = historial
