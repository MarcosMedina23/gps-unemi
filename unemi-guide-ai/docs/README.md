# Documentación de UNEMI Guide AI

| Documento | Para quién | Contenido |
|---|---|---|
| [arquitectura.md](arquitectura.md) | Equipo de desarrollo y docente | Capas, módulos, flujo de datos, algoritmo de rutas, modelo de datos y decisiones de diseño |
| [manual_usuario.md](manual_usuario.md) | Estudiantes (usuarios finales) | Cómo usar cada pantalla de la aplicación |
| [../README.md](../README.md) | Cualquier persona | Resumen del proyecto, instalación y estructura de carpetas |

## Glosario

| Término | Significado |
|---|---|
| **Zona** | Área del campus que la IA puede reconocer en una foto (ej.: Entrada Principal). |
| **Destino** | Lugar concreto dentro de una zona (ej.: Laboratorio de Computación 1). |
| **Pasillo** | Punto de cruce entre caminos que no es una zona (ej.: Plaza Central). |
| **Grafo** | Representación del campus como nodos (zonas y pasillos) unidos por caminos. |
| **Dijkstra** | Algoritmo que encuentra el camino más corto en un grafo con distancias. |
| **YOLOv8** | Modelo de visión artificial que detecta objetos o lugares en imágenes. |
| **Modo demostración** | Forma de ejecutar la app sin PostgreSQL, con datos de prueba en Python. |
