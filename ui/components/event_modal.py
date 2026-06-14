import pygame


class EventModal:
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

        self.titulo = ""
        self.mensaje = ""
        self.tipo = "info"
        self.opciones = []

        self.feedback_mensaje = ""
        self.feedback_tiempo_inicio = 0
        self.feedback_duracion = 2500

        # Tamaño grande para compensar padding transparente del asset.
        self.ancho_modal = 920
        self.alto_modal = 500

        self.x = (self.ancho_pantalla - self.ancho_modal) // 2
        self.y = (self.alto_pantalla - self.alto_modal) // 2

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

        if self.boton_verde is None:
            self.boton_verde = self.boton_normal

        if self.boton_rojo is None:
            self.boton_rojo = self.boton_normal

        self.botones = []

    # ============================================================
    # APERTURA / CIERRE
    # ============================================================

    def abrir(self, titulo, mensaje, tipo="info", opciones=None):
        """
        Abre el panel de evento.

        opciones debe ser una lista de diccionarios:
        [
            {"texto": "Continuar", "accion": "continuar", "estilo": "verde"}
        ]
        """

        self.abierto = True
        self.titulo = titulo
        self.mensaje = mensaje
        self.tipo = tipo

        if opciones is None:
            opciones = [
                {
                    "texto": "Continuar",
                    "accion": "continuar",
                    "estilo": "verde"
                }
            ]

        self.opciones = opciones
        self.feedback_mensaje = ""
        self.feedback_tiempo_inicio = 0

        self._crear_botones()

    def cerrar(self):
        self.abierto = False

        self.titulo = ""
        self.mensaje = ""
        self.tipo = "info"
        self.opciones = []
        self.botones = []

        self.feedback_mensaje = ""
        self.feedback_tiempo_inicio = 0

    def mostrar_feedback(self, mensaje, duracion=2500):
        self.feedback_mensaje = mensaje
        self.feedback_tiempo_inicio = pygame.time.get_ticks()
        self.feedback_duracion = duracion

    # ============================================================
    # BOTONES
    # ============================================================

    def _crear_botones(self):
        self.botones = []

        cantidad = len(self.opciones)

        if cantidad == 1:
            x_boton = self.x + (self.ancho_modal - self.boton_ancho) // 2
            y_boton = self.y + 375

            opcion = self.opciones[0]

            self.botones.append({
                "texto": opcion.get("texto", "Continuar"),
                "accion": opcion.get("accion", "continuar"),
                "estilo": opcion.get("estilo", "verde"),
                "rect": pygame.Rect(
                    x_boton,
                    y_boton,
                    self.boton_ancho,
                    self.boton_alto
                )
            })

            return

        if cantidad == 2:
            espacio = 36
            total = (self.boton_ancho * 2) + espacio
            x_izquierda = self.x + (self.ancho_modal - total) // 2
            x_derecha = x_izquierda + self.boton_ancho + espacio
            y_boton = self.y + 375

            posiciones = [x_izquierda, x_derecha]

            for i, opcion in enumerate(self.opciones[:2]):
                self.botones.append({
                    "texto": opcion.get("texto", "Opción"),
                    "accion": opcion.get("accion", "accion"),
                    "estilo": opcion.get("estilo", "normal"),
                    "rect": pygame.Rect(
                        posiciones[i],
                        y_boton,
                        self.boton_ancho,
                        self.boton_alto
                    )
                })

            return

        # Para 3 o más opciones: las acomoda en filas.
        espacio_x = 24
        espacio_y = 14

        columnas = 2
        total_fila = (self.boton_ancho * columnas) + espacio_x
        x_inicio = self.x + (self.ancho_modal - total_fila) // 2
        y_inicio = self.y + 335

        for i, opcion in enumerate(self.opciones):
            fila = i // columnas
            columna = i % columnas

            x_boton = x_inicio + columna * (self.boton_ancho + espacio_x)
            y_boton = y_inicio + fila * (self.boton_alto + espacio_y)

            self.botones.append({
                "texto": opcion.get("texto", "Opción"),
                "accion": opcion.get("accion", "accion"),
                "estilo": opcion.get("estilo", "normal"),
                "rect": pygame.Rect(
                    x_boton,
                    y_boton,
                    self.boton_ancho,
                    self.boton_alto
                )
            })

    def manejar_click(self, pos_mouse):
        if not self.abierto:
            return None

        for boton in self.botones:
            if boton["rect"].collidepoint(pos_mouse):
                return boton["accion"]

        return None

    # ============================================================
    # DIBUJO
    # ============================================================

    def dibujar(self, pantalla):
        if not self.abierto:
            return

        self._dibujar_fondo(pantalla)
        self._dibujar_titulo(pantalla)
        self._dibujar_mensaje(pantalla)
        self._dibujar_botones(pantalla)
        self._dibujar_feedback(pantalla)

    def _dibujar_fondo(self, pantalla):
        if self.fondo:
            pantalla.blit(self.fondo, (self.x, self.y))
            return

        pygame.draw.rect(
            pantalla,
            (18, 18, 28),
            (self.x, self.y, self.ancho_modal, self.alto_modal),
            border_radius=24
        )

        pygame.draw.rect(
            pantalla,
            self._color_por_tipo(),
            (self.x, self.y, self.ancho_modal, self.alto_modal),
            width=4,
            border_radius=24
        )

    def _dibujar_titulo(self, pantalla):
        centro_x = self.x + self.ancho_modal // 2
        y_titulo = self.y + 95

        self._dibujar_texto_centrado(
            pantalla,
            self.titulo,
            centro_x,
            y_titulo,
            36,
            self._color_por_tipo()
        )

    def _dibujar_mensaje(self, pantalla):
        centro_x = self.x + self.ancho_modal // 2
        x_texto = self.x + 150
        y_texto = self.y + 155
        ancho_linea = 60

        lineas = self._dividir_texto(self.mensaje, ancho_linea)

        for linea in lineas[:6]:
            self._dibujar_texto_centrado(
                pantalla,
                linea,
                centro_x,
                y_texto,
                22,
                (245, 245, 245)
            )

            y_texto += 32

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
                18,
                (255, 255, 255)
            )

    def _dibujar_feedback(self, pantalla):
        if not self.feedback_mensaje:
            return

        tiempo_actual = pygame.time.get_ticks()

        if tiempo_actual - self.feedback_tiempo_inicio > self.feedback_duracion:
            self.feedback_mensaje = ""
            self.feedback_tiempo_inicio = 0
            return

        centro_x = self.x + self.ancho_modal // 2
        y = self.y + self.alto_modal - 40

        ancho_fondo = 620
        alto_fondo = 34
        x_fondo = centro_x - ancho_fondo // 2

        pygame.draw.rect(
            pantalla,
            (30, 10, 10),
            (x_fondo, y - 10, ancho_fondo, alto_fondo),
            border_radius=10
        )

        pygame.draw.rect(
            pantalla,
            (190, 60, 60),
            (x_fondo, y - 10, ancho_fondo, alto_fondo),
            width=2,
            border_radius=10
        )

        self._dibujar_texto_centrado(
            pantalla,
            self.feedback_mensaje,
            centro_x,
            y + 6,
            16,
            (255, 90, 90)
        )

    # ============================================================
    # UTILIDADES VISUALES
    # ============================================================

    def _color_por_tipo(self):
        if self.tipo == "premio":
            return (255, 220, 90)

        if self.tipo == "riesgo_malo":
            return (255, 90, 90)

        if self.tipo == "riesgo_bueno":
            return (120, 255, 150)

        if self.tipo == "prision":
            return (170, 170, 190)

        if self.tipo == "descanso":
            return (130, 210, 255)

        if self.tipo == "yonkou":
            return (255, 205, 80)

        return (230, 190, 80)

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
        palabras = str(texto).split()
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