"""
Servicios de visión artificial de UNEMI Guide AI.

Flujo previsto cuando el modelo esté entrenado:

    1. validar_imagen()     -> Comprueba formato y tamaño.
    2. preparar_imagen()    -> Convierte a RGB y redimensiona a 640x640.
    3. modelo.predict()     -> YOLOv8 detecta la clase (zona) en la foto.
    4. Se busca la Zona cuya ``etiqueta_yolo`` coincide con la clase.

ESTADO ACTUAL: SIMULADO. ``reconocer_zona`` devuelve siempre una zona
fija para poder presentar el flujo completo sin el modelo entrenado.
"""
import logging
import random

from .utils import preparar_imagen, validar_imagen

logger = logging.getLogger(__name__)

# Resultado fijo que se devuelve mientras no exista el modelo real.
ZONA_SIMULADA = {
    "id": 1,
    "codigo": "ZONA-01",
    "nombre": "Entrada Principal",
    "etiqueta_yolo": "entrada_principal",
}


def cargar_modelo():
    """
    Carga el modelo YOLOv8 entrenado con fotos del campus.

    Se deja la implementación de referencia comentada para no requerir
    el archivo de pesos (.pt) en esta fase.

    Returns:
        None: mientras el modelo no exista.
    """
    # from django.conf import settings
    # from ultralytics import YOLO
    # return YOLO(settings.VISION_MODEL_PATH)
    logger.info("Modelo YOLOv8 no cargado: modo simulación activo.")
    return None


def reconocer_zona(imagen):
    """
    Reconoce la zona del campus que aparece en la imagen.

    Args:
        imagen: Archivo de imagen recibido en la petición (UploadedFile).

    Returns:
        dict: Resultado del reconocimiento con el formato:
            {
                "reconocida": bool,
                "zona": {"id", "codigo", "nombre", "etiqueta_yolo"},
                "confianza": float (0-1),
                "modo": "simulado" | "yolov8",
            }
    """
    validar_imagen(imagen)
    preparar_imagen(imagen)

    # --- Implementación real (pendiente) -------------------------------
    # modelo = cargar_modelo()
    # resultados = modelo.predict(imagen_preparada, conf=settings.VISION_CONFIDENCE_THRESHOLD)
    # clase_detectada = resultados[0].names[int(resultados[0].boxes.cls[0])]
    # zona = Zona.objects.get(etiqueta_yolo=clase_detectada)
    # -------------------------------------------------------------------

    # Confianza aleatoria alta para que la demo se vea realista.
    confianza_simulada = round(random.uniform(0.85, 0.98), 2)

    logger.debug("Zona simulada devuelta: %s", ZONA_SIMULADA["codigo"])
    return {
        "reconocida": True,
        "zona": ZONA_SIMULADA,
        "confianza": confianza_simulada,
        "modo": "simulado",
    }
