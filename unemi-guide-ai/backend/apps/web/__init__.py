"""
Aplicación ``web``.

Sirve la interfaz de usuario con plantillas de Django: toda la lógica de
las páginas (inicio de sesión, reconocimiento por foto, cálculo de ruta y
preparación de la escena 3D) se ejecuta en Python.

Las plantillas están en ``frontend/pages/`` y los archivos estáticos en
``frontend/assets/`` (ver TEMPLATES y STATICFILES_DIRS en settings.py).

MODO DEMOSTRACIÓN: esta app NO usa la base de datos. Trabaja con los datos
de ``datos_demo.py`` y guarda el estado del usuario en la sesión.
"""
