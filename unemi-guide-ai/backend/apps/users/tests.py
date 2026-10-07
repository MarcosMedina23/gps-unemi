"""
Pruebas de los servicios de usuarios (registro y estadísticas por carrera).

Ejecutar con:  python manage.py test apps.users
"""
from django.contrib.auth import get_user_model
from django.test import TestCase

from . import services

Usuario = get_user_model()


def registrar(email, carrera):
    return services.registrar_estudiante(
        email=email,
        password="Clave-Segura-2026",
        first_name="Nombre",
        last_name="Apellido",
        carrera=carrera,
    )


class RegistroEstudianteTests(TestCase):
    def test_la_cuenta_queda_guardada_con_clave_cifrada(self):
        registrar("nuevo@unemi.edu.ec", "Enfermería")

        usuario = Usuario.objects.get(email="nuevo@unemi.edu.ec")
        self.assertEqual(usuario.carrera, "Enfermería")
        self.assertEqual(usuario.rol, Usuario.Rol.ESTUDIANTE)
        self.assertNotEqual(usuario.password, "Clave-Segura-2026")
        self.assertTrue(usuario.check_password("Clave-Segura-2026"))

    def test_correo_registrado_ignora_mayusculas(self):
        registrar("ana@unemi.edu.ec", "Derecho")
        self.assertTrue(services.correo_registrado("ANA@unemi.edu.ec"))
        self.assertFalse(services.correo_registrado("otra@unemi.edu.ec"))


class EstadisticasCarreraTests(TestCase):
    """
    La migración 0003 ya crea a María (estudiante de Ingeniería de Software).
    José (docente) y el administrador NO cuentan en el ranking.
    """

    def test_ranking_ordenado_por_cantidad(self):
        registrar("a@unemi.edu.ec", "Enfermería")
        registrar("b@unemi.edu.ec", "Enfermería")
        registrar("c@unemi.edu.ec", "Enfermería")
        registrar("d@unemi.edu.ec", "Derecho")

        ranking = services.estadisticas_por_carrera()

        self.assertEqual(
            [(item.carrera, item.total) for item in ranking],
            [("Enfermería", 3), ("Derecho", 1), ("Ingeniería de Software", 1)],
        )
        self.assertEqual(ranking[0].porcentaje, 60.0)
        self.assertEqual(ranking[0].proporcion_maxima, 1.0)
        self.assertEqual(services.total_estudiantes(), 5)

    def test_solo_cuenta_estudiantes_activos(self):
        inactivo = registrar("x@unemi.edu.ec", "Economía")
        inactivo.is_active = False
        inactivo.save()

        carreras = [item.carrera for item in services.estadisticas_por_carrera()]
        self.assertNotIn("Economía", carreras)

    def test_limite_de_resultados(self):
        for indice, carrera in enumerate(("Derecho", "Turismo", "Economía")):
            registrar(f"e{indice}@unemi.edu.ec", carrera)
        self.assertEqual(len(services.estadisticas_por_carrera(limite=2)), 2)
