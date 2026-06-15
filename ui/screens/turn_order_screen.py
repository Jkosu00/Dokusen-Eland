import pygame
import sys

from game.dice import Dice
from services.sound_service import SoundService

class TurnOrderScreen:
    def __init__(self, screen, jugadores, fondo_path=None):
        self.screen = screen
        self.jugadores = jugadores

        self.ancho = screen.get_width()
        self.alto = screen.get_height()
        self.clock = pygame.time.Clock()
        self.sound_service = SoundService()
        self.dice = Dice(size=(120, 120), animation_duration=1000)

        self.font_title = pygame.font.SysFont("arial", 44, bold=True)
        self.font = pygame.font.SysFont("arial", 28, bold=True)
        self.font_small = pygame.font.SysFont("arial", 21, bold=True)
        self.font_resultados = pygame.font.SysFont("arial", 30, bold=True)

        self.fondo = self._cargar_imagen(fondo_path, (self.ancho, self.alto))

        self.boton_lanzar = pygame.Rect(
            int(self.ancho * 0.40),
            int(self.alto * 0.75),
            int(self.ancho * 0.20),
            int(self.alto * 0.16)
        )

        self.boton_volver = pygame.Rect(
            int(self.ancho * 0.10),
            int(self.alto * 0.75),
            int(self.ancho * 0.13),
            int(self.alto * 0.16)
        )

        self.boton_lanzar_img = self._cargar_imagen(
            "assets/images/UI_Eventos/boton_verde.png",
            (self.boton_lanzar.width, self.boton_lanzar.height)
        )

        self.boton_volver_img = self._cargar_imagen(
            "assets/images/UI_Eventos/boton_rojo.png",
            (self.boton_volver.width, self.boton_volver.height)
        )

        self.indice_jugador = 0
        self.resultados = []
        self.estado = "esperando_tiro"

        self.resultado_actual = ""
        self.mensaje = "Presiona el botón para lanzar los dados"

    def run(self):
        while True:
            self.clock.tick(60)
            self.dice.actualizar()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None

                    if event.key == pygame.K_SPACE:
                        self._accion_boton_principal()

                    if event.key == pygame.K_RETURN and self.estado == "orden_listo":
                        return self._obtener_jugadores_ordenados()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.boton_volver.collidepoint(event.pos):
                        self.sound_service.play_effect("click")
                        pygame.time.delay(150)
                        return None

                    if self.boton_lanzar.collidepoint(event.pos):
                        self.sound_service.play_effect("click")
                        resultado = self._accion_boton_principal()

                        if resultado is not None:
                            return resultado

            if self.estado == "tirando" and not self.dice.esta_animando():
                self._guardar_resultado()

            self._dibujar()
            pygame.display.flip()

    def _accion_boton_principal(self):
        if self.estado == "esperando_tiro":
            self._iniciar_tiro()
            return None

        if self.estado == "orden_listo":
            return self._obtener_jugadores_ordenados()

        return None

    def _iniciar_tiro(self):
        jugador = self.jugadores[self.indice_jugador]
        
        self.sound_service.play_effect("dados")
        
        self.resultado_actual = ""
        self.mensaje = f"{jugador.nombre} está lanzando..."
        self.estado = "tirando"
        self.dice.iniciar_lanzamiento()

    def _guardar_resultado(self):
        dado_1, dado_2, suma = self.dice.obtener_resultados()
        jugador = self.jugadores[self.indice_jugador]

        jugador.ultima_tirada = suma

        self.resultados.append({
            "jugador": jugador,
            "dado_1": dado_1,
            "dado_2": dado_2,
            "suma": suma
        })

        self.resultado_actual = f"{jugador.nombre} sacó {dado_1} + {dado_2} = {suma}"
        self.indice_jugador += 1

        if self.indice_jugador >= len(self.jugadores):
            self.estado = "orden_listo"
            self.mensaje = "Orden definido. Presiona Empezar juego."
            return

        siguiente = self.jugadores[self.indice_jugador]
        self.estado = "esperando_tiro"
        self.mensaje = f"Sigue {siguiente.nombre}. Presiona Lanzar dados."

    def _obtener_jugadores_ordenados(self):
        resultados_ordenados = sorted(
            self.resultados,
            key=lambda item: item["suma"],
            reverse=True
        )

        jugadores_ordenados = []

        for indice, item in enumerate(resultados_ordenados):
            jugador = item["jugador"]
            jugador.orden_turno = indice + 1
            jugadores_ordenados.append(jugador)

        return jugadores_ordenados

    def _dibujar(self):
        if self.fondo:
            self.screen.blit(self.fondo, (0, 0))
        else:
            self.screen.fill((18, 24, 34))

        self._dibujar_titulo()
        self._dibujar_zona_dados()
        self._dibujar_resultados_derecha()
        self._dibujar_botones()
        self._dibujar_mensaje()

    def _dibujar_titulo(self):
        titulo = self.font_title.render(
            "Decidir orden de turnos",
            True,
            (255, 225, 95)
        )

        self.screen.blit(
            titulo,
            titulo.get_rect(center=(self.ancho // 2, int(self.alto * 0.18)))
        )

    def _dibujar_zona_dados(self):
        if self.estado == "orden_listo":
            texto_jugador = "Orden final listo"
        else:
            jugador = self.jugadores[self.indice_jugador]
            texto_jugador = f"Lanza dados: {jugador.nombre}"

        render = self.font.render(texto_jugador, True, (255, 255, 255))
        self.screen.blit(
            render,
            render.get_rect(center=(int(self.ancho * 0.32), int(self.alto * 0.34)))
        )

        total_ancho = 120 * 2 + 35
        x = int(self.ancho * 0.32) - total_ancho // 2
        y = int(self.alto * 0.42)

        self.dice.dibujar(self.screen, x, y, separacion=35)

        if self.resultado_actual:
            resultado = self.font.render(self.resultado_actual, True, (255, 230, 130))
            self.screen.blit(
                resultado,
                resultado.get_rect(center=(int(self.ancho * 0.32), int(self.alto * 0.63)))
            )

    def _dibujar_resultados_derecha(self):
        titulo = self.font.render("Resultados", True, (255, 225, 95))
        self.screen.blit(
            titulo,
            titulo.get_rect(center=(int(self.ancho * 0.70), int(self.alto * 0.34)))
        )

        resultados = self.resultados

        if self.estado == "orden_listo":
            resultados = sorted(
                self.resultados,
                key=lambda item: item["suma"],
                reverse=True
            )

        y = int(self.alto * 0.42)

        for indice, item in enumerate(resultados):
            prefijo = ""

            if self.estado == "orden_listo":
                prefijo = f"{indice + 1}. "

            linea = (
                f"{prefijo}{item['jugador'].nombre}: "
                f"{item['dado_1']} + {item['dado_2']} = {item['suma']}"
            )

            render = self.font_resultados.render(linea, True, (245, 245, 245))
            self.screen.blit(
                render,
                render.get_rect(center=(int(self.ancho * 0.70), y))
            )

            y += int(self.alto * 0.065)

    def _dibujar_botones(self):
        self._dibujar_boton_asset(
            self.boton_volver,
            self.boton_volver_img,
            "Volver"
        )

        texto = "Lanzar dados"

        if self.estado == "tirando":
            texto = "Lanzando..."

        if self.estado == "orden_listo":
            texto = "Empezar juego"

        self._dibujar_boton_asset(
            self.boton_lanzar,
            self.boton_lanzar_img,
            texto
        )

    def _dibujar_boton_asset(self, rect, imagen, texto):
        if imagen:
            self.screen.blit(imagen, rect.topleft)
        else:
            pygame.draw.rect(self.screen, (40, 130, 70), rect, border_radius=10)

        render = self.font.render(texto, True, (255, 255, 255))
        self.screen.blit(render, render.get_rect(center=rect.center))

    def _dibujar_mensaje(self):
        render = self.font_small.render(self.mensaje, True, (230, 230, 230))
        self.screen.blit(
            render,
            render.get_rect(center=(self.ancho // 2, int(self.alto * 0.76)))
        )

    def _cargar_imagen(self, path, size):
        if not path:
            return None

        try:
            imagen = pygame.image.load(path).convert_alpha()
            return pygame.transform.smoothscale(imagen, size)
        except Exception:
            return None