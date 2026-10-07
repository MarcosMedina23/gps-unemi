# Arquitectura de UNEMI Guide AI

## 1. Visión general

UNEMI Guide AI es una aplicación **monolítica en Django**. Las páginas y la API se sirven
desde el mismo proyecto Python. Se organiza en **capas** y **aplicaciones** con una
responsabilidad cada una.

```text
┌──────────────────────────────────────────────────────────────────────┐
│                         NAVEGADOR DEL ESTUDIANTE                     │
│   HTML (plantillas)  ·  CSS (BEM)  ·  simulation.js (solo Three.js)  │
└───────────────────────────────┬──────────────────────────────────────┘
                                │ HTTP (formularios y páginas)
┌───────────────────────────────▼──────────────────────────────────────┐
│                   CAPA DE PRESENTACIÓN  (apps.web)                   │
│   views.py · forms.py · sesion.py · context_processors.py            │
│   Plantillas en frontend/pages/  ·  Estáticos en frontend/assets/    │
├──────────────────────────────────────────────────────────────────────┤
│                   CAPA DE API REST  (DRF)                            │
│   apps.users · apps.zones · apps.routes   →  /api/v1/...             │
│   (preparada para una futura app móvil)                              │
├──────────────────────────────────────────────────────────────────────┤
│                   CAPA DE SERVICIOS  (lógica de negocio)             │
│   routes/services.py   → Grafo del campus + Dijkstra + instrucciones │
│   vision/services.py   → Reconocimiento de zona (YOLOv8, simulado)   │
│   vision/utils.py      → Validación y procesamiento de imágenes      │
│   web/servicios.py     → Ruta, mapa SVG y escena 3D para las vistas  │
├──────────────────────────────────────────────────────────────────────┤
│                   CAPA DE DATOS                                      │
│   Cuentas:     Modelo Usuario → SQLite (demo) o PostgreSQL (real)    │
│   Campus:      web/datos_demo.py (demo) o modelos Zona/Destino       │
└──────────────────────────────────────────────────────────────────────┘
```

**Regla principal:** la lógica vive en la **capa de servicios**, que es Python puro. Así, las
vistas web y la API usan **el mismo** algoritmo de Dijkstra. Se puede probar sin navegador
ni base de datos.

---

## 2. Aplicaciones del backend

| App | Responsabilidad | Archivos clave |
|---|---|---|
| `users` | Modelo `Usuario` (extiende `AbstractUser`), registro de cuentas, ranking de carreras, API de login y perfil | `models.py`, `services.py`, `admin.py` |
| `zones` | Modelos `Zona` y `Destino`, listados y reconocimiento por foto (API) | `models.py`, `views.py` |
| `routes` | Modelo `Ruta`, grafo del campus y algoritmo de ruta más corta | `mapa_campus.py`, `services.py` |
| `vision` | Procesamiento de imágenes e inferencia de YOLOv8 | `services.py`, `utils.py` |
| `web` | Interfaz de usuario con plantillas de Django | `views.py`, `forms.py`, `servicios.py` |

---

## 3. Flujo principal

```text
 Estudiante            apps.web                 Servicios                  Datos
 ──────────            ────────                 ─────────                  ─────
     │  1. Inicia sesión   │                         │                        │
     ├────────────────────►│ LoginForm.clean()       │                        │
     │                     ├─────────────────────────┼───────────────────────►│ authenticate()
     │                     │                         │                        │ (tabla usuario)
     │◄────────────────────┤ sesión iniciada         │                        │
     │                     │                         │                        │
     │  2. Envía una foto  │                         │                        │
     ├────────────────────►│ FotoZonaForm            │                        │
     │                     ├────────────────────────►│ validar_imagen()       │
     │                     │                         │ reconocer_zona()       │
     │                     │                         │ generar_miniatura()    │
     │◄────────────────────┤ «Entrada Principal 93%» │                        │
     │                     │                         │                        │
     │  3. Elige destino   │                         │                        │
     ├────────────────────►│ SolicitudRutaForm       │                        │
     │                     ├────────────────────────►│ Dijkstra               │
     │                     │                         │ generar_instrucciones()│
     │◄────────────────────┤ Mapa SVG + pasos        │                        │
     │                     │                         │                        │
     │  4. Vista 3D        │                         │                        │
     ├────────────────────►│ construir_escena_3d()   │                        │
     │◄────────────────────┤ JSON (json_script)      │                        │
     │  simulation.js dibuja la escena con Three.js  │                        │
```

