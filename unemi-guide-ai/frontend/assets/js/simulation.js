/**
 * ==========================================================================
 * UNEMI Guide AI - Simulación 3D del recorrido (Three.js r128)
 * --------------------------------------------------------------------------
 * Este es el ÚNICO archivo JavaScript del proyecto: el navegador solo puede
 * dibujar 3D con WebGL a través de JavaScript.
 *
 * Toda la información (zonas, pasillos, ruta e indicaciones) la calcula
 * Python en apps/web/servicios.py → construir_escena_3d() y llega aquí como
 * JSON dentro de <script id="datos-escena" type="application/json">.
 *
 * Sistema de coordenadas: X = este, Z = sur, Y = altura. 1 unidad = 1 metro.
 * ==========================================================================
 */
(function () {
    "use strict";

    /* ----------------------------------------------------------------------
     * Configuración visual
     * -------------------------------------------------------------------- */
    const COLORES = {
        cielo: 0xdbe9f7,
        cesped: 0x9cc78a,
        pasillo: 0xe8e2d6,
        edificio: 0x0d47a1,
        origen: 0x2e7d32,
        destino: 0xff6f00,
        ruta: 0xff6f00,
        marcador: 0xff6f00,
    };

    const EDIFICIO = { ancho: 14, profundidad: 10, separacion: 9 };
    const ANCHO_PASILLO = 3;
    const VELOCIDAD_MARCADOR = 10; // metros por segundo (acelerado para la demo)

    // Punto central del campus: hacia donde mira la cámara al iniciar.
    // Es un objeto simple (no THREE.Vector3) porque THREE aún puede no existir.
    const CENTRO_CAMPUS = Object.freeze({ x: 0, y: 0, z: -22 });

    /* ----------------------------------------------------------------------
     * Referencias al DOM
     * -------------------------------------------------------------------- */
    const contenedor = document.getElementById("escena-3d");
    const fallback = document.getElementById("escena-fallback");
    const textoInstruccion = document.getElementById("escena-instruccion");
    const barraProgreso = document.getElementById("escena-progreso");
    const botonReproducir = document.querySelector('[data-accion="reproducir"]');
    const botonReiniciar = document.querySelector('[data-accion="reiniciar"]');
    const botonVista = document.querySelector('[data-accion="vista"]');

    /* ----------------------------------------------------------------------
     * Estado de la simulación
     * -------------------------------------------------------------------- */
    const estado = {
        reproduciendo: false,
        seguirMarcador: false,
        recorrido: 0, // metros avanzados
        ultimoTiempo: null,
        indicePaso: -1,
    };

    /* ======================================================================
     * 1. Lectura de datos
     * ==================================================================== */

    /** Lee el JSON que generó Django con el filtro json_script. */
    function leerEscena() {
        const nodo = document.getElementById("datos-escena");
        return nodo ? JSON.parse(nodo.textContent) : { zonas: [], pasillos: [], ruta: [] };
    }

    /** Comprueba que Three.js se haya cargado y que exista WebGL. */
    function soporta3D() {
        if (typeof THREE === "undefined") return false;
        try {
            const lienzo = document.createElement("canvas");
            return Boolean(lienzo.getContext("webgl") || lienzo.getContext("experimental-webgl"));
        } catch (error) {
            return false;
        }
    }

    /* ======================================================================
     * 2. Construcción de la escena
     * ==================================================================== */

    function crearRenderer() {
        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.setSize(contenedor.clientWidth, contenedor.clientHeight);
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        contenedor.appendChild(renderer.domElement);
        return renderer;
    }

    function crearCamara() {
        const camara = new THREE.PerspectiveCamera(
            50,
            contenedor.clientWidth / contenedor.clientHeight,
            0.1,
            1000
        );
        camara.position.set(42, 48, 34);
        camara.lookAt(CENTRO_CAMPUS.x, CENTRO_CAMPUS.y, CENTRO_CAMPUS.z);
        return camara;
    }

    function agregarLuces(escena) {
        escena.add(new THREE.HemisphereLight(0xffffff, 0x6f8f60, 0.55));

        const sol = new THREE.DirectionalLight(0xffffff, 0.6);
        sol.position.set(40, 80, 30);
        sol.castShadow = true;
        sol.shadow.mapSize.set(2048, 2048);
        Object.assign(sol.shadow.camera, { left: -80, right: 80, top: 80, bottom: -80 });
        escena.add(sol);
    }

    function agregarSuelo(escena) {
        const suelo = new THREE.Mesh(
            new THREE.PlaneGeometry(220, 220),
            new THREE.MeshLambertMaterial({ color: COLORES.cesped })
        );
        suelo.rotation.x = -Math.PI / 2;
        suelo.position.set(CENTRO_CAMPUS.x, 0, CENTRO_CAMPUS.z);
        suelo.receiveShadow = true;
        escena.add(suelo);
    }

    /** Cada pasillo es una franja plana entre dos nodos del grafo. */
    function agregarPasillos(escena, pasillos) {
        const material = new THREE.MeshLambertMaterial({ color: COLORES.pasillo });

        pasillos.forEach(({ x1, z1, x2, z2 }) => {
            const largo = Math.hypot(x2 - x1, z2 - z1);
            const tramo = new THREE.Mesh(new THREE.PlaneGeometry(largo + ANCHO_PASILLO, ANCHO_PASILLO), material);
            tramo.rotation.x = -Math.PI / 2;
            tramo.rotation.z = -Math.atan2(z2 - z1, x2 - x1);
            tramo.position.set((x1 + x2) / 2, 0.02, (z1 + z2) / 2);
            tramo.receiveShadow = true;
            escena.add(tramo);
        });
    }

    /** Etiqueta de texto que siempre mira a la cámara (sprite). */
    function crearEtiqueta(texto) {
        const lienzo = document.createElement("canvas");
        const contexto = lienzo.getContext("2d");
        lienzo.width = 512;
        lienzo.height = 96;

        contexto.fillStyle = "rgba(255, 255, 255, 0.92)";
        contexto.beginPath();
        contexto.roundRect
            ? contexto.roundRect(4, 4, 504, 88, 40)
            : contexto.rect(4, 4, 504, 88);
        contexto.fill();

        contexto.font = "600 40px Poppins, 'Segoe UI', sans-serif";
        contexto.fillStyle = "#212121";
        contexto.textAlign = "center";
        contexto.textBaseline = "middle";
        contexto.fillText(texto, 256, 50);

        const textura = new THREE.CanvasTexture(lienzo);
        const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: textura, depthTest: false }));
        sprite.scale.set(16, 3, 1);
        sprite.renderOrder = 10;
        return sprite;
    }

    /**
     * Cada zona tiene una plazoleta circular (donde termina la ruta) y un
     * edificio ubicado detrás de ella, hacia el norte.
     */
    function agregarZonas(escena, zonas) {
        zonas.forEach((zona) => {
            let color = COLORES.edificio;
            if (zona.es_origen) color = COLORES.origen;
            if (zona.es_destino) color = COLORES.destino;

            const plaza = new THREE.Mesh(
                new THREE.CylinderGeometry(4, 4, 0.2, 32),
                new THREE.MeshLambertMaterial({ color: 0xffffff })
            );
            plaza.position.set(zona.x, 0.1, zona.z);
            plaza.receiveShadow = true;
            escena.add(plaza);

            const edificio = new THREE.Mesh(
                new THREE.BoxGeometry(EDIFICIO.ancho, zona.altura, EDIFICIO.profundidad),
                new THREE.MeshStandardMaterial({ color, roughness: 0.6, metalness: 0.05 })
            );
            edificio.position.set(zona.x, zona.altura / 2, zona.z - EDIFICIO.separacion);
            edificio.castShadow = true;
            edificio.receiveShadow = true;
            escena.add(edificio);

            const etiqueta = crearEtiqueta(zona.nombre);
            etiqueta.position.set(zona.x, zona.altura + 3.5, zona.z - EDIFICIO.separacion);
            escena.add(etiqueta);
        });
    }

    /** Tubo naranja que sigue los puntos de la ruta. */
    function agregarRuta(escena, ruta) {
        if (ruta.length < 2) return;

        const camino = new THREE.CurvePath();
        for (let i = 0; i < ruta.length - 1; i += 1) {
            camino.add(
                new THREE.LineCurve3(
                    new THREE.Vector3(ruta[i].x, 0.4, ruta[i].z),
                    new THREE.Vector3(ruta[i + 1].x, 0.4, ruta[i + 1].z)
                )
            );
        }

        const tubo = new THREE.Mesh(
            new THREE.TubeGeometry(camino, 200, 0.45, 8, false),
            new THREE.MeshStandardMaterial({
                color: COLORES.ruta,
                emissive: COLORES.ruta,
                emissiveIntensity: 0.35,
            })
        );
        escena.add(tubo);
    }

    /** Marcador que representa al estudiante (cuerpo + cabeza). */
    function crearMarcador() {
        const grupo = new THREE.Group();
        const material = new THREE.MeshStandardMaterial({ color: COLORES.marcador, roughness: 0.4 });

        const cuerpo = new THREE.Mesh(new THREE.CylinderGeometry(0.7, 0.9, 2.2, 16), material);
        cuerpo.position.y = 1.1;
        const cabeza = new THREE.Mesh(new THREE.SphereGeometry(0.7, 16, 16), material);
        cabeza.position.y = 2.9;

        [cuerpo, cabeza].forEach((parte) => {
            parte.castShadow = true;
            grupo.add(parte);
        });
        return grupo;
    }

    /* ======================================================================
     * 3. Animación del recorrido
     * ==================================================================== */

    /** Precalcula la distancia acumulada en cada punto de la ruta. */
    function calcularTramos(ruta) {
        const acumulado = [0];
        for (let i = 1; i < ruta.length; i += 1) {
            const distancia = Math.hypot(ruta[i].x - ruta[i - 1].x, ruta[i].z - ruta[i - 1].z);
            acumulado.push(acumulado[i - 1] + distancia);
        }
        return { acumulado, total: acumulado[acumulado.length - 1] };
    }

    /** Posición (x, z) y tramo actual para una distancia recorrida. */
    function posicionEnRuta(ruta, tramos, recorrido) {
        if (ruta.length === 1) return { x: ruta[0].x, z: ruta[0].z, indice: 0 };

        let indice = tramos.acumulado.findIndex((valor) => valor > recorrido) - 1;
        if (indice < 0) indice = ruta.length - 2;

        const largoTramo = tramos.acumulado[indice + 1] - tramos.acumulado[indice] || 1;
        const avance = Math.min(1, (recorrido - tramos.acumulado[indice]) / largoTramo);
        return {
            x: ruta[indice].x + (ruta[indice + 1].x - ruta[indice].x) * avance,
            z: ruta[indice].z + (ruta[indice + 1].z - ruta[indice].z) * avance,
            indice,
        };
    }

    function mostrarInstruccion(texto) {
        if (textoInstruccion) textoInstruccion.textContent = texto;
    }

    function actualizarBotonReproducir() {
        if (!botonReproducir) return;
        botonReproducir.textContent = estado.reproduciendo ? "⏸ Pausar" : "▶ Reproducir";
        botonReproducir.setAttribute("aria-pressed", String(estado.reproduciendo));
    }

    /* ======================================================================
     * 4. Inicio
     * ==================================================================== */

    function iniciar() {
        if (!contenedor) return;
        if (!soporta3D()) return; // Se queda visible el mensaje de fallback.

        fallback.hidden = true;
        const datos = leerEscena();
        const ruta = datos.ruta;
        const tramos = calcularTramos(ruta);

        const escena = new THREE.Scene();
        escena.background = new THREE.Color(COLORES.cielo);
        escena.fog = new THREE.Fog(COLORES.cielo, 120, 260);

        const renderer = crearRenderer();
        const camara = crearCamara();
        agregarLuces(escena);
        agregarSuelo(escena);
        agregarPasillos(escena, datos.pasillos);
        agregarZonas(escena, datos.zonas);
        agregarRuta(escena, ruta);

        const marcador = crearMarcador();
        if (ruta.length > 0) {
            marcador.position.set(ruta[0].x, 0, ruta[0].z);
            escena.add(marcador);
        }

        // Controles de órbita (arrastrar para girar, rueda para acercar).
        let controles = null;
        if (typeof THREE.OrbitControls === "function") {
            controles = new THREE.OrbitControls(camara, renderer.domElement);
            controles.target.set(CENTRO_CAMPUS.x, CENTRO_CAMPUS.y, CENTRO_CAMPUS.z);
            controles.enableDamping = true;
            controles.maxPolarAngle = Math.PI / 2.2; // No dejar ver bajo el suelo.
            controles.minDistance = 20;
            controles.maxDistance = 180;
            controles.update();
        }

        /** Avanza el marcador y actualiza indicación y progreso. */
        function actualizarRecorrido(segundos) {
            if (!estado.reproduciendo || ruta.length < 2) return;

            estado.recorrido = Math.min(tramos.total, estado.recorrido + VELOCIDAD_MARCADOR * segundos);
            const posicion = posicionEnRuta(ruta, tramos, estado.recorrido);
            marcador.position.set(posicion.x, 0, posicion.z);

            if (posicion.indice !== estado.indicePaso) {
                estado.indicePaso = posicion.indice;
                mostrarInstruccion(ruta[posicion.indice].instruccion);
            }

            if (barraProgreso) {
                barraProgreso.value = Math.round((estado.recorrido / tramos.total) * 100);
            }

            if (estado.recorrido >= tramos.total) {
                estado.reproduciendo = false;
                actualizarBotonReproducir();
                mostrarInstruccion(`🎉 ${ruta[ruta.length - 1].instruccion}`);
            }
        }

        /** Cámara en modo "seguir": se coloca detrás y arriba del marcador. */
        function actualizarCamara() {
            if (estado.seguirMarcador && ruta.length > 0) {
                const objetivo = new THREE.Vector3(marcador.position.x, 0, marcador.position.z);
                camara.position.lerp(new THREE.Vector3(objetivo.x + 18, 22, objetivo.z + 22), 0.05);
                if (controles) controles.target.lerp(objetivo, 0.1);
                else camara.lookAt(objetivo);
            }
            if (controles) controles.update();
        }

        function bucle(tiempo) {
            const segundos = estado.ultimoTiempo === null ? 0 : (tiempo - estado.ultimoTiempo) / 1000;
            estado.ultimoTiempo = tiempo;

            actualizarRecorrido(Math.min(segundos, 0.1));
            actualizarCamara();
            renderer.render(escena, camara);
            requestAnimationFrame(bucle);
        }

        // --- Eventos de los botones -------------------------------------
        if (botonReproducir) {
            botonReproducir.addEventListener("click", () => {
                if (estado.recorrido >= tramos.total) estado.recorrido = 0; // Repetir al terminar.
                estado.reproduciendo = !estado.reproduciendo;
                actualizarBotonReproducir();
            });
        }

        if (botonReiniciar) {
            botonReiniciar.addEventListener("click", () => {
                Object.assign(estado, { reproduciendo: false, recorrido: 0, indicePaso: -1 });
                marcador.position.set(ruta[0].x, 0, ruta[0].z);
                if (barraProgreso) barraProgreso.value = 0;
                actualizarBotonReproducir();
                mostrarInstruccion("Presiona «Reproducir» para iniciar el recorrido.");
            });
        }

        if (botonVista) {
            botonVista.addEventListener("click", () => {
                estado.seguirMarcador = !estado.seguirMarcador;
                botonVista.setAttribute("aria-pressed", String(estado.seguirMarcador));
            });
        }

        // --- Ajuste al cambiar el tamaño de la ventana -------------------
        new ResizeObserver(() => {
            const { clientWidth: ancho, clientHeight: alto } = contenedor;
            if (ancho === 0 || alto === 0) return;
            camara.aspect = ancho / alto;
            camara.updateProjectionMatrix();
            renderer.setSize(ancho, alto);
        }).observe(contenedor);

        requestAnimationFrame(bucle);
    }

    document.addEventListener("DOMContentLoaded", iniciar);
})();
