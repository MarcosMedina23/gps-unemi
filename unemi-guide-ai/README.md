# UNEMI Guide AI

> Toma una foto, descubre dónde estás y llega a tu aula por el camino más corto.

**UNEMI Guide AI** es una aplicación web para que los estudiantes de nuevo ingreso de la
**Universidad Estatal de Milagro (UNEMI)** no se pierdan en el campus. El estudiante toma una
foto, la inteligencia artificial reconoce la zona en la que se encuentra, el sistema calcula la
ruta más corta hasta su destino y la muestra paso a paso, en un mapa y en 3D.

Proyecto académico · Ingeniería de Software · 5to semestre.

---

## Características

| Módulo | Qué hace | Tecnología |
|---|---|---|
| Reconocimiento de zona | Identifica la zona del campus a partir de una foto | YOLOv8 + Pillow (Python) |
| Cálculo de ruta | Encuentra el camino más corto por los pasillos del campus | Algoritmo de Dijkstra (Python) |
| Indicaciones | Genera instrucciones como «gira a la derecha y avanza 25 m» | Python (producto cruz) |
| Mapa 2D | Dibuja el campus y la ruta resaltada | SVG generado por Django |
| Simulación 3D | Recorrido animado sobre un modelo del campus | Three.js |
| Interfaz web | Páginas, formularios, validación y sesión | Django (plantillas) |
| Cuentas de usuario | Registro guardado en base de datos, contraseñas cifradas | Django ORM + SQLite/PostgreSQL |
| Carreras más activas | Ranking de las carreras de los estudiantes registrados | Django ORM (`GROUP BY`) |
| API REST | Endpoints para una futura app móvil | Django REST Framework |
| Base de datos | Esquema y datos de prueba | PostgreSQL (scripts SQL) |

**Casi todo está escrito en Python.** El único archivo JavaScript es `simulation.js`, porque
el navegador solo puede dibujar 3D (WebGL) con JavaScript. Ese archivo no toma decisiones:
solo dibuja la escena que Python le entrega.

---

## Estado del proyecto

| Parte | Estado |
|---|---|
| Interfaz web completa (6 pantallas) | ✅ Funcional en **modo demostración** |
| Registro e inicio de sesión | ✅ Real: las cuentas quedan **guardadas** en `unemi_demo.sqlite3` |
| Ranking de carreras en el panel | ✅ Real: se calcula con las cuentas registradas |
| Algoritmo de ruta más corta (Dijkstra) | ✅ Real y probado |
| Validación de fotos y miniaturas | ✅ Real (Pillow) |
| Reconocimiento con YOLOv8 | 🟡 **Simulado**: siempre devuelve «Entrada Principal» |
| Base de datos PostgreSQL | 🟡 Scripts listos, **sin conexión** |
| API REST | 🟡 Código listo; requiere PostgreSQL para funcionar |

En **modo demostración** no hace falta instalar PostgreSQL:
- Las **cuentas de usuario** se guardan en un archivo SQLite (`backend/unemi_demo.sqlite3`),
  así que siguen existiendo al reiniciar el servidor.
- Las **zonas y destinos** vienen de `backend/apps/web/datos_demo.py`, que es idéntico a
  `database/seed_data.sql`.

---

## Inicio rápido

Requisitos: **Python 3.11 o superior**.

```bash
# 1. Entrar al backend
cd unemi-guide-ai/backend

# 2. Crear y activar un entorno virtual
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux / macOS

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Crear la base de datos y las cuentas de prueba (solo la primera vez)
python manage.py migrate

# 5. Ejecutar el servidor
python manage.py runserver
```

> `migrate` crea el archivo `unemi_demo.sqlite3`, donde quedan guardadas las cuentas.
> Para **borrar todas las cuentas creadas** y empezar de cero, elimina ese archivo y
> vuelve a ejecutar `python manage.py migrate`.

Abre **http://127.0.0.1:8000** en el navegador.

**Cuentas de prueba** (contraseña para todas: `Unemi2026*`):

| Correo | Rol |
|---|---|
| `mperez@unemi.edu.ec` | Estudiante |
| `jlopez@unemi.edu.ec` | Docente |
| `admin.guide@unemi.edu.ec` | Administrador |

> **Nota:** `ultralytics` (YOLOv8) es una librería pesada. Si solo vas a presentar la
> demostración, puedes instalar lo mínimo con:
> `pip install "Django>=5.0,<5.2" djangorestframework Pillow`