Todas las vistas que reciben formularios usan el patrón **POST → Redirect → GET**. Así, al
recargar la página no se reenvía la foto ni se recalcula la ruta.

---

## 4. Algoritmo de ruta más corta

### 4.1 El campus como grafo

El campus se modela como un **grafo ponderado no dirigido**:

- **Nodos:** las 5 zonas (de la base de datos o de `datos_demo.py`) y 3 pasillos o cruces
  (`mapa_campus.py`).
- **Aristas:** caminos peatonales entre nodos (`CONEXIONES`).
- **Peso:** distancia euclidiana en metros, calculada a partir de las coordenadas.

```text
                    ZONA-04 Biblioteca (0,-50)
                           │
    ZONA-02 Admin ──── P-03 Pasillo Norte (0,-35) ──── ZONA-03 Aulas A
     (-30,-20)  ╲          │                         ╱   (25,-25)
                 ╲── P-01 Plaza Central (0,-20) ────╱        │
                           │                                 │
                    ZONA-01 Entrada (0,0) ────── P-02 Cruce Este (25,0)
                                                             │
                                                ZONA-05 Comedor (35,10)

    Eje X → este   ·   Eje Z → sur (Z negativo = norte)   ·   1 unidad = 1 metro
```

### 4.2 Dijkstra

Implementado en `GrafoCampus.ruta_mas_corta()` con una cola de prioridad (`heapq`):

```text
distancias[origen] ← 0
cola ← [(0, origen)]
mientras cola no esté vacía:
    (d, nodo) ← extraer el de menor distancia
    si nodo ya fue visitado: continuar
    marcar nodo como visitado
    si nodo = destino: terminar
    para cada vecino de nodo:
        si d + peso < distancias[vecino]:
            distancias[vecino] ← d + peso
            previo[vecino] ← nodo
            insertar (d + peso, vecino) en la cola
reconstruir el camino siguiendo «previo» desde el destino
```

**Complejidad:** O((V + E) · log V). Para un campus con cientos de nodos responde en
microsegundos.

**Ejemplo:** de la Entrada a Aulas A hay dos caminos:

| Camino | Distancia |
|---|---|
| Entrada → Plaza Central → Aulas A | 20 + 25.5 = **45.5 m** ✅ |
| Entrada → Cruce Este → Aulas A | 25 + 25 = 50 m |

### 4.3 Instrucciones en lenguaje natural

En cada nodo intermedio se calcula el **producto cruz** entre el tramo anterior (v1) y el
siguiente (v2):

```text
cruz = v1.x · v2.z − v1.z · v2.x
seno = cruz / (|v1| · |v2|)

|seno| < 0.26  (~15°)  →  «continúa recto»
seno  > 0              →  «gira a la derecha»
seno  < 0              →  «gira a la izquierda»
```

El sistema de coordenadas (X = este, Z = sur) visto desde arriba equivale al de una
pantalla. Por eso un producto cruz positivo significa un giro en sentido horario, es decir,
a la derecha.

---

## 5. Reconocimiento de zona (visión artificial)

```text
foto ──► validar_imagen() ──► preparar_imagen() ──► YOLOv8.predict() ──► etiqueta ──► Zona
         · ≤ 5 MB             · corrige rotación                         "entrada_    (etiqueta_yolo)
         · JPG/PNG/WEBP       · RGB                                       principal"
         · no corrupta        · 640 × 640
```

- **Estado actual:** `reconocer_zona()` devuelve siempre la zona *Entrada Principal* con una
  confianza aleatoria entre 85 % y 98 %. La validación y el procesamiento de imágenes sí son
  reales.
