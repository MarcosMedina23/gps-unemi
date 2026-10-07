"""
Pruebas de la interfaz web (flujo completo del estudiante).

Ejecutar con:  python manage.py test apps.web
"""
import io
import json
import re

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from .datos_demo import CONTRASENA_DEMO


def crear_foto_jpeg():
    """Genera en memoria una foto JPEG válida para las pruebas."""
    buffer = io.BytesIO()
    Image.new("RGB", (800, 600), (13, 71, 161)).save(buffer, "JPEG")
    return SimpleUploadedFile("foto.jpg", buffer.getvalue(), content_type="image/jpeg")


class AccesoTests(TestCase):
    def test_paginas_publicas(self):
        self.assertEqual(self.client.get(reverse("web:inicio")).status_code, 200)
        self.assertEqual(self.client.get(reverse("web:acceso")).status_code, 200)

    def test_pagina_privada_redirige_al_login(self):
        respuesta = self.client.get(reverse("web:panel"))
        self.assertRedirects(respuesta, f"{reverse('web:acceso')}?next=%2Fpanel%2F")

    def test_rechaza_correo_no_institucional(self):
        respuesta = self.client.post(
            reverse("web:acceso"), {"accion": "login", "email": "a@gmail.com", "password": "x"}
        )
        self.assertContains(respuesta, "correo institucional")

    def test_rechaza_contrasena_incorrecta(self):
        respuesta = self.client.post(
            reverse("web:acceso"),
            {"accion": "login", "email": "mperez@unemi.edu.ec", "password": "mala"},
        )
        self.assertContains(respuesta, "incorrectos")

    def test_no_redirige_a_sitios_externos(self):
        respuesta = self.client.post(
            reverse("web:acceso"),
            {
                "accion": "login",
                "email": "mperez@unemi.edu.ec",
                "password": CONTRASENA_DEMO,
                "next": "https://sitio-malicioso.com",
            },
        )
        self.assertRedirects(respuesta, reverse("web:panel"))

    def test_registro_con_contrasenas_distintas(self):
        respuesta = self.client.post(
            reverse("web:acceso"),
            {
                "accion": "registro",
                "first_name": "Ana",
                "last_name": "Ruiz",
                "email": "aruiz@unemi.edu.ec",
                "carrera": "Software",
                "password": "Clave-Segura-2026",
                "password_confirmacion": "Otra-Clave-2026",
            },
        )
        self.assertContains(respuesta, "no coinciden")

    def test_cuenta_creada_se_guarda_y_permite_volver_a_ingresar(self):
        datos = {
            "accion": "registro",
            "first_name": "Ana",
            "last_name": "Ruiz",
            "email": "ARuiz@unemi.edu.ec",
            "carrera": "Enfermería",
            "password": "Clave-Segura-2026",
            "password_confirmacion": "Clave-Segura-2026",
        }
        respuesta = self.client.post(reverse("web:acceso"), datos)
        self.assertRedirects(respuesta, reverse("web:panel"))

        # El panel ya muestra la carrera en el ranking.
        self.assertContains(self.client.get(reverse("web:panel")), "Enfermería")

        # Cierra sesión y vuelve a ingresar con la cuenta nueva.
        self.client.post(reverse("web:salir"))
        respuesta = self.client.post(
            reverse("web:acceso"),
            {"accion": "login", "email": "aruiz@unemi.edu.ec", "password": "Clave-Segura-2026"},
        )
        self.assertRedirects(respuesta, reverse("web:panel"))

    def test_no_permite_registrar_un_correo_existente(self):
        respuesta = self.client.post(
            reverse("web:acceso"),
            {
                "accion": "registro",
                "first_name": "Otra",
                "last_name": "Persona",
                "email": "mperez@unemi.edu.ec",
                "carrera": "Derecho",
                "password": "Clave-Segura-2026",
                "password_confirmacion": "Clave-Segura-2026",
            },
        )
        self.assertContains(respuesta, "Ya existe una cuenta")

    def test_carrera_fuera_de_la_lista_es_rechazada(self):
        respuesta = self.client.post(
            reverse("web:acceso"),
            {
                "accion": "registro",
                "first_name": "Ana",
                "last_name": "Ruiz",
                "email": "aruiz@unemi.edu.ec",
                "carrera": "Carrera inventada",
                "password": "Clave-Segura-2026",
                "password_confirmacion": "Clave-Segura-2026",
            },
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "form-field--invalid")

    def test_cerrar_sesion_solo_por_post(self):
        self.assertEqual(self.client.get(reverse("web:salir")).status_code, 405)


class FlujoEstudianteTests(TestCase):
    """Login → foto → ruta → simulación 3D → panel."""

    def setUp(self):
        self.client.post(
            reverse("web:acceso"),
            {"accion": "login", "email": "mperez@unemi.edu.ec", "password": CONTRASENA_DEMO},
        )

    def test_reconocimiento_de_zona(self):
        respuesta = self.client.post(reverse("web:camara"), {"imagen": crear_foto_jpeg()})
        self.assertRedirects(respuesta, reverse("web:camara"))

        pagina = self.client.get(reverse("web:camara"))
        self.assertContains(pagina, "Entrada Principal")
        self.assertContains(pagina, "data:image/jpeg;base64,")

    def test_rechaza_archivo_que_no_es_imagen(self):
        archivo = SimpleUploadedFile("x.jpg", b"texto", content_type="image/jpeg")
        respuesta = self.client.post(reverse("web:camara"), {"imagen": archivo})
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "alert--error")

    def test_calculo_de_ruta_y_simulacion(self):
        respuesta = self.client.post(reverse("web:ruta"), {"origen": 1, "destino": 3})
        self.assertRedirects(
            respuesta, f"{reverse('web:ruta')}#resultado", fetch_redirect_response=False
        )

        pagina = self.client.get(reverse("web:ruta")).content.decode()
        self.assertIn("gira a la derecha", pagina)
        # El SVG debe usar punto decimal aunque el idioma sea español.
        self.assertIsNone(re.search(r'c[xy]="-?\d+,\d', pagina))

        simulacion = self.client.get(reverse("web:simulacion")).content.decode()
        patron_escena = r'id="datos-escena" type="application/json">(.*?)</script>'
        escena = json.loads(re.search(patron_escena, simulacion, re.S).group(1))
        self.assertEqual(len(escena["zonas"]), 5)
        self.assertEqual(len(escena["ruta"]), 3)

        panel = self.client.get(reverse("web:panel"))
        self.assertContains(panel, "Laboratorio de Computación 1")

    def test_ruta_sin_destino_muestra_error(self):
        respuesta = self.client.post(reverse("web:ruta"), {"origen": 1})
        self.assertContains(respuesta, "Elige un destino")
