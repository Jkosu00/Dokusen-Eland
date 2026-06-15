import pygame

from game.dice import Dice
from game.turn_manager import TurnManager
from game.board_manager import BoardManager
from game.movement_manager import MovementManager
from models.jugador import Jugador


ANCHO = 1280
ALTO = 720

BOARD_SIZE = 720
BOARD_PATH = "assets/images/board/tablero.png"


def cargar_tablero():
    try:
        tablero = pygame.image.load(BOARD_PATH).convert()
        tablero = pygame.transform.scale(tablero, (BOARD_SIZE, BOARD_SIZE))
        return tablero
    except FileNotFoundError:
        superficie = pygame.Surface((BOARD_SIZE, BOARD_SIZE))
        superficie.fill((180, 150, 100))
        return superficie


def dibujar_texto(pantalla, texto, x, y, size=24, color=(255, 255, 255)):
    fuente = pygame.font.SysFont("arial", size, bold=True)
    render = fuente.render(texto, True, color)
    pantalla.blit(render, (x, y))


def inicializar_jugadores(board_manager):
    jugadores = [
        Jugador("Jugador 1", "", ""),
        Jugador("Jugador 2", "", ""),
        Jugador("Jugador 3", "", ""),
        Jugador("Jugador 4", "", ""),
    ]

    for i, jugador in enumerate(jugadores):
        x, y = board_manager.obtener_coordenadas_ficha(
            posicion=0,
            indice_jugador=i,
            ficha_size=36
        )

        jugador.establecer_coordenadas(x, y)

    return jugadores


def dibujar_jugadores(pantalla, jugadores, movement_manager):
    colores = [
        (255, 80, 80),
        (80, 160, 255),
        (80, 220, 120),
        (255, 220, 80),
    ]

    for i, jugador in enumerate(jugadores):
        x, y = movement_manager.obtener_posicion_con_efecto_barco(jugador)

        color = colores[i % len(colores)]

        # Ficha temporal como círculo
        pygame.draw.circle(pantalla, color, (x + 18, y + 18), 18)
        pygame.draw.circle(pantalla, (20, 20, 20), (x + 18, y + 18), 18, 2)

        # Número del jugador
        dibujar_texto(
            pantalla,
            str(i + 1),
            x + 10,
            y + 2,
            size=20,
            color=(0, 0, 0)
        )


def main():
    pygame.init()

    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Prueba visual - Dados, turnos, tablero y movimiento")

    reloj = pygame.time.Clock()

    tablero = cargar_tablero()

    dice = Dice(size=(72, 72))

    board_manager = BoardManager(
        board_x=0,
        board_y=0,
        board_size=BOARD_SIZE
    )

    movement_manager = MovementManager(
        board_manager=board_manager,
        velocidad=260
    )

    jugadores = inicializar_jugadores(board_manager)

    turn_manager = TurnManager(jugadores, dice)
    turn_manager.definir_orden_inicial()

    mensaje = "Presiona ESPACIO para lanzar dados"
    detalle_casilla = ""
    estado = "esperando_lanzamiento"

    dado_1 = 0
    dado_2 = 0
    suma = 0

    running = True

    while running:
        dt = reloj.tick(60) / 1000

        pantalla.fill((25, 25, 35))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if estado == "esperando_lanzamiento" and not dice.esta_animando() and not movement_manager.esta_moviendose():
                        dice.iniciar_lanzamiento()
                        estado = "animando_dados"
                        mensaje = "Lanzando dados..."
                        detalle_casilla = ""

        dice.actualizar()
        movement_manager.actualizar(dt)

        # Cuando termina la animación de dados, iniciar movimiento
        if estado == "animando_dados" and not dice.esta_animando():
            dado_1, dado_2, suma = dice.obtener_resultados()
            turn_manager.registrar_resultado_dados(dado_1, dado_2)

            jugador_actual = turn_manager.obtener_jugador_actual()

            mensaje = f"{jugador_actual.nombre} sacó {dado_1} + {dado_2} = {suma}"
            detalle_casilla = "Moviendo ficha..."

            movement_manager.iniciar_movimiento(
                jugador=jugador_actual,
                pasos=suma,
                indice_jugador=turn_manager.indice_turno_actual,
                ficha_size=36
            )

            estado = "moviendo_ficha"

        # Cuando termina el movimiento, detectar casilla
        if estado == "moviendo_ficha" and not movement_manager.esta_moviendose():
            casilla_final = movement_manager.obtener_ultima_casilla_final()
            jugador_actual = turn_manager.obtener_jugador_actual()

            if casilla_final:
                detalle_casilla = (
                    f"{jugador_actual.nombre} cayó en "
                    f"{casilla_final.nombre} ({casilla_final.tipo})"
                )

                print(detalle_casilla)

                movement_manager.limpiar_ultima_casilla()

            turn_manager.siguiente_turno()
            estado = "esperando_lanzamiento"

        # Dibujar tablero
        pantalla.blit(tablero, (0, 0))

        # Dibujar jugadores
        dibujar_jugadores(pantalla, jugadores, movement_manager)

        # Panel derecho
        pygame.draw.rect(pantalla, (35, 35, 45), (720, 0, 560, 720))

        jugador_actual = turn_manager.obtener_jugador_actual()

        dibujar_texto(pantalla, "PRUEBA GRAFICA", 760, 30, 32)
        dibujar_texto(pantalla, f"Ronda: {turn_manager.turno_numero}", 760, 90, 24)

        if jugador_actual:
            dibujar_texto(pantalla, f"Turno actual: {jugador_actual.nombre}", 760, 125, 24)

        dibujar_texto(pantalla, "Dados:", 760, 190, 24)
        dice.dibujar(pantalla, 760, 230, separacion=20)

        dibujar_texto(pantalla, mensaje, 760, 340, 22)
        dibujar_texto(pantalla, detalle_casilla, 760, 375, 18)

        dibujar_texto(pantalla, "Orden de jugadores:", 760, 440, 24)

        y = 480
        for jugador in turn_manager.obtener_orden_jugadores():
            dibujar_texto(
                pantalla,
                f"{jugador.orden_turno}. {jugador.nombre} | Pos: {jugador.posicion}",
                780,
                y,
                20
            )
            y += 35

        dibujar_texto(
            pantalla,
            "ESPACIO = lanzar dados",
            760,
            660,
            22,
            color=(255, 220, 90)
        )

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()