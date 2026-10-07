"""
Vistas de la API REST de la aplicación ``routes``.

- CalcularRutaView:   calcula la ruta más corta (Dijkstra) y la guarda.
- HistorialRutasView: lista las rutas consultadas por el usuario.
- RutaDetalleView:    devuelve una ruta guardada (para la simulación 3D).

El algoritmo vive en ``services.py`` para que las vistas solo se ocupen
de recibir la petición y devolver la respuesta.
"""
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.zones.models import Zona

from .models import Ruta
from .serializers import RutaSerializer, SolicitudRutaSerializer
from .services import RutaNoEncontradaError, construir_grafo_campus


def obtener_grafo_desde_bd():
    """Construye el grafo del campus con las zonas activas de la base de datos."""
    zonas = Zona.objects.filter(activa=True).values_list(
        "codigo", "nombre", "posicion_x", "posicion_z"
    )
    return construir_grafo_campus(zonas)


class CalcularRutaView(APIView):
    """
    POST /api/v1/rutas/calcular/

    Body JSON esperado:
        {"zona_origen_id": 1, "destino_id": 3, "confianza_reconocimiento": 0.92}
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        solicitud = SolicitudRutaSerializer(data=request.data)
        solicitud.is_valid(raise_exception=True)
        datos = solicitud.validated_data

        zona_origen = datos["zona_origen"]
        destino = datos["destino"]

        try:
            resultado = obtener_grafo_desde_bd().ruta_mas_corta(
                zona_origen.codigo, destino.zona.codigo
            )
        except (KeyError, RutaNoEncontradaError) as error:
            return Response({"detalle": str(error)}, status=status.HTTP_404_NOT_FOUND)

        ruta = Ruta.objects.create(
            usuario=request.user if request.user.is_authenticated else None,
            zona_origen=zona_origen,
            destino=destino,
            distancia_metros=resultado.distancia_metros,
            tiempo_estimado_min=resultado.tiempo_estimado_min,
            puntos=resultado.puntos_como_dicts(),
            confianza_reconocimiento=datos.get("confianza_reconocimiento"),
        )
        return Response(RutaSerializer(ruta).data, status=status.HTTP_201_CREATED)


class HistorialRutasView(generics.ListAPIView):
    """
    GET /api/v1/rutas/historial/

    Devuelve las rutas consultadas por el usuario autenticado.
    """

    serializer_class = RutaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Ruta.objects.filter(usuario=self.request.user).select_related(
            "zona_origen", "destino"
        )


class RutaDetalleView(generics.RetrieveAPIView):
    """
    GET /api/v1/rutas/{id}/

    Devuelve una ruta concreta; la usa la simulación 3D.
    """

    queryset = Ruta.objects.select_related("zona_origen", "destino")
    serializer_class = RutaSerializer
    permission_classes = [permissions.AllowAny]
