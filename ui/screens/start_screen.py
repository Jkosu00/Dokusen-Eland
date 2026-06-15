
import pygame
import sys
from pathlib import Path

from ui.components.button import ImageButton
from services.sound_service import SoundService


class StartScreen:
    def __init__(self, screen):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()

        self.start_time = pygame.time.get_ticks()

        self.base_dir = Path(__file__).resolve().parents[2]

        # Servicio de sonido
        self.sound_service = SoundService()

        # Música del menú
        self.sound_service.play_music("menu")

        self.title_hold_time = 3000
        self.title_move_time = 1800
        self.buttons_delay = 450
        self.buttons_fade_time = 1200

        self.background = pygame.image.load(
            self.base_dir / "assets/images/UI_Eventos/Menu/fondo_start_screen.png"
        ).convert()

        self.background = pygame.transform.scale(
            self.background, (self.width, self.height)
        )

        self.title = pygame.image.load(
            self.base_dir / "assets/images/UI_Eventos/Menu/titulo_start_screen.png"
        ).convert_alpha()

        self.title = pygame.transform.scale(self.title, (1010, 505))

        self.title_x = self.width // 2
        self.title_start_y = self.height // 2
        self.title_end_y = 150

        self.btn_jugar = ImageButton(
            self.width // 2,
            405,
            self.base_dir / "assets/images/UI_Eventos/Menu/btn_jugar_normal.png",
            self.base_dir / "assets/images/UI_Eventos/Menu/btn_jugar_hover.png",
            scale=(330, 180),
        )

        self.btn_salir = ImageButton(
            self.width // 2,
            525,
            self.base_dir / "assets/images/UI_Eventos/Menu/btn_salir_normal.png",
            self.base_dir / "assets/images/UI_Eventos/Menu/btn_salir_hover.png",
            scale=(330, 180),
        )

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.start_time

            buttons_start_time = self.title_hold_time + self.buttons_delay

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if elapsed > buttons_start_time:
                    if self.btn_jugar.is_clicked(event):
                        self.sound_service.play_effect("click")
                        return "jugar"

                    if self.btn_salir.is_clicked(event):
                        self.sound_service.play_effect("click")
                        pygame.time.delay(250)
                        pygame.quit()
                        sys.exit()

            self.draw(elapsed)

            pygame.display.flip()
            clock.tick(60)

    def draw(self, elapsed):
        self.screen.blit(self.background, (0, 0))

        # Oscurecer fondo
        overlay_alpha = min(150, 40 + elapsed // 20)
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, overlay_alpha))
        self.screen.blit(overlay, (0, 0))

        # Movimiento del título
        if elapsed < self.title_hold_time:
            title_y = self.title_start_y
        else:
            move_elapsed = elapsed - self.title_hold_time
            title_progress = min(move_elapsed / self.title_move_time, 1)

            # Suavizado
            title_progress = title_progress * title_progress * (3 - 2 * title_progress)

            title_y = self.title_start_y + (
                self.title_end_y - self.title_start_y
            ) * title_progress

        title_rect = self.title.get_rect(center=(self.title_x, title_y))
        self.screen.blit(self.title, title_rect)

        # Aparición de botones
        buttons_start_time = self.title_hold_time + self.buttons_delay

        if elapsed > buttons_start_time:
            button_alpha = int(
                min((elapsed - buttons_start_time) / self.buttons_fade_time, 1) * 255
            )

            self.btn_jugar.draw(self.screen, button_alpha)
            self.btn_salir.draw(self.screen, button_alpha)