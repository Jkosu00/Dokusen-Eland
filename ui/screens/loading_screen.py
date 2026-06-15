import pygame


class LoadingScreen:
    def __init__(self, screen, fondo_path, spinner_path=None):
        self.screen = screen
        self.ancho = screen.get_width()
        self.alto = screen.get_height()

        self.fondo = pygame.image.load(fondo_path).convert()
        self.fondo = pygame.transform.scale(self.fondo, (self.ancho, self.alto))

        self.spinner = None
        if spinner_path:
            self.spinner = pygame.image.load(spinner_path).convert_alpha()
            self.spinner = pygame.transform.smoothscale(self.spinner, (70, 70))

        self.angulo = 0
        self.font = pygame.font.SysFont("arial", 24, bold=True)

    def draw(self, texto="Cargando..."):
        self.screen.blit(self.fondo, (0, 0))

        render = self.font.render(texto, True, (255, 255, 255))
        self.screen.blit(
            render,
            render.get_rect(center=(self.ancho // 2, int(self.alto * 0.86)))
        )

        if self.spinner:
            self.angulo = (self.angulo + 6) % 360
            spinner_rotado = pygame.transform.rotate(self.spinner, self.angulo)
            rect = spinner_rotado.get_rect(
                center=(self.ancho - 85, self.alto - 85)
            )
            self.screen.blit(spinner_rotado, rect)
        else:
            pygame.draw.circle(
                self.screen,
                (255, 220, 80),
                (self.ancho - 85, self.alto - 85),
                30,
                5
            )

        pygame.display.flip()