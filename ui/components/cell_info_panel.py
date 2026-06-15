import pygame


class CellInfoPanel:
    def __init__(self, ancho_pantalla, alto_pantalla):
        self.ancho_pantalla = ancho_pantalla
        self.alto_pantalla = alto_pantalla

        self.abierto = False

        self.titulo = ""
        self.subtitulo = ""
        self.lineas = []
        self.tipo = "info"

        # Tamaño del panel lateral
        self.ancho = 340
        self.alto = 380

        # Posición por defecto: lado derecho, centrado verticalmente
        self.margen = 20
        self.x = self.ancho_pantalla - self.ancho - self.margen
        self.y = (self.alto_pantalla - self.alto) // 2

        # Colores
        self.color_fondo = (18, 18, 28)
        self.color_borde = (230, 190, 80)
        self.color_titulo = (255, 230, 130)
        self.color_subtitulo = (180, 220, 255)
        self.color_texto = (245, 245, 245)
        self.color_texto_secundario = (170, 170, 170)

    # ============================================================
    # CONTROL DEL PANEL
    # ============================================================

    def abrir(self, titulo, subtitulo="", lineas=None, tipo="info"):
        self.abierto = True
        self.titulo = str(titulo)
        self.subtitulo = str(subtitulo)
        self.lineas = lineas if lineas is not None else []
        self.tipo = tipo

    def cerrar(self):
        self.abierto = False
        self.titulo = ""
        self.subtitulo = ""
        self.lineas = []
        self.tipo = "info"

    def alternar(self, titulo, subtitulo="", lineas=None, tipo="info"):
        if self.abierto and self.titulo == titulo:
            self.cerrar()
        else:
            self.abrir(titulo, subtitulo, lineas, tipo)

    def contiene_punto(self, pos_mouse):
        rect = pygame.Rect(self.x, self.y, self.ancho, self.alto)
        return rect.collidepoint(pos_mouse)

    def actualizar_tamano_pantalla(self, ancho_pantalla, alto_pantalla):
        self.ancho_pantalla = ancho_pantalla
        self.alto_pantalla = alto_pantalla

        self.x = self.ancho_pantalla - self.ancho - self.margen
        self.y = (self.alto_pantalla - self.alto) // 2

    # ============================================================
    # DIBUJO PRINCIPAL
    # ============================================================

    def dibujar(self, pantalla):
        if not self.abierto:
            return

        self._dibujar_fondo(pantalla)
        self._dibujar_encabezado(pantalla)
        self._dibujar_contenido(pantalla)
        self._dibujar_pie(pantalla)

    def _dibujar_fondo(self, pantalla):
        rect_panel = pygame.Rect(self.x, self.y, self.ancho, self.alto)

        # Sombra
        sombra = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        pygame.draw.rect(
            sombra,
            (0, 0, 0, 120),
            (8, 8, self.ancho - 8, self.alto - 8),
            border_radius=20
        )
        pantalla.blit(sombra, (self.x, self.y))

        # Fondo
        pygame.draw.rect(
            pantalla,
            self.color_fondo,
            rect_panel,
            border_radius=20
        )

        # Borde según tipo
        pygame.draw.rect(
            pantalla,
            self._obtener_color_borde(),
            rect_panel,
            width=3,
            border_radius=20
        )

    def _dibujar_encabezado(self, pantalla):
        x_texto = self.x + 20
        y_texto = self.y + 22

        titulo = self._recortar_texto(self.titulo, 24)

        self._dibujar_texto(
            pantalla,
            titulo,
            x_texto,
            y_texto,
            23,
            self.color_titulo
        )

        if self.subtitulo:
            subtitulo = self._recortar_texto(self.subtitulo, 34)

            self._dibujar_texto(
                pantalla,
                subtitulo,
                x_texto,
                y_texto + 34,
                16,
                self.color_subtitulo
            )

        # Línea separadora
        pygame.draw.line(
            pantalla,
            (90, 80, 60),
            (self.x + 18, self.y + 78),
            (self.x + self.ancho - 18, self.y + 78),
            2
        )

    def _dibujar_contenido(self, pantalla):
        x_texto = self.x + 22
        y_actual = self.y + 98

        ancho_max_caracteres = 34
        alto_maximo = self.y + self.alto - 55

        for linea in self.lineas:
            sublineas = self._dividir_texto(str(linea), ancho_max_caracteres)

            for sublinea in sublineas:
                if y_actual >= alto_maximo:
                    self._dibujar_texto(
                        pantalla,
                        "...",
                        x_texto,
                        y_actual,
                        15,
                        self.color_texto_secundario
                    )
                    return

                color = self._color_linea(sublinea)

                self._dibujar_texto(
                    pantalla,
                    sublinea,
                    x_texto,
                    y_actual,
                    15,
                    color
                )

                y_actual += 23

            y_actual += 3

    def _dibujar_pie(self, pantalla):
        texto_pie = "Click fuera del tablero para cerrar"

        self._dibujar_texto(
            pantalla,
            texto_pie,
            self.x + 20,
            self.y + self.alto - 32,
            13,
            self.color_texto_secundario
        )

    # ============================================================
    # COLORES
    # ============================================================

    def _obtener_color_borde(self):
        if self.tipo == "isla":
            return (230, 190, 80)

        if self.tipo == "road_poneglyph":
            return (255, 80, 80)

        if self.tipo == "evento":
            return (150, 220, 255)

        if self.tipo == "riesgo":
            return (255, 90, 90)

        if self.tipo == "premio":
            return (255, 220, 90)

        if self.tipo == "descanso":
            return (130, 210, 255)

        if self.tipo == "prision":
            return (170, 170, 190)

        if self.tipo == "yonkou":
            return (255, 205, 80)

        if self.tipo == "salida":
            return (120, 255, 150)

        return self.color_borde

    def _color_linea(self, linea):
        texto = linea.lower()

        if "libre" in texto:
            return (130, 255, 160)

        if "dueño" in texto:
            return (255, 230, 130)

        if "precio" in texto or "costo" in texto or "impuesto" in texto or "recompra" in texto:
            return (180, 220, 255)

        if "yonkou: sí" in texto or "sí" in texto:
            return (255, 215, 80)

        if "no puede" in texto or "riesgo" in texto:
            return (255, 140, 140)

        return self.color_texto

    # ============================================================
    # TEXTO
    # ============================================================

    def _dibujar_texto(self, pantalla, texto, x, y, size, color):
        fuente = pygame.font.SysFont("arial", size, bold=True)
        render = fuente.render(str(texto), True, color)
        pantalla.blit(render, (x, y))

    def _recortar_texto(self, texto, max_caracteres):
        texto = str(texto)

        if len(texto) <= max_caracteres:
            return texto

        return texto[:max_caracteres - 3] + "..."

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