### Ejecutar las pruebas

```bash
python manage.py test
```

Son 28 pruebas automáticas: el algoritmo de Dijkstra, el registro de cuentas, el ranking de
carreras y el flujo completo del estudiante.

### Ver el registro completo de cuentas

Entra a **http://127.0.0.1:8000/admin/** con `admin.guide@unemi.edu.ec` / `Unemi2026*`.
En **Usuarios** puedes filtrar las cuentas por carrera, rol o fecha de registro.

---

## Estructura del proyecto

```text
unemi-guide-ai/
│
├── backend/                         ← Todo el código Python (Django)
│   ├── apps/
│   │   ├── users/                   Usuarios
│   │   │   ├── models.py            Modelo Usuario y lista de carreras UNEMI
│   │   │   ├── services.py          Registro de cuentas y ranking de carreras
│   │   │   ├── admin.py             Registro de cuentas en /admin/
│   │   │   └── migrations/          Incluye la creación de las cuentas de prueba
│   │   ├── zones/                   Zonas y destinos del campus + API de reconocimiento
│   │   ├── routes/                  Rutas
│   │   │   ├── mapa_campus.py       Pasillos y conexiones del campus (el grafo)
│   │   │   ├── services.py          Algoritmo de Dijkstra e instrucciones
│   │   │   └── tests.py             Pruebas del algoritmo
│   │   ├── vision/                  Visión artificial
│   │   │   ├── services.py          Reconocimiento de zona (simulado)
│   │   │   └── utils.py             Validación, preparación y miniatura de imágenes
│   │   └── web/                     Interfaz web (sirve las páginas)
│   │       ├── views.py             Una vista por pantalla
│   │       ├── forms.py             Formularios con validación en Python
│   │       ├── servicios.py         Arma la ruta, el mapa 2D y la escena 3D
│   │       ├── sesion.py            Datos del usuario guardados en la sesión
│   │       ├── datos_demo.py        Datos de demostración (= seed_data.sql)
│   │       └── tests.py             Pruebas del flujo completo
│   ├── config/                      settings.py, urls.py, wsgi.py
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/                        ← Lo que ve el usuario
│   ├── pages/                       Plantillas de Django (HTML)
│   │   ├── base.html                Estructura común de todas las páginas
│   │   ├── partials/                Navbar, footer, mensajes y campos de formulario
│   │   ├── index.html               Página de presentación
│   │   ├── login.html               Iniciar sesión / crear cuenta
│   │   ├── dashboard.html           Panel del estudiante
│   │   ├── camera.html              Reconocer zona por foto
│   │   ├── route.html               Elegir destino y ver la ruta
│   │   └── simulation.html          Recorrido en 3D
│   └── assets/
│       ├── css/                     Un archivo CSS por página + style.css global (BEM)
│       ├── js/simulation.js         Único JavaScript: dibuja la escena 3D
│       └── img/logo.svg
│
├── database/
│   ├── init.sql                     Creación de tablas
│   └── seed_data.sql                Datos de prueba
│
├── docs/
│   ├── README.md                    Índice de la documentación
│   ├── arquitectura.md              Arquitectura y diagramas
│   └── manual_usuario.md            Manual de uso
│
└── README.md                        Este archivo
```

---

## Paleta de colores

| Uso | Color |
|---|---|
| Primario (Azul UNEMI) | `#0D47A1` |
| Secundario (Naranja) | `#FF6F00` |
| Fondo | `#F5F5F5` |
| Texto | `#212121` |
| Éxito | `#2E7D32` |
| Error | `#C62828` |

---

## Buenas prácticas aplicadas

- **PEP 8** en todo el código Python (verificado con `ruff`, líneas de máximo 100 caracteres).
- **HTML semántico** (`header`, `nav`, `main`, `section`, `article`, `aside`, `figure`).
- **CSS con metodología BEM** (`.bloque__elemento--modificador`), sin estilos en línea.
- **Sin scripts embebidos** en el HTML.
- **Accesibilidad:** enlace «Saltar al contenido», etiquetas en todos los campos y
  `aria-live` en los resultados. El menú móvil funciona sin JavaScript.
- **Seguridad:** CSRF en todos los formularios, cierre de sesión solo por POST, protección
  contra redirecciones a sitios externos y renovación de la sesión al iniciar sesión.

---

## Documentación

- [Arquitectura del sistema](docs/arquitectura.md)
- [Manual de usuario](docs/manual_usuario.md)
