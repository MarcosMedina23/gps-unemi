"""
Serializadores de la aplicación ``zones``.
"""
from rest_framework import serializers

from .models import Destino, Zona


class DestinoSerializer(serializers.ModelSerializer):
    """Destino con el nombre legible de su tipo y de su zona."""

    tipo_display = serializers.CharField(source="get_tipo_display", read_only=True)
    zona_nombre = serializers.CharField(source="zona.nombre", read_only=True)

    class Meta:
        model = Destino
        fields = [
            "id",
            "nombre",
            "tipo",
            "tipo_display",
            "descripcion",
            "piso",
            "referencia",
            "latitud",
            "longitud",
            "zona",
            "zona_nombre",
        ]


class ZonaSerializer(serializers.ModelSerializer):
    """Zona básica, usada en listados."""

    total_destinos = serializers.IntegerField(source="destinos.count", read_only=True)

    class Meta:
        model = Zona
        fields = [
            "id",
            "codigo",
            "nombre",
            "descripcion",
            "etiqueta_yolo",
            "latitud",
            "longitud",
            "posicion_x",
            "posicion_z",
            "total_destinos",
        ]


class ZonaDetalleSerializer(ZonaSerializer):
    """Zona con la lista completa de sus destinos (vista de detalle)."""

    destinos = DestinoSerializer(many=True, read_only=True)

    class Meta(ZonaSerializer.Meta):
        fields = ZonaSerializer.Meta.fields + ["destinos"]


class ReconocimientoZonaSerializer(serializers.Serializer):
    """Valida la foto enviada para el reconocimiento de zona."""

    imagen = serializers.ImageField(
        help_text="Foto tomada por el estudiante (JPG o PNG)."
    )
