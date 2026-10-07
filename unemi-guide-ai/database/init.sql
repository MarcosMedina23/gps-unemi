-- ============================================================
-- UNEMI Guide AI - Script de creación de la base de datos
-- Motor: PostgreSQL 14+
--
-- Este script crea el esquema equivalente a los modelos de Django
-- (backend/apps/*/models.py). Sirve como documentación y para crear
-- la base manualmente si se desea. En la práctica, Django generará
-- las tablas con "python manage.py migrate".
--
-- Uso:  psql -U unemi_admin -d unemi_guide_ai -f init.sql
-- ============================================================

-- Se eliminan las tablas en orden inverso a sus dependencias para
-- poder ejecutar el script varias veces sin errores.
DROP TABLE IF EXISTS ruta;
DROP TABLE IF EXISTS destino;
DROP TABLE IF EXISTS zona;
DROP TABLE IF EXISTS usuario;

-- ------------------------------------------------------------
-- Tabla: usuario
-- Estudiantes, docentes, visitantes y administradores.
-- ------------------------------------------------------------
CREATE TABLE usuario (
    id                  BIGSERIAL       PRIMARY KEY,
    username            VARCHAR(150)    NOT NULL UNIQUE,
    email               VARCHAR(254)    NOT NULL UNIQUE,
    password            VARCHAR(128)    NOT NULL,          -- Hash, nunca texto plano
    first_name          VARCHAR(150)    NOT NULL DEFAULT '',
    last_name           VARCHAR(150)    NOT NULL DEFAULT '',
    cedula              CHAR(10)        UNIQUE,
    rol                 VARCHAR(20)     NOT NULL DEFAULT 'ESTUDIANTE',
    carrera             VARCHAR(120)    NOT NULL DEFAULT '',
    semestre            SMALLINT,
    es_nuevo_ingreso    BOOLEAN         NOT NULL DEFAULT TRUE,
    is_active           BOOLEAN         NOT NULL DEFAULT TRUE,
    is_staff            BOOLEAN         NOT NULL DEFAULT FALSE,
    is_superuser        BOOLEAN         NOT NULL DEFAULT FALSE,
    last_login          TIMESTAMPTZ,
    date_joined         TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    fecha_actualizacion TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_usuario_rol
        CHECK (rol IN ('ESTUDIANTE', 'DOCENTE', 'VISITANTE', 'ADMINISTRADOR')),
    CONSTRAINT chk_usuario_email_unemi
        CHECK (email LIKE '%@unemi.edu.ec'),
    CONSTRAINT chk_usuario_semestre
        CHECK (semestre IS NULL OR semestre BETWEEN 1 AND 10)
);

-- ------------------------------------------------------------
-- Tabla: zona
-- Áreas del campus que reconoce el modelo YOLOv8.
-- ------------------------------------------------------------
CREATE TABLE zona (
    id                  BIGSERIAL       PRIMARY KEY,
    codigo              VARCHAR(10)     NOT NULL UNIQUE,
    nombre              VARCHAR(100)    NOT NULL,
    descripcion         TEXT            NOT NULL DEFAULT '',
    etiqueta_yolo       VARCHAR(50)     NOT NULL UNIQUE,   -- Clase del modelo
    latitud             NUMERIC(9, 6)   NOT NULL,
    longitud            NUMERIC(9, 6)   NOT NULL,
    posicion_x          DOUBLE PRECISION NOT NULL DEFAULT 0, -- Escena 3D
    posicion_z          DOUBLE PRECISION NOT NULL DEFAULT 0, -- Escena 3D
    imagen_referencia   VARCHAR(255),
    activa              BOOLEAN         NOT NULL DEFAULT TRUE,
    fecha_creacion      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
-- Tabla: destino
-- Lugares concretos dentro de cada zona.
-- ------------------------------------------------------------
CREATE TABLE destino (
    id                  BIGSERIAL       PRIMARY KEY,
    zona_id             BIGINT          NOT NULL,
    nombre              VARCHAR(120)    NOT NULL,
    tipo                VARCHAR(20)     NOT NULL DEFAULT 'AULA',
    descripcion         TEXT            NOT NULL DEFAULT '',
    piso                SMALLINT        NOT NULL DEFAULT 0,
    referencia          VARCHAR(200)    NOT NULL DEFAULT '',
    latitud             NUMERIC(9, 6)   NOT NULL,
    longitud            NUMERIC(9, 6)   NOT NULL,
    activo              BOOLEAN         NOT NULL DEFAULT TRUE,

    CONSTRAINT fk_destino_zona
        FOREIGN KEY (zona_id) REFERENCES zona (id) ON DELETE RESTRICT,
    CONSTRAINT chk_destino_tipo
        CHECK (tipo IN ('AULA', 'LABORATORIO', 'OFICINA', 'BIBLIOTECA',
                        'CAFETERIA', 'BANO', 'AUDITORIO', 'OTRO')),
    CONSTRAINT chk_destino_piso
        CHECK (piso BETWEEN -1 AND 10)
);

-- ------------------------------------------------------------
-- Tabla: ruta
-- Historial de rutas calculadas.
-- ------------------------------------------------------------
CREATE TABLE ruta (
    id                          BIGSERIAL       PRIMARY KEY,
    usuario_id                  BIGINT,                     -- NULL = visitante anónimo
    zona_origen_id              BIGINT          NOT NULL,
    destino_id                  BIGINT          NOT NULL,
    distancia_metros            NUMERIC(7, 2)   NOT NULL,
    tiempo_estimado_min         SMALLINT        NOT NULL,
    puntos                      JSONB           NOT NULL DEFAULT '[]'::JSONB,
    confianza_reconocimiento    DOUBLE PRECISION,
    fecha_creacion              TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_ruta_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuario (id) ON DELETE SET NULL,
    CONSTRAINT fk_ruta_zona_origen
        FOREIGN KEY (zona_origen_id) REFERENCES zona (id) ON DELETE RESTRICT,
    CONSTRAINT fk_ruta_destino
        FOREIGN KEY (destino_id) REFERENCES destino (id) ON DELETE RESTRICT,
    CONSTRAINT chk_ruta_distancia
        CHECK (distancia_metros >= 0),
    CONSTRAINT chk_ruta_confianza
        CHECK (confianza_reconocimiento IS NULL
               OR confianza_reconocimiento BETWEEN 0 AND 1)
);

-- ------------------------------------------------------------
-- Índices para acelerar las consultas más frecuentes
-- ------------------------------------------------------------
CREATE INDEX idx_destino_zona   ON destino (zona_id);
CREATE INDEX idx_destino_tipo   ON destino (tipo);
CREATE INDEX idx_ruta_usuario   ON ruta (usuario_id);
CREATE INDEX idx_ruta_fecha     ON ruta (fecha_creacion DESC);
