"""
Pruebas del motor de rutas (Dijkstra).

Ejecutar con:  python manage.py test apps.routes
"""
from django.test import SimpleTestCase

from .services import GrafoCampus, Nodo, RutaNoEncontradaError, construir_grafo_campus

ZONAS_PRUEBA = (
    ("ZONA-01", "Entrada Principal", 0, 0),
    ("ZONA-02", "Bloque Administrativo", -30, -20),
    ("ZONA-03", "Bloque de Aulas A", 25, -25),
    ("ZONA-04", "Biblioteca General", 0, -50),
    ("ZONA-05", "Comedor Universitario", 35, 10),
)


class DijkstraCampusTests(SimpleTestCase):
    """Rutas sobre el mapa real del campus (mapa_campus.py)."""

    def setUp(self):
        self.grafo = construir_grafo_campus(ZONAS_PRUEBA)

    def claves(self, resultado):
        return [nodo.clave for nodo in resultado.nodos]

    def test_ruta_recta_hacia_biblioteca(self):
        resultado = self.grafo.ruta_mas_corta("ZONA-01", "ZONA-04")
        self.assertEqual(self.claves(resultado), ["ZONA-01", "P-01", "P-03", "ZONA-04"])
        self.assertEqual(resultado.distancia_metros, 50.0)

    def test_elige_el_camino_mas_corto_entre_dos_alternativas(self):
        # Por la Plaza Central son 45.5 m; por el Cruce Este serían 50 m.
        resultado = self.grafo.ruta_mas_corta("ZONA-01", "ZONA-03")
        self.assertEqual(self.claves(resultado), ["ZONA-01", "P-01", "ZONA-03"])
        self.assertAlmostEqual(resultado.distancia_metros, 45.5, places=1)

    def test_instruccion_de_giro_a_la_derecha(self):
        resultado = self.grafo.ruta_mas_corta("ZONA-01", "ZONA-03")
        self.assertIn("gira a la derecha", resultado.pasos[1].instruccion)

    def test_origen_igual_a_destino(self):
        resultado = self.grafo.ruta_mas_corta("ZONA-04", "ZONA-04")
        self.assertEqual(resultado.distancia_metros, 0)
        self.assertEqual(len(resultado.pasos), 1)

    def test_tiempo_estimado_minimo_un_minuto(self):
        resultado = self.grafo.ruta_mas_corta("ZONA-01", "ZONA-04")
        self.assertEqual(resultado.tiempo_estimado_min, 1)

    def test_nodo_inexistente(self):
        with self.assertRaises(KeyError):
            self.grafo.ruta_mas_corta("ZONA-01", "ZONA-99")

    def test_cada_pasillo_se_cuenta_una_sola_vez(self):
        self.assertEqual(len(list(self.grafo.aristas())), 10)


class GrafoAisladoTests(SimpleTestCase):
    """Casos límite con grafos pequeños construidos a mano."""

    def test_sin_camino_lanza_error(self):
        grafo = GrafoCampus()
        grafo.agregar_nodo(Nodo("A", "A", 0, 0))
        grafo.agregar_nodo(Nodo("B", "B", 10, 0))  # B no está conectado.
        with self.assertRaises(RutaNoEncontradaError):
            grafo.ruta_mas_corta("A", "B")

    def test_prefiere_desvio_si_es_mas_corto(self):
        # A-C directo mide 100, pero A-B-C mide 20 + 20.
        grafo = GrafoCampus()
        for clave, x in (("A", 0), ("B", 20), ("C", 40)):
            grafo.agregar_nodo(Nodo(clave, clave, x, 0))
        grafo.conectar("A", "B")
        grafo.conectar("B", "C")
        grafo._adyacencia["A"]["C"] = grafo._adyacencia["C"]["A"] = 100
        resultado = grafo.ruta_mas_corta("A", "C")
        self.assertEqual([nodo.clave for nodo in resultado.nodos], ["A", "B", "C"])
        self.assertIn("continúa recto", resultado.pasos[1].instruccion)
