"""
Datos de demostración de UNEMI Guide AI.

Las zonas y destinos son un espejo exacto de ``database/seed_data.sql`` y
permiten presentar la aplicación sin PostgreSQL. Cuando se conecte, estas
búsquedas se reemplazarán por consultas a los modelos Zona y Destino.

Las CUENTAS de usuario ya NO viven aquí: se guardan en la base de datos
(modelo ``apps.users.models.Usuario``). Las cuentas de prueba las crea la
migración ``users/0003_cuentas_de_prueba.py``; aquí solo se listan para
mostrarlas en la pantalla de acceso.
"""
from __future__ import annotations

from dataclasses import dataclass

# Contraseña de las cuentas de prueba (ver users/migrations/0003_cuentas_de_prueba.py).
CONTRASENA_DEMO = "Unemi2026*"


@dataclass(frozen=True)
class ZonaDemo:
    """Zona del campus. ``x``/``z`` son su posición en la escena 3D."""

    id: int
    codigo: str
    nombre: str
    descripcion: str
    x: float
    z: float
    altura: float  # Altura del edificio en la simulación 3D (metros).
    icono: str


@dataclass(frozen=True)
class DestinoDemo:
    """Lugar concreto dentro de una zona."""

    id: int
    zona_id: int
    nombre: str
    tipo: str
    piso: int
    referencia: str

    @property
    def zona(self) -> ZonaDemo:
        return buscar_zona(self.zona_id)

    @property
    def tipo_display(self) -> str:
        return dict(TIPOS_DESTINO).get(self.tipo, self.tipo.title())

    @property
    def piso_display(self) -> str:
        return "Planta baja" if self.piso == 0 else f"Piso {self.piso}"


@dataclass(frozen=True)
class CuentaDePrueba:
    """Cuenta de prueba que se muestra en la pantalla de acceso."""

    email: str
    rol: str


# ----------------------------------------------------------------------
# Catálogos
# ----------------------------------------------------------------------
TIPOS_DESTINO = (
    ("LABORATORIO", "Laboratorio"),
    ("OFICINA", "Oficina"),
    ("BIBLIOTECA", "Biblioteca"),
    ("CAFETERIA", "Cafetería"),
)

ZONAS = (
    ZonaDemo(1, "ZONA-01", "Entrada Principal",
             "Puerta de acceso principal al campus, junto a la garita de seguridad.",
             0, 0, 4, "🚪"),
    ZonaDemo(2, "ZONA-02", "Bloque Administrativo",
             "Edificio de Rectorado, Secretaría General y Bienestar Estudiantil.",
             -30, -20, 12, "🏛️"),
    ZonaDemo(3, "ZONA-03", "Bloque de Aulas A",
             "Edificio de aulas y laboratorios de la facultad de ingeniería.",
             25, -25, 14, "🏫"),
    ZonaDemo(4, "ZONA-04", "Biblioteca General",
             "Biblioteca central con salas de estudio y área de computadoras.",
             0, -50, 9, "📚"),
    ZonaDemo(5, "ZONA-05", "Comedor Universitario",
             "Área de comedor, bares y zona de descanso al aire libre.",
             35, 10, 5, "🍽️"),
)

DESTINOS = (
    DestinoDemo(1, 1, "Garita de Información", "OFICINA", 0,
                "A la derecha de la puerta principal."),
    DestinoDemo(2, 2, "Secretaría General", "OFICINA", 1,
                "Subiendo las escaleras, primera puerta."),
    DestinoDemo(3, 3, "Laboratorio de Computación 1", "LABORATORIO", 2,
                "Segundo piso, al final del pasillo."),
    DestinoDemo(4, 4, "Sala de Lectura", "BIBLIOTECA", 0,
                "Planta baja, frente al mostrador."),
    DestinoDemo(5, 5, "Bar Central", "CAFETERIA", 0,
                "Junto a las mesas techadas."),
)

CUENTAS_DE_PRUEBA = (
    CuentaDePrueba("mperez@unemi.edu.ec", "Estudiante"),
    CuentaDePrueba("jlopez@unemi.edu.ec", "Docente"),
    CuentaDePrueba("admin.guide@unemi.edu.ec", "Administrador"),
)


# ----------------------------------------------------------------------
# Funciones de búsqueda (equivalentes a consultas del ORM)
# ----------------------------------------------------------------------
def buscar_zona(zona_id: int) -> ZonaDemo | None:
    return next((zona for zona in ZONAS if zona.id == int(zona_id)), None)


def buscar_zona_por_codigo(codigo: str) -> ZonaDemo | None:
    return next((zona for zona in ZONAS if zona.codigo == codigo), None)


def buscar_destino(destino_id: int) -> DestinoDemo | None:
    return next((destino for destino in DESTINOS if destino.id == int(destino_id)), None)



def filtrar_destinos(tipo: str | None = None) -> tuple[DestinoDemo, ...]:
    """Destinos de un tipo concreto, o todos si ``tipo`` está vacío."""
    if not tipo:
        return DESTINOS
    return tuple(destino for destino in DESTINOS if destino.tipo == tipo.upper())