- **Para activarlo:**
  1. Entrenar YOLOv8 con fotos del campus (una clase por zona).
  2. Guardar los pesos en `backend/apps/vision/weights/unemi_zonas.pt`.
  3. Descomentar el bloque marcado en `vision/services.py`.
- Cada `Zona` guarda su `etiqueta_yolo`, que une la clase detectada por el modelo con la base
  de datos.

---

## 6. Modelo de datos

```text
┌──────────────────────┐          ┌──────────────────────┐
│       usuario        │          │         zona         │
├──────────────────────┤          ├──────────────────────┤
│ PK id                │          │ PK id                │
│    email (único)     │          │    codigo (único)    │
│    password (hash)   │          │    nombre            │
│    first_name        │          │    etiqueta_yolo     │
│    last_name         │          │    latitud/longitud  │
│    cedula            │          │    posicion_x/_z     │
│    rol               │          │    activa            │
│    carrera/semestre  │          └──────────┬───────────┘
└──────────┬───────────┘                1   │   1
           │ 0..1                           │
           │                          N     │     N
           │                 ┌──────────────┴───┐
           │                 ▼                  │
           │      ┌──────────────────────┐      │
           │      │       destino        │      │
           │      ├──────────────────────┤      │
           │      │ PK id                │      │
           │      │ FK zona_id           │      │
           │      │    nombre, tipo      │      │
           │      │    piso, referencia  │      │
           │      └──────────┬───────────┘      │
           │                1│                  │
           │ N               │ N                │ N
           ▼                 ▼                  ▼
┌──────────────────────────────────────────────────────┐
│                         ruta                         │
├──────────────────────────────────────────────────────┤
│ PK id                                                │
│ FK usuario_id      (NULL = visitante anónimo)        │
│ FK destino_id                                        │
│ FK zona_origen_id                                    │
│    distancia_metros, tiempo_estimado_min             │
│    puntos (JSONB: pasos con x, z e instrucción)      │
│    confianza_reconocimiento                          │
└──────────────────────────────────────────────────────┘
```

Los scripts equivalentes están en `database/init.sql` (con restricciones `CHECK` e índices) y
`database/seed_data.sql`. Las migraciones de Django están en `apps/*/migrations/`.

---

### 6.1 Registro de cuentas y ranking de carreras

- **Registro:** `RegistroForm` valida los datos y llama a
  `users.services.registrar_estudiante()`, que guarda la cuenta con `create_user`. La
  contraseña se cifra con PBKDF2 y nunca se guarda en texto plano.
- **Carrera:** se elige de una lista cerrada (`CARRERAS_UNEMI` en `users/models.py`). Así
  «Software» e «Ing. de Software» no aparecen como carreras distintas en las estadísticas.
  Para agregar una carrera, se añade a la lista y se ejecuta `makemigrations` y `migrate`.
- **Ranking:** `users.services.estadisticas_por_carrera()` agrupa a los estudiantes activos
  con un `GROUP BY` del ORM:

```sql
SELECT carrera, COUNT(*) AS total
FROM usuario
WHERE rol = 'ESTUDIANTE' AND is_active AND carrera <> ''
GROUP BY carrera
ORDER BY total DESC, carrera;
```

  El panel muestra las 5 carreras con más estudiantes, con su cantidad, su porcentaje y una
  barra proporcional. La carrera del usuario actual aparece resaltada. Los docentes y
  administradores no cuentan en el ranking.
- **Registro completo:** en `/admin/` (modelo `Usuario`), con filtros por carrera, rol y fecha.

---

## 7. API REST (`/api/v1/`)

