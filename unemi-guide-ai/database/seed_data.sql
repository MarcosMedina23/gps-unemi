-- ============================================================
-- UNEMI Guide AI - Datos de prueba
-- Ejecutar DESPUÉS de init.sql:
--     psql -U unemi_admin -d unemi_guide_ai -f seed_data.sql
--
-- NOTA: Las coordenadas son aproximadas y los datos son ficticios,
-- creados solo para pruebas y demostración.
-- ============================================================

BEGIN;

-- ------------------------------------------------------------
-- 5 zonas del campus
-- posicion_x / posicion_z: ubicación en la escena 3D (1 unidad ≈ 1 m)
-- ------------------------------------------------------------
INSERT INTO zona (codigo, nombre, descripcion, etiqueta_yolo, latitud, longitud, posicion_x, posicion_z) VALUES
('ZONA-01', 'Entrada Principal',     'Puerta de acceso principal al campus, junto a la garita de seguridad.', 'entrada_principal',    -2.149700, -79.603600,   0,   0),
('ZONA-02', 'Bloque Administrativo', 'Edificio de Rectorado, Secretaría General y Bienestar Estudiantil.',   'bloque_administrativo', -2.149300, -79.603900, -30, -20),
('ZONA-03', 'Bloque de Aulas A',     'Edificio de aulas y laboratorios de la facultad de ingeniería.',      'bloque_aulas_a',       -2.149200, -79.603300,  25, -25),
('ZONA-04', 'Biblioteca General',    'Biblioteca central con salas de estudio y área de computadoras.',     'biblioteca_general',   -2.148900, -79.603600,   0, -50),
('ZONA-05', 'Comedor Universitario', 'Área de comedor, bares y zona de descanso al aire libre.',            'comedor_universitario',-2.149800, -79.603200,  35,  10);

-- ------------------------------------------------------------
-- 5 destinos (uno por zona)
-- ------------------------------------------------------------
INSERT INTO destino (zona_id, nombre, tipo, descripcion, piso, referencia, latitud, longitud) VALUES
(1, 'Garita de Información',          'OFICINA',     'Punto de información para visitantes.',            0, 'A la derecha de la puerta principal.',      -2.149710, -79.603580),
(2, 'Secretaría General',             'OFICINA',     'Trámites de matrícula, certificados y récords.',   1, 'Subiendo las escaleras, primera puerta.',   -2.149310, -79.603920),
(3, 'Laboratorio de Computación 1',   'LABORATORIO', 'Laboratorio con 30 equipos para clases prácticas.', 2, 'Segundo piso, al final del pasillo.',       -2.149190, -79.603280),
(4, 'Sala de Lectura',                'BIBLIOTECA',  'Sala silenciosa para estudio individual.',          0, 'Planta baja, frente al mostrador.',         -2.148910, -79.603610),
(5, 'Bar Central',                    'CAFETERIA',   'Venta de almuerzos, snacks y bebidas.',             0, 'Junto a las mesas techadas.',               -2.149820, -79.603190);

-- ------------------------------------------------------------
-- 3 usuarios de prueba
-- La contraseña de los tres es "Unemi2026*". El valor guardado es un
-- hash de EJEMPLO (no válido); en la práctica, crear usuarios con
-- "python manage.py createsuperuser" o desde el endpoint de registro.
-- ------------------------------------------------------------
INSERT INTO usuario (username, email, password, first_name, last_name, cedula, rol, carrera, semestre, es_nuevo_ingreso, is_staff, is_superuser) VALUES
('admin.guide',  'admin.guide@unemi.edu.ec',  'pbkdf2_sha256$600000$ejemplo$hashficticio0000000000000000000000000000=', 'Administrador', 'UNEMI Guide', '0900000001', 'ADMINISTRADOR', '',                         NULL, FALSE, TRUE,  TRUE),
('mperez',       'mperez@unemi.edu.ec',       'pbkdf2_sha256$600000$ejemplo$hashficticio1111111111111111111111111111=', 'María',         'Pérez',       '0900000002', 'ESTUDIANTE',    'Ingeniería de Software',   1,    TRUE,  FALSE, FALSE),
('jlopez',       'jlopez@unemi.edu.ec',       'pbkdf2_sha256$600000$ejemplo$hashficticio2222222222222222222222222222=', 'José',          'López',       '0900000003', 'DOCENTE',       'Ingeniería de Software',   NULL, FALSE, FALSE, FALSE);

-- ------------------------------------------------------------
-- 1 ruta de ejemplo en el historial (Entrada -> Laboratorio)
-- ------------------------------------------------------------
INSERT INTO ruta (usuario_id, zona_origen_id, destino_id, distancia_metros, tiempo_estimado_min, puntos, confianza_reconocimiento) VALUES
(2, 1, 3, 35.36, 1,
 '[{"orden":1,"x":0,"z":0,"instruccion":"Inicia en Entrada Principal"},
   {"orden":2,"x":12.5,"z":-12.5,"instruccion":"Continúa recto por el pasillo central"},
   {"orden":3,"x":25,"z":-25,"instruccion":"Has llegado a Laboratorio de Computación 1"}]'::JSONB,
 0.93);

COMMIT;
