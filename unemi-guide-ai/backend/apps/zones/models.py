"""
Modelos de la aplicación ``zones``.

- Zona:    área física reconocible del campus (lo que detecta YOLOv8).
- Destino: lugar concreto al que el estudiante quiere llegar.
"""
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Zona(models.Model):
    """
    Área del campus que el modelo de visión artificial puede reconocer.

    El campo ``etiqueta_yolo`` debe coincidir exactamente con el nombre de
    la clase usada al entrenar el modelo YOLOv8.
    """

    codigo = models.CharField(
        max_length=10,
        unique=True,
        help_text="Código corto de la zona. Ej.: ZONA-01",
    )
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    etiqueta_yolo = models.CharField(
        "etiqueta YOLO",
        max_length=50,
        unique=True,
        help_text="Nombre de la clase en el modelo YOLOv8. Ej.: entrada_principal",
    )

    # Coordenadas geográficas (WGS84) del punto central de la zona.
    latitud = models.DecimalField(max_digits=9, decimal_places=6)
    longitud = models.DecimalField(max_digits=9, decimal_places=6)

    # Posición en la escena 3D de Three.js (unidades de la escena).
    posicion_x = models.FloatField(default=0)
    posicion_z = models.FloatField(default=0)

    imagen_referencia = models.ImageField(
        upload_to="zonas/",
        null=True,
        blank=True,
    )
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "zona"
        verbose_name = "zona"
        verbose_name_plural = "zonas"
        ordering = ["codigo"]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Destino(models.Model):
    """Lugar específico dentro de una zona (aula, laboratorio, oficina...)."""

    class Tipo(models.TextChoices):
        """Categorías de destinos disponibles en el campus."""

        AULA = "AULA", "Aula"
        LABORATORIO = "LABORATORIO", "Laboratorio"
        OFICINA = "OFICINA", "Oficina administrativa"
        BIBLIOTECA = "BIBLIOTECA", "Biblioteca"
        CAFETERIA = "CAFETERIA", "Cafetería / Comedor"
        BANO = "BANO", "Baño"
        AUDITORIO = "AUDITORIO", "Auditorio"
        OTRO = "OTRO", "Otro"

    zona = models.ForeignKey(
        Zona,
        on_delete=models.PROTECT,
        related_name="destinos",
    )
    nombre = models.CharField(max_length=120)
    tipo = models.CharField(max_length=20, choices=Tipo.choices, default=Tipo.AULA)
    descripcion = models.TextField(blank=True)
    piso = models.SmallIntegerField(
        default=0,
        validators=[MinValueValidator(-1), MaxValueValidator(10)],
        help_text="0 = planta baja.",
    )
    referencia = models.CharField(
        max_length=200,
        blank=True,
        help_text="Indicación visual. Ej.: 'Junto a las escaleras centrales'.",
    )
    latitud = models.DecimalField(max_digits=9, decimal_places=6)
    longitud = models.DecimalField(max_digits=9, decimal_places=6)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "destino"
        verbose_name = "destino"
        verbose_name_plural = "destinos"
        ordering = ["zona__codigo", "nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.zona.nombre})"
