r"""
Topología del campus para el cálculo de rutas.

Define los PASILLOS (puntos de cruce que no son zonas reconocibles) y las
CONEXIONES caminables entre nodos. Las zonas se cargan aparte (desde la
base de datos o desde los datos de demostración) y se identifican por su
``codigo``.

Sistema de coordenadas (el mismo de la escena 3D):
    * Eje X positivo -> este.
    * Eje Z positivo -> sur  (por lo tanto, Z negativo -> norte).
    * 1 unidad ≈ 1 metro.

Mapa aproximado (vista superior):

                    ZONA-04 Biblioteca (0,-50)
                           |
    ZONA-02 Admin ---- P-03 Pasillo Norte (0,-35) ---- ZONA-03 Aulas A
     (-30,-20)  \          |                         /   (25,-25)
                 \-- P-01 Plaza Central (0,-20) ----/        |
                           |                                 |
                    ZONA-01 Entrada (0,0) ------ P-02 Cruce Este (25,0)
                                                             |
                                                ZONA-05 Comedor (35,10)
"""

# (clave, nombre, x, z)
PASILLOS = (
    ("P-01", "Plaza Central", 0.0, -20.0),
    ("P-02", "Cruce Este", 25.0, 0.0),
    ("P-03", "Pasillo Norte", 0.0, -35.0),
)

# Pares de nodos unidos por un camino peatonal (bidireccional).
# La distancia de cada tramo se calcula a partir de las coordenadas.
CONEXIONES = (
    ("ZONA-01", "P-01"),
    ("ZONA-01", "P-02"),
    ("P-01", "ZONA-02"),
    ("P-01", "ZONA-03"),
    ("P-01", "P-03"),
    ("P-03", "ZONA-04"),
    ("P-03", "ZONA-02"),
    ("P-03", "ZONA-03"),
    ("P-02", "ZONA-03"),
    ("P-02", "ZONA-05"),
)
