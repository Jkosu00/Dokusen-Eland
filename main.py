from game.game_manager import GameManager
from models.jugador import Jugador


def main():
    jugadores = [
        Jugador(
            nombre="Jugador 1",
            ruta_imagen="assets/images/players/avatar_1.png",
            ruta_ficha="assets/images/players/barco_1.png"
        ),
        Jugador(
            nombre="Jugador 2",
            ruta_imagen="assets/images/players/avatar_1.png",
            ruta_ficha="assets/images/players/barco_1.png"
        ),
        Jugador(
            nombre="Jugador 3",
            ruta_imagen="assets/images/players/avatar_1.png",
            ruta_ficha="assets/images/players/barco_1.png"
        ),
        Jugador(
            nombre="Jugador 4",
            ruta_imagen="assets/images/players/avatar_1.png",
            ruta_ficha="assets/images/players/barco_1.png"
        ),
    ]

    game_manager = GameManager(jugadores)
    game_manager.run()


if __name__ == "__main__":
    main()