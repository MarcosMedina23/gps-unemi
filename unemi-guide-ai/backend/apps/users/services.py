"""
Servicios de la aplicación ``users``.

Contiene la lógica de registro de cuentas y las estadísticas de uso por
carrera. Las vistas web (y, en el futuro, la API) llaman a estas funciones
en lugar de consultar el ORM directamente.
"""
from __future__ import annotations

from dataclasses import dataclass

from django.contrib.auth import get_user_model
from django.db.models import Count

Usuario = get_user_model()


@dataclass(frozen=True)
class EstadisticaCarrera:
    """Cantidad de estudiantes registrados en una carrera."""

    carrera: str
    total: int
    porcentaje: float  # Respecto al total de estudiantes con carrera.
    proporcion_maxima: float  # 0-1 respecto a la carrera más usada (para la barra).


def correo_registrado(email: str) -> bool:
    """Indica si ya existe una cuenta con ese correo (sin distinguir mayúsculas)."""
    return Usuario.objects.filter(email__iexact=email).exists()


def registrar_estudiante(
    *, email: str, password: str, first_name: str, last_name: str, carrera: str
) -> Usuario:
    """
    Crea y GUARDA en la base de datos la cuenta de un estudiante nuevo.

    La contraseña se almacena cifrada (``create_user`` usa el hasher de
    Django, PBKDF2 por defecto). El ``username`` interno se toma de la parte
    del correo anterior a la @, que es única dentro del dominio UNEMI.
    """
    return Usuario.objects.create_user(
        username=email.split("@")[0],
        email=email,
        password=password,
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        carrera=carrera,
        rol=Usuario.Rol.ESTUDIANTE,
        semestre=1,
        es_nuevo_ingreso=True,
    )


def estadisticas_por_carrera(limite: int | None = None) -> list[EstadisticaCarrera]:
    """
    Ranking de carreras según cuántos estudiantes usan la aplicación.

    Equivale a la consulta SQL:

        SELECT carrera, COUNT(*) AS total
        FROM usuario
        WHERE rol = 'ESTUDIANTE' AND carrera <> ''
        GROUP BY carrera
        ORDER BY total DESC, carrera;

    Args:
        limite: Cantidad máxima de carreras a devolver (None = todas).
    """
    filas = (
        Usuario.objects.filter(rol=Usuario.Rol.ESTUDIANTE, is_active=True)
        .exclude(carrera="")
        .values("carrera")
        .annotate(total=Count("id"))
        .order_by("-total", "carrera")
    )
    filas = list(filas)
    if not filas:
        return []

    total_general = sum(fila["total"] for fila in filas)
    maximo = filas[0]["total"]
    ranking = [
        EstadisticaCarrera(
            carrera=fila["carrera"],
            total=fila["total"],
            porcentaje=round(fila["total"] * 100 / total_general, 1),
            proporcion_maxima=round(fila["total"] / maximo, 3),
        )
        for fila in filas
    ]
    return ranking[:limite] if limite else ranking


def total_estudiantes() -> int:
    """Número de estudiantes registrados con una carrera asignada."""
    return (
        Usuario.objects.filter(rol=Usuario.Rol.ESTUDIANTE, is_active=True)
        .exclude(carrera="")
        .count()
    )
