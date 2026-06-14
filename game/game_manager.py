import os
import pygame

from game.dice import Dice
from game.turn_manager import TurnManager
from game.board_manager import BoardManager
from game.movement_manager import MovementManager
from game.cell_resolver import CellResolver


class GameManager:
    def __init__(
        self,
        jugadores,
        ancho=1280,
        alto=720,
        board_size=None,
        board_path="assets/images/board/tablero.png",
        background_path="assets/images/board/fondo.png",
        ventana_completa=True
    ):
        pygame.init()

        self.board_path = board_path
        self.background_path = background_path

        if ventana_completa:
            info = pygame.display.Info()
            self.ancho = info.current_w
            self.alto = info.current_h

            # Ventana sin bordes, ocupa toda la pantalla, pero NO es fullscreen real
            self.pantalla = pygame.display.set_mode(
                (self.ancho, self.alto),
                pygame.NOFRAME
            )
        else:
            self.ancho = ancho
            self.alto = alto

            self.pantalla = pygame.display.set_mode(
                (self.ancho, self.alto),
                pygame.RESIZABLE
            )

        pygame.display.set_caption("Dokusen Eland - Ruta del Rey Pirata")

        self.reloj = pygame.time.Clock()
        self.running = True

        self.jugadores = jugadores

        if board_size is None:
            self.board_size = self._calcular_tamano_tablero()
        else:
            self.board_size = board_size

        self.board_x = (self.ancho - self.board_size) // 2
        self.board_y = (self.alto - self.board_size) // 2

        self.dice = Dice(size=(72, 72))

        self.board_manager = BoardManager(
            board_x=self.board_x,
            board_y=self.board_y,
            board_size=self.board_size
        )

        self.movement_manager = MovementManager(
            board_manager=self.board_manager,
            velocidad=260
        )

        self.turn_manager = TurnManager(
            jugadores=self.jugadores,
            dice=self.dice
        )

        self.cell_resolver = CellResolver()

        self.estado = "esperando_lanzamiento"

        self.mensaje = "Presiona ESPACIO para lanzar los dados"
        self.detalle_casilla = ""

        self.dado_1 = 0
        self.dado_2 = 0
        self.suma_dados = 0

        self.fondo = self._cargar_fondo()
        self.tablero = self._cargar_tablero()

        self._preparar_jugadores()
        self._definir_orden_inicial()

    def _calcular_tamano_tablero(self):
        """
        Calcula el tamaño del tablero para que se vea grande,
        centrado y sin salirse de la pantalla.
        """

        margen_superior = 10
        margen_inferior = 10
        margen_lateral = 10

        espacio_horizontal = self.ancho - (margen_lateral * 2)
        espacio_vertical = self.alto - margen_superior - margen_inferior

        board_size = min(espacio_horizontal, espacio_vertical)

        return int(board_size)

    def _cargar_imagen_segura(self, path, size=None, usar_alpha=False):
        """
        Carga una imagen si existe.
        Si no existe, devuelve None.
        """

        if not path or not os.path.exists(path):
            return None

        if usar_alpha:
            imagen = pygame.image.load(path).convert_alpha()
        else:
            imagen = pygame.image.load(path).convert()

        if size:
            imagen = pygame.transform.smoothscale(imagen, size)

        return imagen
    
    

    def _cargar_fondo(self):
        """
        Carga el fondo completo de pantalla.
        Si no existe, crea un fondo temporal.
        """

        fondo = self._cargar_imagen_segura(
            self.background_path,
            size=(self.ancho, self.alto),
            usar_alpha=False
        )

        if fondo:
            return fondo

        fondo_temporal = pygame.Surface((self.ancho, self.alto))
        fondo_temporal.fill((18, 28, 45))

        return fondo_temporal

    def _cargar_tablero(self):
        """
        Carga el tablero centrado.
        Si no existe, crea un tablero temporal.
        """

        tablero = self._cargar_imagen_segura(
            self.board_path,
            size=(self.board_size, self.board_size),
            usar_alpha=False
        )

        if tablero:
            return tablero

        tablero_temporal = pygame.Surface((self.board_size, self.board_size))
        tablero_temporal.fill((180, 150, 100))

        return tablero_temporal

    def _preparar_jugadores(self):
        """
        Coloca los jugadores en la casilla de salida y carga sus imágenes si existen.
        """

        for i, jugador in enumerate(self.jugadores):
            x, y = self.board_manager.obtener_coordenadas_ficha(
                posicion=0,
                indice_jugador=i,
                ficha_size=64
            )

            jugador.establecer_coordenadas(x, y)
            jugador.posicion = 0

            imagen = self._cargar_imagen_segura(
                getattr(jugador, "ruta_imagen", ""),
                size=(64, 64),
                usar_alpha=True
            )

            ficha = self._cargar_imagen_segura(
                getattr(jugador, "ruta_ficha", ""),
                size=(64, 64),
                usar_alpha=True
            )

            jugador.imagen = imagen
            jugador.ficha = ficha

            if ficha:
                jugador.rect = ficha.get_rect()
                jugador.rect.topleft = (jugador.x, jugador.y)

    def _definir_orden_inicial(self):
        """
        Lanza dados para definir el orden inicial.
        """

        resultados = self.turn_manager.definir_orden_inicial()

        print("\n=== ORDEN INICIAL ===")

        for item in resultados:
            jugador = item["jugador"]

            print(
                f"{jugador.nombre}: "
                f"{item['dado_1']} + {item['dado_2']} = {item['suma']}"
            )

        print("\n=== ORDEN FINAL ===")

        for jugador in self.turn_manager.obtener_orden_jugadores():
            print(f"Orden {jugador.orden_turno}: {jugador.nombre}")

    def run(self):
        """
        Loop principal del juego.
        """

        while self.running:
            dt = self.reloj.tick(60) / 1000

            self._manejar_eventos()
            self._actualizar(dt)
            self._dibujar()

        pygame.quit()

    def _manejar_eventos(self):
        """
        Maneja teclado, mouse y cierre de ventana.
        """

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                if event.key == pygame.K_SPACE:
                    self._intentar_lanzar_dados()

    def _intentar_lanzar_dados(self):
        """
        Inicia el lanzamiento de dados solo si el juego está listo.
        """

        if self.estado != "esperando_lanzamiento":
            return

        if self.dice.esta_animando():
            return

        if self.movement_manager.esta_moviendose():
            return

        jugador_actual = self.turn_manager.obtener_jugador_actual()

        self.dice.iniciar_lanzamiento()

        self.estado = "animando_dados"
        self.mensaje = f"{jugador_actual.nombre} está lanzando los dados..."
        self.detalle_casilla = ""

    def _actualizar(self, dt):
        """
        Actualiza dados, movimiento y estados del juego.
        """

        self.dice.actualizar()
        self.movement_manager.actualizar(dt)

        if self.estado == "animando_dados":
            self._actualizar_animacion_dados()

        elif self.estado == "moviendo_ficha":
            self._actualizar_movimiento_ficha()

    def _actualizar_animacion_dados(self):
        """
        Cuando termina la animación de dados, inicia el movimiento.
        """

        if self.dice.esta_animando():
            return

        self.dado_1, self.dado_2, self.suma_dados = self.dice.obtener_resultados()

        self.turn_manager.registrar_resultado_dados(
            self.dado_1,
            self.dado_2
        )

        jugador_actual = self.turn_manager.obtener_jugador_actual()

        self.mensaje = (
            f"{jugador_actual.nombre} sacó "
            f"{self.dado_1} + {self.dado_2} = {self.suma_dados}"
        )

        self.detalle_casilla = "Moviendo ficha..."

        self.movement_manager.iniciar_movimiento(
            jugador=jugador_actual,
            pasos=self.suma_dados,
            indice_jugador=self.turn_manager.indice_turno_actual,
            ficha_size=64
        )

        self.estado = "moviendo_ficha"

    def _actualizar_movimiento_ficha(self):
        """
        Cuando termina el movimiento, resuelve la casilla.
        """

        if self.movement_manager.esta_moviendose():
            return

        casilla_final = self.movement_manager.obtener_ultima_casilla_final()
        jugador_actual = self.turn_manager.obtener_jugador_actual()

        if casilla_final:
            resultado = self.cell_resolver.resolver_casilla(
                jugador_actual,
                casilla_final
            )

            self.detalle_casilla = resultado["mensaje"]

            self.movement_manager.limpiar_ultima_casilla()

        self.turn_manager.siguiente_turno()
        self.estado = "esperando_lanzamiento"

    def _dibujar(self):
        """
        Dibuja todo en pantalla.
        """

        self.pantalla.blit(self.fondo, (0, 0))
        self.pantalla.blit(self.tablero, (self.board_x, self.board_y))

        self._dibujar_jugadores()
        self._dibujar_paneles_jugadores()
        self._dibujar_dados_centro()
        self._dibujar_msgbox()

        pygame.display.flip()

    def _dibujar_jugadores(self):
        """
        Dibuja las fichas dentro del tablero.
        Si hay asset, dibuja el barco.
        Si no hay asset, dibuja un círculo temporal.
        """

        colores = [
            (255, 80, 80),
            (80, 190, 60),
            (80, 160, 255),
            (255, 220, 80),
        ]

        for i, jugador in enumerate(self.jugadores):
            x, y = self.movement_manager.obtener_posicion_con_efecto_barco(jugador)

            if getattr(jugador, "ficha", None):
                self.pantalla.blit(jugador.ficha, (x, y))
            else:
                color = colores[i % len(colores)]

                pygame.draw.circle(
                    self.pantalla,
                    color,
                    (int(x) + 24, int(y) + 24),
                    22
                )

                pygame.draw.circle(
                    self.pantalla,
                    (20, 20, 20),
                    (int(x) + 24, int(y) + 24),
                    22,
                    2
                )

                self._dibujar_texto(
                    str(i + 1),
                    int(x) + 16,
                    int(y) + 8,
                    size=22,
                    color=(0, 0, 0)
                )

    def _dibujar_paneles_jugadores(self):
        """
        Dibuja los 4 jugadores en las esquinas de la pantalla.
        """

        posiciones_paneles = [
            (25, 25),
            (self.ancho - 305, 25),
            (25, self.alto - 105),
            (self.ancho - 305, self.alto - 105)
        ]

        colores = [
            (220, 40, 30),
            (80, 190, 60),
            (220, 40, 30),
            (220, 40, 30)
        ]

        for i, jugador in enumerate(self.jugadores):
            x, y = posiciones_paneles[i]
            color = colores[i % len(colores)]

            es_turno = jugador == self.turn_manager.obtener_jugador_actual()

            self._dibujar_panel_jugador(
                jugador=jugador,
                x=x,
                y=y,
                color=color,
                es_turno=es_turno
            )

    def _dibujar_panel_jugador(self, jugador, x, y, color, es_turno=False):
        """
        Dibuja una tarjeta pequeña de jugador.
        """

        ancho_panel = 280
        alto_panel = 80

        if es_turno:
            borde_color = (255, 230, 90)
            borde_width = 4
        else:
            borde_color = (25, 25, 25)
            borde_width = 2

        pygame.draw.rect(
            self.pantalla,
            color,
            (x, y, ancho_panel, alto_panel),
            border_radius=18
        )

        pygame.draw.rect(
            self.pantalla,
            borde_color,
            (x, y, ancho_panel, alto_panel),
            width=borde_width,
            border_radius=18
        )

        pygame.draw.circle(
            self.pantalla,
            (240, 220, 120),
            (x + 40, y + 40),
            32
        )

        pygame.draw.circle(
            self.pantalla,
            (30, 30, 30),
            (x + 40, y + 40),
            32,
            3
        )

        if getattr(jugador, "imagen", None):
            imagen_rect = jugador.imagen.get_rect(center=(x + 40, y + 40))
            self.pantalla.blit(jugador.imagen, imagen_rect)
        else:
            self._dibujar_texto(
                jugador.nombre[0].upper(),
                x + 28,
                y + 20,
                size=28,
                color=(30, 30, 30)
            )

        self._dibujar_texto(
            jugador.nombre,
            x + 90,
            y + 10,
            size=18,
            color=(20, 20, 20)
        )

        pygame.draw.rect(
            self.pantalla,
            (20, 20, 25),
            (x + 90, y + 38, 165, 28),
            border_radius=12
        )

        self._dibujar_texto(
            f"${jugador.dinero}",
            x + 105,
            y + 42,
            size=15,
            color=(255, 255, 255)
        )

    def _dibujar_dados_centro(self):
        """
        Dibuja los dados en el centro del tablero, sin fondo.
        """

        centro_x = self.board_x + self.board_size // 2
        centro_y = self.board_y + self.board_size // 2

        dado_ancho = 72
        separacion = 20
        total_ancho = dado_ancho * 2 + separacion

        x = centro_x - total_ancho // 2
        y = centro_y - 45

        self.dice.dibujar(
            self.pantalla,
            x,
            y,
            separacion=separacion
        )

    def _dibujar_msgbox(self):
        """
        Dibuja un cuadro pequeño de mensaje debajo del tablero,
        sin tapar las casillas.
        """

        ancho_box = 520
        alto_box = 46

        x = (self.ancho - ancho_box) // 2

        # Se coloca justo debajo del tablero
        y = self.board_y + self.board_size + 8

        # Seguridad por si el tablero cambia de tamaño
        if y + alto_box > self.alto:
            y = self.alto - alto_box - 8

        pygame.draw.rect(
            self.pantalla,
            (20, 20, 28),
            (x, y, ancho_box, alto_box),
            border_radius=14
        )

        pygame.draw.rect(
            self.pantalla,
            (230, 190, 80),
            (x, y, ancho_box, alto_box),
            width=2,
            border_radius=14
        )

        texto = self.mensaje

        if self.detalle_casilla:
            texto = f"{self.mensaje} | {self.detalle_casilla}"

        self._dibujar_texto(
            texto,
            x + 15,
            y + 13,
            size=15,
            color=(255, 255, 255)
        )

    def _dibujar_texto(self, texto, x, y, size=24, color=(255, 255, 255)):
        """
        Dibuja texto simple en pantalla.
        """

        fuente = pygame.font.SysFont("arial", size, bold=True)
        render = fuente.render(str(texto), True, color)
        self.pantalla.blit(render, (x, y))