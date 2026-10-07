# Manual de usuario · UNEMI Guide AI

¡Te damos la bienvenida a la UNEMI! Esta guía te explica cómo usar **UNEMI Guide AI** para
encontrar cualquier lugar del campus en tres pasos: **foto → destino → ruta**.

> **Versión de demostración.** Por ahora, el reconocimiento por foto siempre detecta la
> *Entrada Principal*. El cálculo de rutas sí es real.

---

## Índice

1. [Ingresar a la aplicación](#1-ingresar-a-la-aplicación)
2. [Tu panel](#2-tu-panel)
3. [Paso 1 · Reconocer dónde estás](#3-paso-1--reconocer-dónde-estás)
4. [Paso 2 · Elegir tu destino](#4-paso-2--elegir-tu-destino)
5. [Paso 3 · Ver el recorrido en 3D](#5-paso-3--ver-el-recorrido-en-3d)
6. [Cerrar sesión](#6-cerrar-sesión)
7. [Preguntas frecuentes](#7-preguntas-frecuentes)

---

## 1. Ingresar a la aplicación

1. Abre la aplicación en tu navegador (en la demostración: `http://127.0.0.1:8000`).
2. Pulsa **Comenzar ahora** o **Ingresar**.
3. Elige una pestaña:
   - **Iniciar sesión:** escribe tu correo institucional y tu contraseña.
   - **Crear cuenta:** completa nombres, apellidos y correo, **elige tu carrera de la
     lista** y crea una contraseña. Tu cuenta queda guardada y podrás volver a ingresar
     cuando quieras.

| Regla | Detalle |
|---|---|
| Correo | Debe terminar en `@unemi.edu.ec` |
| Contraseña | Al menos 8 caracteres, que no sea solo números ni demasiado común |

**Cuentas de prueba:** abre el recuadro naranja *«Cuentas de prueba»* debajo del botón
**Ingresar**. Por ejemplo: `mperez@unemi.edu.ec` con la contraseña `Unemi2026*`.

---

## 2. Tu panel

Después de iniciar sesión verás:

| Sección | Para qué sirve |
|---|---|
| **Estadísticas** | Cuántas rutas consultaste y cuántos metros planificaste |
| **Acciones rápidas** | Accesos directos a *Reconocer zona*, *Calcular ruta* y *Vista 3D* |
| **Rutas recientes** | Tus últimas 5 rutas |
| **Tu ubicación** | La última zona reconocida por foto |
| **Carreras que más usan la app** | Las 5 carreras con más estudiantes registrados. La tuya aparece resaltada con la etiqueta *Tu carrera* |
| **Zonas del campus** | Las zonas que reconoce el sistema, con tu zona actual resaltada en verde |

---

## 3. Paso 1 · Reconocer dónde estás

1. En el menú, entra a **Reconocer zona**.
2. Toca el recuadro **«Toca para abrir la cámara o elegir una imagen»**.
   - En el **celular** se abre directamente la cámara trasera.
   - En la **computadora** puedes elegir una foto guardada.
3. Pulsa **Reconocer zona**.
4. A la derecha verás tu foto, la **zona reconocida** y la **confianza del modelo** (barra
   verde).
5. Pulsa **Elegir mi destino →**.

**Consejos para una buena foto:**
- Enfoca la fachada o un letrero del edificio.
- Evita las fotos a contraluz o muy oscuras.
- Formatos aceptados: JPG, PNG o WEBP, de máximo 5 MB.

---

## 4. Paso 2 · Elegir tu destino

1. En **¿Dónde estás?** aparece la zona reconocida. Puedes cambiarla si hace falta.
2. En **¿A dónde vas?**, filtra por tipo (*Laboratorio*, *Oficina*, *Biblioteca*,
   *Cafetería*) o deja **Todos**.
3. Toca la tarjeta del destino. Se marcará en azul con un ✓.
4. Pulsa **Calcular ruta más corta**.

Verás:

| Elemento | Descripción |
|---|---|
| **Distancia** | Metros a recorrer |
| **Tiempo a pie** | Minutos aproximados caminando |
| **Mapa** | El campus visto desde arriba, con tu ruta en naranja |
| **Indicaciones** | Pasos numerados, como *«En Plaza Central, gira a la derecha y avanza 25 m»* |
| **Último paso (verde)** | Piso y referencia exacta del destino |

---

## 5. Paso 3 · Ver el recorrido en 3D

1. Pulsa **Ver recorrido en 3D →** o entra a **Vista 3D** en el menú.
2. Usa los controles de la parte inferior:

| Botón | Acción |
|---|---|
| **▶ Reproducir / ⏸ Pausar** | Inicia o detiene la animación del recorrido |
| **↺ Reiniciar** | Vuelve al punto de partida |
| **🎥 Seguir** | La cámara sigue al marcador naranja |

3. Con el mouse o el dedo:
   - **Arrastra** para girar la vista.
   - Usa la **rueda** o **pellizca** para acercar o alejar.

**Colores de la escena:** verde = origen · naranja = destino · azul = otros edificios ·
tubo naranja = ruta.

En la parte superior verás la indicación del tramo actual. Debajo de la escena puedes abrir
**«Ver indicaciones paso a paso»**.

---

## 6. Cerrar sesión

Pulsa **Salir** en el menú superior. Se borran tu zona reconocida y tu historial de la
sesión.

---

## 7. Preguntas frecuentes

**¿Por qué siempre reconoce la «Entrada Principal»?**
Es una versión de demostración. El modelo YOLOv8 todavía se está entrenando con fotos del
campus.

**La vista 3D dice «No se pudo cargar la vista 3D».**
La vista 3D necesita internet (para cargar Three.js) y un navegador con WebGL, como Chrome,
Edge o Firefox actualizados.

**¿Puedo usarla en el celular?**
Sí. Todas las pantallas se adaptan al celular y el menú se abre con el botón ☰.

**Me sale «Ya existe una cuenta con este correo».**
Ya te registraste antes. Usa la pestaña **Iniciar sesión** con ese correo.

**Mi carrera no está en la lista.**
Elige **Otra**. El equipo puede agregar más carreras en una próxima versión.

**Me sale «Usa tu correo institucional».**
Solo se aceptan correos que terminen en `@unemi.edu.ec`.

**¿Se guardan mis fotos?**
No. La foto solo se usa para reconocer la zona. Lo único que se guarda, durante tu sesión, es
una miniatura para mostrarte el resultado.
