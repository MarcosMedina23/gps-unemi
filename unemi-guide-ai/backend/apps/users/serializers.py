"""
Serializadores de la aplicación ``users``.

Convierten instancias de Usuario a JSON (y viceversa) y validan los
datos que llegan desde el frontend.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

Usuario = get_user_model()

DOMINIO_INSTITUCIONAL = "@unemi.edu.ec"


class UsuarioSerializer(serializers.ModelSerializer):
    """Representación pública de un usuario (sin datos sensibles)."""

    nombre_completo = serializers.CharField(source="get_full_name", read_only=True)

    class Meta:
        model = Usuario
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "nombre_completo",
            "rol",
            "carrera",
            "semestre",
            "es_nuevo_ingreso",
            "date_joined",
        ]
        read_only_fields = ["id", "rol", "date_joined"]


class RegistroUsuarioSerializer(serializers.ModelSerializer):
    """Valida y crea una nueva cuenta de usuario."""

    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirmacion = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "carrera",
            "semestre",
            "password",
            "password_confirmacion",
        ]

    def validate_email(self, value):
        """Solo se aceptan correos institucionales de la UNEMI."""
        if not value.lower().endswith(DOMINIO_INSTITUCIONAL):
            raise serializers.ValidationError(
                f"Debes usar tu correo institucional ({DOMINIO_INSTITUCIONAL})."
            )
        return value.lower()

    def validate(self, attrs):
        """Comprueba que ambas contraseñas coincidan."""
        if attrs["password"] != attrs["password_confirmacion"]:
            raise serializers.ValidationError(
                {"password_confirmacion": "Las contraseñas no coinciden."}
            )
        return attrs

    def create(self, validated_data):
        """Crea el usuario guardando la contraseña cifrada."""
        validated_data.pop("password_confirmacion")
        return Usuario.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    """Datos requeridos para iniciar sesión."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
