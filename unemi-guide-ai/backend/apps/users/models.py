"""
Modelos de la aplicación ``users``.

Se extiende el usuario estándar de Django (AbstractUser) para añadir los
datos propios de la comunidad universitaria de la UNEMI.
"""
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

# Carreras de grado de la UNEMI que se ofrecen al registrarse.
# Se usa una lista cerrada (y no texto libre) para que las estadísticas no
# se dividan por diferencias de escritura ("Software" vs "Ing. Software").
# El valor guardado es el mismo nombre visible.
_NOMBRES_CARRERAS = (
    "Ingeniería de Software",
    "Tecnologías de la Información",
    "Ingeniería Industrial",
    "Ingeniería Ambiental",
    "Biotecnología",
    "Administración de Empresas",
    "Contabilidad y Auditoría",
    "Economía",
    "Turismo",
    "Derecho",
    "Comunicación",
    "Psicología",
    "Trabajo Social",
    "Enfermería",
    "Nutrición y Dietética",
    "Educación Básica",
    "Educación Inicial",
    "Pedagogía de la Actividad Física y Deporte",
    "Otra",
)
CARRERAS_UNEMI = [(nombre, nombre) for nombre in _NOMBRES_CARRERAS]


class Usuario(AbstractUser):
    """
    Usuario de UNEMI Guide AI.

    Hereda de AbstractUser los campos: username, first_name, last_name,
    email, password, is_active, date_joined, etc.
    """

    class Rol(models.TextChoices):
        """Tipos de usuario que pueden utilizar la aplicación."""

        ESTUDIANTE = "ESTUDIANTE", "Estudiante"
        DOCENTE = "DOCENTE", "Docente"
        VISITANTE = "VISITANTE", "Visitante"
        ADMINISTRADOR = "ADMINISTRADOR", "Administrador"

    # Validador para cédula ecuatoriana (10 dígitos numéricos).
    validador_cedula = RegexValidator(
        regex=r"^\d{10}$",
        message="La cédula debe contener exactamente 10 dígitos.",
    )

    email = models.EmailField(
        "correo institucional",
        unique=True,
        help_text="Correo con dominio @unemi.edu.ec",
    )
    cedula = models.CharField(
        "cédula",
        max_length=10,
        unique=True,
        null=True,
        blank=True,
        validators=[validador_cedula],
    )
    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.ESTUDIANTE,
    )
    carrera = models.CharField(
        max_length=120,
        blank=True,
        choices=CARRERAS_UNEMI,
        help_text="Carrera a la que pertenece el estudiante.",
    )
    semestre = models.PositiveSmallIntegerField(null=True, blank=True)
    es_nuevo_ingreso = models.BooleanField(
        default=True,
        help_text="Indica si el estudiante cursa su primer semestre.",
    )
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    # El inicio de sesión se realiza con el correo institucional.
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        db_table = "usuario"
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.get_full_name()} <{self.email}>"

    def datos_para_sesion(self) -> dict:
        """Datos públicos del usuario en formato serializable (para la sesión web)."""
        return {
            "id": self.pk,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "nombre_completo": self.get_full_name(),
            "rol": self.rol,
            "carrera": self.carrera,
            "semestre": self.semestre,
        }
