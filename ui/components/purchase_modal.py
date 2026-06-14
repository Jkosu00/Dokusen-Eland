import pygame


class PurchaseModal:
    def __init__(
        self,
        ancho_pantalla,
        alto_pantalla,
        cargar_imagen_segura,
        fondo_path="assets/images/UI_Eventos/background.png",
        boton_normal_path="assets/images/UI_Eventos/boton_neutral.png",
        boton_verde_path="assets/images/UI_Eventos/boton_verde.png",
        boton_rojo_path="assets/images/UI_Eventos/boton_rojo.png"
    ):
        self.ancho_pantalla = ancho_pantalla
        self.alto_pantalla = alto_pantalla
        self.cargar_imagen_segura = cargar_imagen_segura

        self.fondo_path = fondo_path
        self.boton_normal_path = boton_normal_path
        self.boton_verde_path = boton_verde_path
        self.boton_rojo_path = boton_rojo_path

        self.abierto = False
        self.modo = None

        self.jugador = None
        self.propiedad = None
        self.precios = {}
        self.impuesto = 0
        self.recompra = 0

        # Tamaño general del modal.
        # Como tu asset tiene padding transparente, se usa grande.
        self.ancho_modal = 980
        self.alto_modal = 560

        self.x = (self.ancho_pantalla - self.ancho_modal) // 2
        self.y = (self.alto_pantalla - self.alto_modal) // 2

        # Imagen izquierda
        self.imagen_ancho = 230
        self.imagen_alto = 230

        # Botones
        self.boton_ancho = 300
        self.boton_alto = 72

        self.fondo = self.cargar_imagen_segura(
            self.fondo_path,
            size=(self.ancho_modal, self.alto_modal),
            usar_alpha=True
        )

        self.boton_normal = self.cargar_imagen_segura(
            self.boton_normal_path,
            size=(self.boton_ancho, self.boton_alto),
            usar_alpha=True
        )

        self.boton_verde = self.cargar_imagen_segura(
            self.boton_verde_path,
            size=(self.boton_ancho, self.boton_alto),
            usar_alpha=True
        )

        self.boton_rojo = self.cargar_imagen_segura(
            self.boton_rojo_path,
            size=(self.boton_ancho, self.boton_alto),
            usar_alpha=True
        )

        # Si no existen verde o rojo, usa el normal.
        if self.boton_verde is None:
            self.boton_verde = self.boton_normal

        if self.boton_rojo is None:
            self.boton_rojo = self.boton_normal

        self.imagen_propiedad = None
        self.botones = []

        self.feedback_mensaje = ""
        self.feedback_tiempo_inicio = 0
        self.feedback_duracion = 2500

        self.descripciones = self._crear_descripciones()
        self.rutas_imagenes = self._crear_rutas_imagenes()

    # ============================================================
    # APERTURAS DEL MODAL
    # ============================================================

    def abrir(self, jugador, propiedad, precios, modo="isla"):
        """
        Método compatible con lo que ya usa GameManager.
        Por defecto abre compra de isla.
        """

        if modo == "poneglyph":
            self.abrir_compra_poneglyph(jugador, propiedad, precios)
        else:
            self.abrir_compra_isla(jugador, propiedad, precios)

    def abrir_compra_isla(self, jugador, propiedad, precios):
        """
        Abre modal de compra de isla.
        Botones:
        - comprar_base
        - comprar_nivel_2
        - comprar_nivel_3
        - no_comprar
        """

        self.abierto = True
        self.modo = "isla"

        self.jugador = jugador
        self.propiedad = propiedad
        self.precios = precios
        self.impuesto = 0
        self.recompra = 0

        self.imagen_propiedad = self._cargar_imagen_propiedad(propiedad.referencia)
        self._crear_botones_isla()

    def abrir_mejora(self, jugador, propiedad):
        """
        Abre modal para mejorar una isla propia.
        Botones:
        - mejorar_propiedad
        - no_mejorar
        """

        self.abierto = True
        self.modo = "mejora"

        self.jugador = jugador
        self.propiedad = propiedad
        self.precios = {}
        self.impuesto = 0
        self.recompra = 0

        self.imagen_propiedad = self._cargar_imagen_propiedad(propiedad.referencia)
        self._crear_botones_mejora()

    def abrir_compra_poneglyph(self, jugador, propiedad, precios):
        """
        Abre modal de compra de Road Poneglyph.
        Botones:
        - comprar_poneglyph
        - no_comprar
        """

        self.abierto = True
        self.modo = "poneglyph"

        self.jugador = jugador
        self.propiedad = propiedad
        self.precios = precios
        self.impuesto = 0
        self.recompra = 0

        self.imagen_propiedad = self._cargar_imagen_propiedad(propiedad.referencia)
        self._crear_botones_poneglyph()

    def abrir_pago_recompra(self, jugador, propiedad, impuesto, recompra):
        """
        Abre modal de impuesto y recompra.
        Botones:
        - pagar_impuesto
        - pagar_y_recomprar
        """

        self.abierto = True
        self.modo = "recompra"

        self.jugador = jugador
        self.propiedad = propiedad
        self.precios = {}
        self.impuesto = impuesto
        self.recompra = recompra

        self.imagen_propiedad = self._cargar_imagen_propiedad(propiedad.referencia)
        self._crear_botones_recompra()

    def cerrar(self):
        self.abierto = False
        self.modo = None

        self.jugador = None
        self.propiedad = None
        self.precios = {}
        self.impuesto = 0
        self.recompra = 0

        self.imagen_propiedad = None
        self.botones = []

        self.feedback_mensaje = ""
        self.feedback_tiempo_inicio = 0

    def mostrar_feedback(self, mensaje, duracion=2500):
        """
        Muestra un mensaje temporal en rojo dentro del modal.
        """

        self.feedback_mensaje = mensaje
        self.feedback_tiempo_inicio = pygame.time.get_ticks()
        self.feedback_duracion = duracion

    # ============================================================
    # DATOS INTERNOS
    # ============================================================

    def _crear_descripciones(self):
        return {
            "dawn_island": "Isla inicial del East Blue. Ideal para comenzar a formar territorio.",
            "shells_town": "Zona del East Blue con valor estratégico para dominar el primer grupo.",
            "orange_town": "Isla comercial del East Blue con buen potencial de crecimiento.",

            "villa_syrup": "Territorio tranquilo del East Blue, útil para completar el segundo monopolio.",
            "baratie": "Restaurante flotante con alto valor comercial en la ruta pirata.",
            "conomi_island": "Isla clave del East Blue final, buena para aumentar ingresos.",

            "little_garden": "Isla peligrosa de Grand Line con gran valor estratégico.",
            "drum_island": "Isla nevada reconocida por sus médicos y su difícil clima.",
            "alabasta": "Reino desértico de gran importancia política y comercial.",

            "mock_town": "Ciudad pirata de paso obligado en la Grand Line.",
            "skypiea": "Isla celestial difícil de alcanzar, con gran valor territorial.",
            "water_7": "Ciudad acuática famosa por sus astilleros y construcción naval.",

            "thriller_bark": "Territorio oscuro y misterioso con gran poder de control.",
            "amazon_lily": "Isla guerrera protegida, valiosa por su posición defensiva.",
            "marineford": "Zona de guerra con alta relevancia estratégica.",

            "gyojin_island": "Isla submarina con conexión entre mares y rutas comerciales.",
            "punk_hazard": "Isla peligrosa con valor experimental y estratégico.",
            "dressrosa": "Reino influyente del Nuevo Mundo, ideal para fortalecer dominio.",

            "zou_island": "Isla viviente y punto clave entre territorios Yonkou.",
            "whole_cake": "Territorio poderoso del Nuevo Mundo con gran valor económico.",
            "wano": "País cerrado y fuerte, clave para controlar el Nuevo Mundo.",

            "egghead": "Isla tecnológica con alto potencial de crecimiento.",
            "elbaf": "Territorio de gigantes con enorme valor militar.",
            "laugh_tale": "Isla legendaria y destino final de los piratas.",

            "road_poneglyph_1": "Poneglyph especial. Reunir los cuatro permite ganar la partida.",
            "road_poneglyph_2": "Poneglyph especial. No puede ser recomprado por otros jugadores.",
            "road_poneglyph_3": "Poneglyph especial. Su valor aumenta según los que posea el jugador.",
            "road_poneglyph_4": "Poneglyph especial. Pieza clave para llegar al One Piece."
        }

    def _crear_rutas_imagenes(self):
        return {
            "dawn_island": "assets/images/board/Casillas/isla_1.png",
            "shells_town": "assets/images/board/Casillas/isla_2.png",
            "orange_town": "assets/images/board/Casillas/isla_3.png",

            "villa_syrup": "assets/images/board/Casillas/isla_4.png",
            "baratie": "assets/images/board/Casillas/isla_5.png",
            "conomi_island": "assets/images/board/Casillas/isla_6.png",

            "little_garden": "assets/images/board/Casillas/isla_7.png",
            "drum_island": "assets/images/board/Casillas/isla_8.png",
            "alabasta": "assets/images/board/Casillas/isla_9.png",

            "mock_town": "assets/images/board/Casillas/isla_10.png",
            "skypiea": "assets/images/board/Casillas/isla_11.png",
            "water_7": "assets/images/board/Casillas/isla_12.png",

            "thriller_bark": "assets/images/board/Casillas/isla_13.png",
            "amazon_lily": "assets/images/board/Casillas/isla_14.png",
            "marineford": "assets/images/board/Casillas/isla_15.png",

            "gyojin_island": "assets/images/board/Casillas/isla_16.png",
            "punk_hazard": "assets/images/board/Casillas/isla_17.png",
            "dressrosa": "assets/images/board/Casillas/isla_18.png",

            "zou_island": "assets/images/board/Casillas/isla_19.png",
            "whole_cake": "assets/images/board/Casillas/isla_20.png",
            "wano": "assets/images/board/Casillas/isla_21.png",

            "egghead": "assets/images/board/Casillas/isla_22.png",
            "elbaf": "assets/images/board/Casillas/isla_23.png",
            "laugh_tale": "assets/images/board/Casillas/isla_24.png",

            "road_poneglyph_1": "assets/images/board/Casillas/road_poneglyph.png",
            "road_poneglyph_2": "assets/images/board/Casillas/road_poneglyph.png",
            "road_poneglyph_3": "assets/images/board/Casillas/road_poneglyph.png",
            "road_poneglyph_4": "assets/images/board/Casillas/road_poneglyph.png",
        }

    def _cargar_imagen_propiedad(self, referencia):
        ruta = self.rutas_imagenes.get(referencia)

        if not ruta:
            return None

        return self.cargar_imagen_segura(
            ruta,
            size=(self.imagen_ancho, self.imagen_alto),
            usar_alpha=True
        )

    # ============================================================
    # CREACIÓN DE BOTONES
    # ============================================================

    def _crear_botones_isla(self):
        self.botones = []

        centro_x = self.x + self.ancho_modal // 2

        espacio = 24
        total_fila = (self.boton_ancho * 2) + espacio

        x_izquierda = centro_x - total_fila // 2
        x_derecha = x_izquierda + self.boton_ancho + espacio

        y_fila_1 = self.y + 355
        y_fila_2 = self.y + 425

        self.botones = [
            {
                "texto": f"Comprar base ${self.precios.get('base', 0)}",
                "accion": "comprar_base",
                "estilo": "verde",
                "rect": pygame.Rect(x_izquierda, y_fila_1, self.boton_ancho, self.boton_alto)
            },
            {
                "texto": f"Nivel 2 ${self.precios.get('nivel_2', 0)}",
                "accion": "comprar_nivel_2",
                "estilo": "verde",
                "rect": pygame.Rect(x_derecha, y_fila_1, self.boton_ancho, self.boton_alto)
            },
            {
                "texto": f"Nivel 3 ${self.precios.get('nivel_3', 0)}",
                "accion": "comprar_nivel_3",
                "estilo": "verde",
                "rect": pygame.Rect(x_izquierda, y_fila_2, self.boton_ancho, self.boton_alto)
            },
            {
                "texto": "No comprar",
                "accion": "no_comprar",
                "estilo": "rojo",
                "rect": pygame.Rect(x_derecha, y_fila_2, self.boton_ancho, self.boton_alto)
            }
        ]

    def _crear_botones_mejora(self):
        self.botones = []

        centro_x = self.x + self.ancho_modal // 2

        espacio = 30
        total_fila = (self.boton_ancho * 2) + espacio

        x_izquierda = centro_x - total_fila // 2
        x_derecha = x_izquierda + self.boton_ancho + espacio

        y_botones = self.y + 410

        costo = self.propiedad.calcular_costo_mejora()

        self.botones = [
            {
                "texto": f"Mejorar ${costo}",
                "accion": "mejorar_propiedad",
                "estilo": "verde",
                "rect": pygame.Rect(x_izquierda, y_botones, self.boton_ancho, self.boton_alto)
            },
            {
                "texto": "No mejorar",
                "accion": "no_mejorar",
                "estilo": "rojo",
                "rect": pygame.Rect(x_derecha, y_botones, self.boton_ancho, self.boton_alto)
            }
        ]

    def _crear_botones_poneglyph(self):
        self.botones = []

        centro_x = self.x + self.ancho_modal // 2

        espacio = 30
        total_fila = (self.boton_ancho * 2) + espacio

        x_izquierda = centro_x - total_fila // 2
        x_derecha = x_izquierda + self.boton_ancho + espacio

        y_botones = self.y + 410

        precio = self.precios.get("base", self.propiedad.precio_actual)

        self.botones = [
            {
                "texto": f"Comprar ${precio}",
                "accion": "comprar_poneglyph",
                "estilo": "verde",
                "rect": pygame.Rect(x_izquierda, y_botones, self.boton_ancho, self.boton_alto)
            },
            {
                "texto": "No comprar",
                "accion": "no_comprar",
                "estilo": "rojo",
                "rect": pygame.Rect(x_derecha, y_botones, self.boton_ancho, self.boton_alto)
            }
        ]

    def _crear_botones_recompra(self):
        self.botones = []

        centro_x = self.x + self.ancho_modal // 2

        espacio = 30
        total_fila = (self.boton_ancho * 2) + espacio

        x_izquierda = centro_x - total_fila // 2
        x_derecha = x_izquierda + self.boton_ancho + espacio

        y_botones = self.y + 410

        self.botones = [
            {
                "texto": f"Pagar impuesto ${self.impuesto}",
                "accion": "pagar_impuesto",
                "estilo": "normal",
                "rect": pygame.Rect(x_izquierda, y_botones, self.boton_ancho, self.boton_alto)
            },
            {
                "texto": f"Pagar y recomprar ${self.impuesto + self.recompra}",
                "accion": "pagar_y_recomprar",
                "estilo": "verde",
                "rect": pygame.Rect(x_derecha, y_botones, self.boton_ancho, self.boton_alto)
            }
        ]

    # ============================================================
    # EVENTOS
    # ============================================================

    def manejar_click(self, pos_mouse):
        if not self.abierto:
            return None

        for boton in self.botones:
            if boton["rect"].collidepoint(pos_mouse):
                return boton["accion"]

        return None

    # ============================================================
    # DIBUJO PRINCIPAL
    # ============================================================

    def dibujar(self, pantalla):
        if not self.abierto or self.propiedad is None:
            return

        self._dibujar_fondo(pantalla)
        self._dibujar_imagen_propiedad(pantalla)
        self._dibujar_informacion(pantalla)
        self._dibujar_botones(pantalla)
        self._dibujar_feedback(pantalla)

    def _dibujar_feedback(self, pantalla):
        """
        Dibuja un mensaje de error o aviso dentro del modal.
        """

        if not self.feedback_mensaje:
            return

        tiempo_actual = pygame.time.get_ticks()

        if tiempo_actual - self.feedback_tiempo_inicio > self.feedback_duracion:
            self.feedback_mensaje = ""
            self.feedback_tiempo_inicio = 0
            return

        centro_x = self.x + self.ancho_modal // 2
        y = self.y + self.alto_modal - 42

        # Fondo pequeño para que el texto se lea bien
        ancho_fondo = 620
        alto_fondo = 32
        x_fondo = centro_x - ancho_fondo // 2

        pygame.draw.rect(
            pantalla,
            (30, 10, 10),
            (x_fondo, y - 8, ancho_fondo, alto_fondo),
            border_radius=10
        )

        pygame.draw.rect(
            pantalla,
            (190, 60, 60),
            (x_fondo, y - 8, ancho_fondo, alto_fondo),
            width=2,
            border_radius=10
        )

        self._dibujar_texto_centrado(
            pantalla,
            self.feedback_mensaje,
            centro_x,
            y + 7,
            16,
            (255, 90, 90)
        )

    def _dibujar_fondo(self, pantalla):
        if self.fondo:
            pantalla.blit(self.fondo, (self.x, self.y))
        else:
            pygame.draw.rect(
                pantalla,
                (18, 18, 28),
                (self.x, self.y, self.ancho_modal, self.alto_modal),
                border_radius=22
            )

            pygame.draw.rect(
                pantalla,
                (230, 190, 80),
                (self.x, self.y, self.ancho_modal, self.alto_modal),
                width=3,
                border_radius=22
            )

    def _dibujar_imagen_propiedad(self, pantalla):
        x_img = self.x + 90
        y_img = self.y + 140

        if self.imagen_propiedad:
            pantalla.blit(self.imagen_propiedad, (x_img, y_img))
        else:
            pygame.draw.rect(
                pantalla,
                (40, 40, 55),
                (x_img, y_img, self.imagen_ancho, self.imagen_alto),
                border_radius=16
            )

            self._dibujar_texto_centrado(
                pantalla,
                "Sin imagen",
                x_img + self.imagen_ancho // 2,
                y_img + self.imagen_alto // 2,
                20,
                (255, 255, 255)
            )

    def _dibujar_informacion(self, pantalla):
        titulo = self.propiedad.nombre

        descripcion = self.descripciones.get(
            self.propiedad.referencia,
            "Propiedad disponible dentro de la ruta pirata."
        )

        # Área derecha de texto
        x_texto = self.x + 365
        y_titulo = self.y + 105
        ancho_texto = 520

        self._dibujar_texto(
            pantalla,
            titulo,
            x_texto,
            y_titulo,
            34,
            (255, 225, 120)
        )

        lineas_descripcion = self._dividir_texto(descripcion, 48)

        y_linea = y_titulo + 48

        for linea in lineas_descripcion[:3]:
            self._dibujar_texto(
                pantalla,
                linea,
                x_texto,
                y_linea,
                19,
                (245, 245, 245)
            )
            y_linea += 27

        if self.modo == "isla":
            self._dibujar_info_isla(pantalla, x_texto, y_linea + 20)

        elif self.modo == "poneglyph":
            self._dibujar_info_poneglyph(pantalla, x_texto, y_linea + 20)

        elif self.modo == "recompra":
            self._dibujar_info_recompra(pantalla, x_texto, y_linea + 20)

        elif self.modo == "mejora":
            self._dibujar_info_mejora(pantalla, x_texto, y_linea + 20)

    def _dibujar_info_mejora(self, pantalla, x_texto, y_info):
        nivel_actual = self.propiedad.nivel_mejora
        nivel_siguiente = nivel_actual + 1
        costo = self.propiedad.calcular_costo_mejora()
        impuesto_actual = self.propiedad.calcular_impuesto()

        self._dibujar_texto(
            pantalla,
            f"Nivel actual: {nivel_actual}",
            x_texto,
            y_info,
            20,
            (255, 255, 255)
        )

        self._dibujar_texto(
            pantalla,
            f"Siguiente nivel: {nivel_siguiente}",
            x_texto,
            y_info + 32,
            20,
            (180, 220, 255)
        )

        self._dibujar_texto(
            pantalla,
            f"Costo de mejora: ${costo}",
            x_texto,
            y_info + 64,
            20,
            (255, 220, 160)
        )

        self._dibujar_texto(
            pantalla,
            f"Impuesto actual: ${impuesto_actual}",
            x_texto,
            y_info + 96,
            17,
            (210, 210, 210)
        )

    def _dibujar_info_isla(self, pantalla, x_texto, y_info):
        precio_base = self.precios.get("base", self.propiedad.precio_actual)
        precio_nivel_2 = self.precios.get("nivel_2", precio_base)
        precio_nivel_3 = self.precios.get("nivel_3", precio_base)

        self._dibujar_texto(
            pantalla,
            f"Precio base: ${precio_base}",
            x_texto,
            y_info,
            20,
            (255, 255, 255)
        )

        self._dibujar_texto(
            pantalla,
            f"Nivel 2: ${precio_nivel_2}  |  Nivel 3: ${precio_nivel_3}",
            x_texto,
            y_info + 32,
            20,
            (180, 220, 255)
        )

        self._dibujar_texto(
            pantalla,
            "Cada nivel agrega mejoras iniciales a la isla.",
            x_texto,
            y_info + 64,
            16,
            (210, 210, 210)
        )

    def _dibujar_info_poneglyph(self, pantalla, x_texto, y_info):
        precio = self.precios.get("base", self.propiedad.precio_actual)

        self._dibujar_texto(
            pantalla,
            f"Precio: ${precio}",
            x_texto,
            y_info,
            22,
            (255, 255, 255)
        )

        self._dibujar_texto(
            pantalla,
            "No se puede recomprar.",
            x_texto,
            y_info + 34,
            19,
            (255, 190, 130)
        )

        self._dibujar_texto(
            pantalla,
            "Reúne los 4 Road Poneglyphs para ganar.",
            x_texto,
            y_info + 66,
            16,
            (210, 210, 210)
        )

    def _dibujar_info_recompra(self, pantalla, x_texto, y_info):
        dueno = self.propiedad.dueno.nombre if self.propiedad.dueno else "Sin dueño"

        self._dibujar_texto(
            pantalla,
            f"Dueño actual: {dueno}",
            x_texto,
            y_info,
            20,
            (255, 255, 255)
        )

        self._dibujar_texto(
            pantalla,
            f"Impuesto: ${self.impuesto}",
            x_texto,
            y_info + 32,
            20,
            (255, 220, 160)
        )

        self._dibujar_texto(
            pantalla,
            f"Recompra: ${self.recompra}",
            x_texto,
            y_info + 64,
            20,
            (180, 220, 255)
        )

        self._dibujar_texto(
            pantalla,
            f"Total para recomprar: ${self.impuesto + self.recompra}",
            x_texto,
            y_info + 96,
            17,
            (210, 210, 210)
        )

    def _dibujar_botones(self, pantalla):
        mouse_pos = pygame.mouse.get_pos()

        for boton in self.botones:
            rect = boton["rect"]
            hover = rect.collidepoint(mouse_pos)

            imagen_boton = self._obtener_imagen_boton(boton["estilo"])

            if imagen_boton:
                pantalla.blit(imagen_boton, rect.topleft)
            else:
                color = self._obtener_color_boton(boton["estilo"], hover)

                pygame.draw.rect(
                    pantalla,
                    color,
                    rect,
                    border_radius=14
                )

                pygame.draw.rect(
                    pantalla,
                    (230, 190, 80),
                    rect,
                    width=2,
                    border_radius=14
                )

            if hover:
                pygame.draw.rect(
                    pantalla,
                    (255, 245, 150),
                    rect,
                    width=3,
                    border_radius=14
                )

            self._dibujar_texto_centrado(
                pantalla,
                boton["texto"],
                rect.centerx,
                rect.centery - 2,
                17,
                (255, 255, 255)
            )

    def _obtener_imagen_boton(self, estilo):
        if estilo == "verde":
            return self.boton_verde

        if estilo == "rojo":
            return self.boton_rojo

        return self.boton_normal

    def _obtener_color_boton(self, estilo, hover):
        if estilo == "verde":
            return (45, 125, 65) if hover else (35, 100, 55)

        if estilo == "rojo":
            return (145, 55, 55) if hover else (115, 40, 40)

        return (65, 75, 105) if hover else (45, 55, 85)

    # ============================================================
    # TEXTO
    # ============================================================

    def _dibujar_texto(self, pantalla, texto, x, y, size=20, color=(255, 255, 255)):
        fuente = pygame.font.SysFont("arial", size, bold=True)
        render = fuente.render(str(texto), True, color)
        pantalla.blit(render, (x, y))

    def _dibujar_texto_centrado(self, pantalla, texto, centro_x, centro_y, size=20, color=(255, 255, 255)):
        fuente = pygame.font.SysFont("arial", size, bold=True)
        render = fuente.render(str(texto), True, color)
        rect = render.get_rect(center=(centro_x, centro_y))
        pantalla.blit(render, rect)

    def _dividir_texto(self, texto, max_caracteres):
        palabras = texto.split()
        lineas = []
        linea_actual = ""

        for palabra in palabras:
            prueba = f"{linea_actual} {palabra}".strip()

            if len(prueba) <= max_caracteres:
                linea_actual = prueba
            else:
                if linea_actual:
                    lineas.append(linea_actual)

                linea_actual = palabra

        if linea_actual:
            lineas.append(linea_actual)

        return lineas