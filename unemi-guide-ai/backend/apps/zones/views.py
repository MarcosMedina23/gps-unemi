"""
Vistas de la aplicación ``zones``.

- ZonaViewSet:        listado y detalle de zonas (solo lectura).
- DestinoViewSet:     listado y detalle de destinos (solo lectura).
- ReconocerZonaView:  recibe una foto y devuelve la zona detectada.
"""
from rest_framework import permissions, status, viewsets
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.vision.services import reconocer_zona

from .models import Destino, Zona
from .serializers import (
    DestinoSerializer,
    ReconocimientoZonaSerializer,
    ZonaDetalleSerializer,
    ZonaSerializer,
)


class ZonaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/v1/zonas/          -> Lista de zonas activas.
    GET /api/v1/zonas/{id}/     -> Detalle de una zona con sus destinos.
    """

    queryset = Zona.objects.filter(activa=True)
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        # En el detalle se incluyen los destinos; en el listado no.
        if self.action == "retrieve":
            return ZonaDetalleSerializer
        return ZonaSerializer


class DestinoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/v1/zonas/destinos/            -> Lista de destinos.
    GET /api/v1/zonas/destinos/?tipo=AULA  -> Filtra por tipo.
    GET /api/v1/zonas/destinos/{id}/       -> Detalle de un destino.
    """

    serializer_class = DestinoSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Destino.objects.filter(activo=True).select_related("zona")
        tipo = self.request.query_params.get("tipo")
        if tipo:
            queryset = queryset.filter(tipo=tipo.upper())
        return queryset


class ReconocerZonaView(APIView):
    """
    POST /api/v1/zonas/reconocer/

    Recibe una imagen (multipart/form-data, campo ``imagen``) y devuelve
    la zona del campus que el modelo YOLOv8 reconoce en ella.

    NOTA: Por ahora el servicio de visión devuelve un resultado simulado.
    """

    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = ReconocimientoZonaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        resultado = reconocer_zona(serializer.validated_data["imagen"])

        if not resultado["reconocida"]:
            return Response(
                {"detalle": "No se pudo reconocer la zona. Intenta con otra foto."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        return Response(resultado, status=status.HTTP_200_OK)
