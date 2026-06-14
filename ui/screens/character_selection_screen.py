import pygame


class CharacterSelectionScreen:
    def __init__(self, screen, personajes, cantidad_jugadores=4, fondo_path=None):
        self.screen = screen
        self.personajes = personajes
        self.cantidad_jugadores = cantidad_jugadores

        self.ancho = screen.get_width()
        self.alto = screen.get_height()
        self.clock = pygame.time.Clock()

        self.font_title = pygame.font.SysFont("arial", 38, bold=True)
        self.font = pygame.font.SysFont("arial", 24, bold=True)
        self.font_small = pygame.font.SysFont("arial", 17, bold=True)

        self.jugador_actual = 0
        self.nombre_actual = ""
        self.input_activo = False
        self.personaje_seleccionado = None
        self.jugadores_configurados = []

        self.fondo = self._cargar_imagen(fondo_path, (self.ancho, self.alto))

        self.input_img = self._cargar_imagen(
            "assets/images/UI_Eventos/input.png",
            (520, 64)
        )

        self.boton_siguiente_img = self._cargar_imagen(
            "assets/images/UI_Eventos/boton_verde.png",
            (300, 70)
        )

        self.boton_volver_img = self._cargar_imagen(
            "assets/images/UI_Eventos/boton_rojo.png",
            (190, 62)
        )

        self.input_rect = pygame.Rect(
            self.ancho // 2 - 260,
            195,
            520,
            64
        )

        self.boton_siguiente = pygame.Rect(
            self.ancho // 2 - 150,
            self.alto - 165,
            300,
            70
        )

        self.boton_volver = pygame.Rect(
            120,
            self.alto - 165,
            190,
            62
        )

        self.banner_rects = self._crear_rects_banners()

        self.banners_cargados = self._cargar_banners()

    def _crear_rects_banners(self):
        rects = []

        margen_lateral = 35
        gap = 14
        banner_w = (self.ancho - margen_lateral * 2 - gap * 6) // 8
        banner_h = int(banner_w * 1.85)

        max_h = self.alto - 360
        if banner_h > max_h:
            banner_h = max_h
            banner_w = int(banner_h / 1.45)

        total_w = banner_w * 7 + gap * 6
        start_x = (self.ancho - total_w) // 2
        y = self.alto // 2 - banner_h // 2 + 40

        for i in range(7):
            x = start_x + i * (banner_w + gap)
            rects.append(pygame.Rect(x, y, banner_w, banner_h))

        return rects

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None

                    if event.key == pygame.K_BACKSPACE and self.input_activo:
                        self.nombre_actual = self.nombre_actual[:-1]

                    elif event.key == pygame.K_RETURN:
                        resultado = self._intentar_siguiente()
                        if resultado is not None:
                            return resultado

                    else:
                        if self.input_activo and len(self.nombre_actual) < 16 and event.unicode.isprintable():
                            self.nombre_actual += event.unicode

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.input_rect.collidepoint(event.pos):
                        self.input_activo = True
                    else:
                        self.input_activo = False

                    if self.boton_volver.collidepoint(event.pos):
                        return None

                    if self.boton_siguiente.collidepoint(event.pos):
                        resultado = self._intentar_siguiente()
                        if resultado is not None:
                            return resultado

                    for i, rect in enumerate(self.banner_rects):
                        if rect.collidepoint(event.pos):
                            if not self._personaje_ya_usado(i):
                                self.personaje_seleccionado = i

            self._dibujar()
            pygame.display.flip()
            self.clock.tick(60)

    def _personaje_ya_usado(self, indice):
        for jugador in self.jugadores_configurados:
            if jugador["personaje_indice"] == indice:
                return True
        return False

    def _intentar_siguiente(self):
        nombre = self.nombre_actual.strip()

        if nombre == "" or self.personaje_seleccionado is None:
            return None

        personaje = self.personajes[self.personaje_seleccionado]

        self.jugadores_configurados.append({
            "nombre": nombre,
            "personaje_indice": self.personaje_seleccionado,
            "personaje": personaje
        })

        if len(self.jugadores_configurados) >= self.cantidad_jugadores:
            return self.jugadores_configurados

        self.jugador_actual += 1
        self.nombre_actual = ""
        self.personaje_seleccionado = None
        return None

    def _dibujar(self):
        if self.fondo:
            self.screen.blit(self.fondo, (0, 0))
        else:
            self.screen.fill((18, 24, 34))

        titulo = self.font_title.render(
            f"Jugador {self.jugador_actual + 1}: escribe tu nombre y elige personaje",
            True,
            (255, 225, 95)
        )
        self.screen.blit(
            titulo,
            titulo.get_rect(center=(self.ancho // 2, int(self.alto * 0.19)))
        )

        self._dibujar_input()
        self._dibujar_banners()
        self._dibujar_botones()

    def _dibujar_input(self):
        if self.input_img:
            self.screen.blit(self.input_img, self.input_rect.topleft)
        else:
            pygame.draw.rect(self.screen, (245, 245, 245), self.input_rect, border_radius=10)

        if self.input_activo:
            pygame.draw.rect(
                self.screen,
                (255, 220, 60),
                self.input_rect,
                width=4,
                border_radius=10
            )

        texto = self.nombre_actual if self.nombre_actual else "Nombre del jugador"
        color = (30, 30, 30) if self.nombre_actual else (120, 120, 120)

        render = self.font.render(texto, True, color)
        self.screen.blit(render, (self.input_rect.x + 28, self.input_rect.y + 18))

    def _dibujar_banners(self):
        for i, rect in enumerate(self.banner_rects):
            banner = self.banners_cargados[i]

            if banner:
                self.screen.blit(banner, rect.topleft)
            else:
                pygame.draw.rect(self.screen, (50, 55, 70), rect)

            if self._personaje_ya_usado(i):
                overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 160))
                self.screen.blit(overlay, rect.topleft)

                texto = self.font_small.render("ESCOGIDO", True, (255, 90, 90))
                self.screen.blit(texto, texto.get_rect(center=rect.center))

            if self.personaje_seleccionado == i:
                overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                overlay.fill((255, 220, 60, 45))
                self.screen.blit(overlay, rect.topleft)

    def _cargar_banners(self):
        banners = []

        for i, personaje in enumerate(self.personajes):
            rect = self.banner_rects[i]
            imagen = self._cargar_imagen(personaje["banner"], (rect.width, rect.height))
            banners.append(imagen)

        return banners

    def _dibujar_botones(self):
        self._dibujar_boton_asset(
            self.boton_volver,
            self.boton_volver_img,
            "Volver"
        )

        texto = "Siguiente jugador"
        if self.jugador_actual == self.cantidad_jugadores - 1:
            texto = "Empezar partida"

        self._dibujar_boton_asset(
            self.boton_siguiente,
            self.boton_siguiente_img,
            texto
        )

    def _dibujar_boton_asset(self, rect, imagen, texto):
        if imagen:
            self.screen.blit(imagen, rect.topleft)
        else:
            pygame.draw.rect(self.screen, (40, 130, 70), rect, border_radius=10)

        render = self.font.render(texto, True, (255, 255, 255))
        self.screen.blit(render, render.get_rect(center=rect.center))

    def _cargar_imagen(self, path, size):
        if not path:
            return None

        try:
            imagen = pygame.image.load(path).convert_alpha()
            return pygame.transform.smoothscale(imagen, size)
        except Exception:
            return None