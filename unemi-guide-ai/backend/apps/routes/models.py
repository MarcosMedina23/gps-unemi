"""
Modelos de la aplicación ``routes``.
"""
from django.conf import settings
from django.db import models

from apps.zones.models import Destino, Zona


class Ruta(models.Model):
    """
    Ruta calculada desde una zona de origen hasta un destino.

    El campo ``puntos`` guarda la secuencia de coordenadas que se dibuja
    en el mapa y en la simulación 3D, con el formato:

        [
            {"orden": 1, "x": 0.0, "z": 0.0, "instruccion": "Sal de la entrada"},
            {"orden": 2, "x": 12.5, "z": -4.0, "instruccion": "Gira a la derecha"},
            ...
        ]
    """

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rutas",
        help_text="Puede ser nulo si la consulta la hace un visitante anónimo.",
    )
    zona_origen = models.ForeignKey(
        Zona,
        on_delete=models.PROTECT,
        related_name="rutas_salientes",
    )
    destino = models.ForeignKey(
        Destino,
        on_delete=models.PROTECT,
        related_name="rutas_entrantes",
    )
    distancia_metros = models.DecimalField(max_digits=7, decimal_places=2)
    tiempo_estimado_min = models.PositiveSmallIntegerField(
        help_text="Tiempo estimado caminando, en minutos.",
    )
    puntos = models.JSONField(default=list)
    confianza_reconocimiento = models.FloatField(
        null=True,
        blank=True,
        help_text="Confianza (0-1) de YOLOv8 al reconocer la zona de origen.",
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ruta"
        verbose_name = "ruta"
        verbose_name_plural = "rutas"
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return f"{self.zona_origen.nombre} → {self.destino.nombre}"
