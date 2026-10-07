"""
Formularios de la interfaz web.

Django genera los campos HTML y realiza TODA la validación en el servidor
(Python), por lo que el frontend no necesita JavaScript para validar.
"""
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from apps.users import services as servicios_usuarios
from apps.users.models import CARRERAS_UNEMI
from apps.vision.utils import validar_imagen

from . import datos_demo

DOMINIO_INSTITUCIONAL = "@unemi.edu.ec"
CLASE_INPUT = "form-field__input"


def validar_correo_institucional(email: str) -> str:
    """Normaliza el correo y verifica que pertenezca a la UNEMI."""
    email = email.strip().lower()
    if not email.endswith(DOMINIO_INSTITUCIONAL):
        raise ValidationError(f"Usa tu correo institucional ({DOMINIO_INSTITUCIONAL}).")
    return email


class LoginForm(forms.Form):
    """Inicio de sesión con correo institucional."""

    email = forms.EmailField(
        label="Correo institucional",
        widget=forms.EmailInput(
            attrs={
                "class": CLASE_INPUT,
                "placeholder": "usuario@unemi.edu.ec",
                "autocomplete": "email",
                "autofocus": True,
            }
        ),
    )
    password = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": CLASE_INPUT,
                "placeholder": "••••••••",
                "autocomplete": "current-password",
            }
        ),
    )

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.usuario = None

    def clean_email(self):
        return validar_correo_institucional(self.cleaned_data["email"])

    def clean(self):
        """
        Verifica las credenciales contra las cuentas guardadas en la base de
        datos. ``authenticate`` compara la contraseña con su hash cifrado.
        """
        datos = super().clean()
        email, password = datos.get("email"), datos.get("password")
        if not email or not password:
            return datos

        usuario = authenticate(self.request, email=email, password=password)
        if usuario is None:
            raise ValidationError("Correo o contraseña incorrectos.")

        self.usuario = usuario
        return datos


class RegistroForm(forms.Form):
    """Registro de un estudiante nuevo."""

    first_name = forms.CharField(
        label="Nombres",
        max_length=150,
        widget=forms.TextInput(attrs={"class": CLASE_INPUT, "autocomplete": "given-name"}),
    )
    last_name = forms.CharField(
        label="Apellidos",
        max_length=150,
        widget=forms.TextInput(attrs={"class": CLASE_INPUT, "autocomplete": "family-name"}),
    )
    email = forms.EmailField(
        label="Correo institucional",
        widget=forms.EmailInput(
            attrs={
                "class": CLASE_INPUT,
                "placeholder": "usuario@unemi.edu.ec",
                "autocomplete": "email",
            }
        ),
    )
    carrera = forms.ChoiceField(
        label="Carrera",
        choices=[("", "Selecciona tu carrera")] + CARRERAS_UNEMI,
        error_messages={"required": "Selecciona tu carrera."},
        widget=forms.Select(attrs={"class": CLASE_INPUT}),
    )
    password = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={"class": CLASE_INPUT, "autocomplete": "new-password"}),
    )
    password_confirmacion = forms.CharField(
        label="Confirmar contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={"class": CLASE_INPUT, "autocomplete": "new-password"}),
    )

    def clean_email(self):
        email = validar_correo_institucional(self.cleaned_data["email"])
        if servicios_usuarios.correo_registrado(email):
            raise ValidationError("Ya existe una cuenta con este correo. Inicia sesión.")
        return email

    def clean_password(self):
        password = self.cleaned_data["password"]
        validate_password(password)  # Validadores definidos en settings.py
        return password

    def clean(self):
        datos = super().clean()
        if datos.get("password") and datos.get("password") != datos.get("password_confirmacion"):
            self.add_error("password_confirmacion", "Las contraseñas no coinciden.")
        return datos

    def crear_usuario(self):
        """Guarda la cuenta en la base de datos y la devuelve."""
        datos = self.cleaned_data
        return servicios_usuarios.registrar_estudiante(
            email=datos["email"],
            password=datos["password"],
            first_name=datos["first_name"],
            last_name=datos["last_name"],
            carrera=datos["carrera"],
        )


class FotoZonaForm(forms.Form):
    """
    Foto para reconocer la zona.

    ``capture="environment"`` hace que en un celular se abra directamente
    la cámara trasera, sin necesidad de JavaScript.
    """

    imagen = forms.ImageField(
        label="Foto del lugar",
        widget=forms.FileInput(
            attrs={
                "class": "upload__input",
                "accept": "image/*",
                "capture": "environment",
            }
        ),
    )

    def clean_imagen(self):
        imagen = self.cleaned_data["imagen"]
        validar_imagen(imagen)
        return imagen


class SolicitudRutaForm(forms.Form):
    """Origen y destino para calcular la ruta más corta."""

    origen = forms.TypedChoiceField(
        label="¿Dónde estás?",
        coerce=int,
        choices=[(zona.id, zona.nombre) for zona in datos_demo.ZONAS],
        widget=forms.Select(attrs={"class": CLASE_INPUT}),
    )
    destino = forms.TypedChoiceField(
        label="¿A dónde vas?",
        coerce=int,
        choices=[(destino.id, destino.nombre) for destino in datos_demo.DESTINOS],
        error_messages={"required": "Elige un destino de la lista."},
    )

    def clean(self):
        datos = super().clean()
        if datos.get("origen") is not None:
            datos["zona_origen"] = datos_demo.buscar_zona(datos["origen"])
        if datos.get("destino") is not None:
            datos["destino_obj"] = datos_demo.buscar_destino(datos["destino"])
        return datos
