"""
Serializadores de la aplicación ``routes``.
"""
from rest_framework import serializers

from apps.zones.models import Destino, Zona

from .models import Ruta


class RutaSerializer(serializers.ModelSerializer):
    """Ruta completa con nombres legibles de origen y destino."""

    zona_origen_nombre = serializers.CharField(source="zona_origen.nombre", read_only=True)
    destino_nombre = serializers.CharField(source="destino.nombre", read_only=True)

    class Meta:
        model = Ruta
        fields = [
            "id",
            "zona_origen",
            "zona_origen_nombre",
            "destino",
            "destino_nombre",
            "distancia_metros",
            "tiempo_estimado_min",
            "puntos",
            "confianza_reconocimiento",
            "fecha_creacion",
        ]
        read_only_fields = fields


class SolicitudRutaSerializer(serializers.Serializer):
    """Datos que envía el frontend para pedir el cálculo de una ruta."""

    zona_origen_id = serializers.PrimaryKeyRelatedField(
        queryset=Zona.objects.filter(activa=True),
        source="zona_origen",
    )
    destino_id = serializers.PrimaryKeyRelatedField(
        queryset=Destino.objects.filter(activo=True),
        source="destino",
    )
    confianza_reconocimiento = serializers.FloatField(
        required=False,
        min_value=0.0,
        max_value=1.0,
    )
