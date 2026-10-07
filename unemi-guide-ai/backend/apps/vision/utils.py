"""
Funciones auxiliares para el procesamiento de imágenes.
"""
import base64
from io import BytesIO

from django.conf import settings
from django.core.exceptions import ValidationError
from PIL import Image, ImageOps, UnidentifiedImageError

# Formatos de imagen aceptados (nombres que reporta Pillow).
FORMATOS_PERMITIDOS = {"JPEG", "PNG", "WEBP"}

# Tamaño de entrada estándar de YOLOv8 (píxeles).
TAMANO_ENTRADA_YOLO = (640, 640)

# Tamaño máximo de la miniatura que se muestra al usuario.
TAMANO_MINIATURA = (480, 480)

BYTES_POR_MB = 1024 * 1024


def validar_imagen(imagen):
    """
    Verifica que la imagen tenga un formato y tamaño aceptables.

    Args:
        imagen: Archivo subido (UploadedFile).

    Raises:
        ValidationError: si el archivo es muy grande, está dañado o no es
            JPG, PNG o WEBP.
    """
    tamano_maximo = settings.VISION_MAX_IMAGE_SIZE_MB * BYTES_POR_MB
    if imagen.size > tamano_maximo:
        raise ValidationError(
            f"La imagen supera el máximo de {settings.VISION_MAX_IMAGE_SIZE_MB} MB."
        )

    try:
        with Image.open(imagen) as archivo:
            formato = archivo.format
            archivo.verify()  # Detecta archivos corruptos.
    except (UnidentifiedImageError, OSError) as error:
        raise ValidationError("El archivo no es una imagen válida.") from error
    finally:
        # Se regresa el puntero al inicio para poder leer la imagen otra vez.
        imagen.seek(0)

    if formato not in FORMATOS_PERMITIDOS:
        raise ValidationError("Formato no soportado. Usa JPG, PNG o WEBP.")


def preparar_imagen(imagen):
    """
    Convierte la imagen al formato que espera YOLOv8.

    Args:
        imagen: Archivo subido (UploadedFile).

    Returns:
        PIL.Image.Image: Imagen RGB, con la orientación corregida y
        redimensionada a 640x640.
    """
    with Image.open(imagen) as archivo:
        # Las fotos de celular traen la rotación en los metadatos EXIF.
        imagen_orientada = ImageOps.exif_transpose(archivo)
        imagen_preparada = imagen_orientada.convert("RGB").resize(TAMANO_ENTRADA_YOLO)

    imagen.seek(0)
    return imagen_preparada


def generar_miniatura_base64(imagen):
    """
    Crea una miniatura JPEG en formato *data URI* para mostrarla en la web
    sin guardar el archivo en disco.

    Args:
        imagen: Archivo subido (UploadedFile).

    Returns:
        str: Cadena ``data:image/jpeg;base64,...`` lista para usar en <img src>.
    """
    with Image.open(imagen) as archivo:
        miniatura = ImageOps.exif_transpose(archivo).convert("RGB")
        miniatura.thumbnail(TAMANO_MINIATURA)

        buffer = BytesIO()
        miniatura.save(buffer, format="JPEG", quality=75, optimize=True)

    imagen.seek(0)
    contenido = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{contenido}"
