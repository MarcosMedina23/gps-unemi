"""
Vistas de la aplicación ``users``.

Endpoints de registro, inicio/cierre de sesión y perfil del usuario.
La lógica es básica y está preparada para conectarse más adelante con
el frontend (frontend/assets/js/api.js).
"""
from django.contrib.auth import authenticate, get_user_model, login, logout
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginSerializer, RegistroUsuarioSerializer, UsuarioSerializer

Usuario = get_user_model()


class RegistroUsuarioView(generics.CreateAPIView):
    """
    POST /api/v1/usuarios/registro/

    Crea una cuenta nueva. Es pública: no requiere autenticación.
    """

    queryset = Usuario.objects.all()
    serializer_class = RegistroUsuarioSerializer
    permission_classes = [permissions.AllowAny]


class LoginView(APIView):
    """
    POST /api/v1/usuarios/login/

    Valida las credenciales y abre una sesión para el usuario.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        usuario = authenticate(
            request,
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )
        if usuario is None:
            return Response(
                {"detalle": "Correo o contraseña incorrectos."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        login(request, usuario)
        return Response(UsuarioSerializer(usuario).data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    POST /api/v1/usuarios/logout/

    Cierra la sesión activa del usuario.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PerfilUsuarioView(generics.RetrieveUpdateAPIView):
    """
    GET   /api/v1/usuarios/perfil/  -> Datos del usuario autenticado.
    PATCH /api/v1/usuarios/perfil/  -> Actualiza carrera, semestre, etc.
    """

    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # El perfil siempre corresponde al usuario que hace la petición.
        return self.request.user