| Método | Endpoint | Descripción |
|---|---|---|
| POST | `/usuarios/registro/` | Crear cuenta (solo correos `@unemi.edu.ec`) |
| POST | `/usuarios/login/` | Iniciar sesión |
| POST | `/usuarios/logout/` | Cerrar sesión |
| GET / PATCH | `/usuarios/perfil/` | Ver o editar el perfil |
| GET | `/zonas/` y `/zonas/{id}/` | Zonas (el detalle incluye sus destinos) |
| GET | `/zonas/destinos/?tipo=LABORATORIO` | Destinos con filtro por tipo |
| POST | `/zonas/reconocer/` | Enviar una foto (multipart, campo `imagen`) |
| POST | `/rutas/calcular/` | `{"zona_origen_id", "destino_id"}` → ruta con Dijkstra |
| GET | `/rutas/historial/` | Rutas del usuario autenticado |
| GET | `/rutas/{id}/` | Detalle de una ruta |

La API necesita PostgreSQL (`UNEMI_MODO_DEMO=0`). La interfaz web no la usa: llama a los
servicios de Python directamente.

---

## 8. Frontend

| Página | Vista | CSS | ¿JavaScript? |
|---|---|---|---|
| `index.html` | `InicioView` | `style.css` | No |
| `login.html` | `AccesoView` | `login.css` | No |
| `dashboard.html` | `PanelView` | `dashboard.css` | No |
| `camera.html` | `CamaraView` | `camera.css` | No: `capture="environment"` abre la cámara del celular |
| `route.html` | `RutaView` | `route.css` | No: el mapa es SVG generado por Django |
| `simulation.html` | `SimulacionView` | `simulation.css` | Sí: `simulation.js` (Three.js) |

**Soluciones en HTML y CSS, sin JavaScript:**

| Necesidad | Solución |
|---|---|
| Menú móvil | Checkbox oculto con `<label>` y selector `:checked` |
| Notificaciones | `django.contrib.messages` con animación CSS de entrada y salida |
| Tarjetas de destino seleccionables | `<input type="radio">` y `:has(:checked)` |
| Barra de confianza | `<meter>` nativo |
| Pestañas de login y registro | Enlaces `?modo=registro` que procesa Python |
| Datos de la escena 3D | Filtro `json_script`: JSON seguro, sin scripts embebidos |

---

## 9. Modo demostración y modo real

| | Modo demostración (por defecto) | Modo real |
|---|---|---|
| Activación | `UNEMI_MODO_DEMO=1` o sin variable | `UNEMI_MODO_DEMO=0` |
| Base de datos de Django | Archivo SQLite `backend/unemi_demo.sqlite3` | PostgreSQL |
| Cuentas de usuario | Guardadas en SQLite (persisten al reiniciar) | Guardadas en PostgreSQL |
| Cuentas de prueba | Las crea la migración `users/0003_cuentas_de_prueba` | Se cargan con `seed_data.sql` |
| Zonas y destinos de la interfaz | `apps/web/datos_demo.py` | `datos_demo.py` (pendiente migrar a los modelos) |
| Sesiones | Archivos temporales | Archivos temporales |
| API REST | Disponible para usuarios; las zonas están vacías | Disponible |

**Primera ejecución:** `python manage.py migrate` crea el archivo SQLite y las cuentas de
prueba. Si se borra el archivo, se pierden todas las cuentas registradas.

**Pasos para pasar al modo real:**
1. Crear la base `unemi_guide_ai` en PostgreSQL.
2. Ajustar las credenciales en `DATABASE_POSTGRESQL` (`settings.py`).
3. Ejecutar `python manage.py migrate` y cargar `database/seed_data.sql`.
4. En `apps/web/views.py`, reemplazar las funciones de `datos_demo` por consultas a
   `Zona.objects` y `Destino.objects`.

---

## 10. Pruebas

```bash
cd backend
python manage.py test
```

| Archivo | Qué prueba |
|---|---|
| `apps/routes/tests.py` | Dijkstra: caminos correctos, elección del más corto, giros, casos límite |
| `apps/users/tests.py` | Registro guardado con contraseña cifrada, correos repetidos, ranking de carreras |
| `apps/web/tests.py` | Login, registro persistente, validaciones, redirección segura, foto, ruta, SVG, escena 3D, panel |
