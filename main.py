from game.game_manager import GameManager
from models.jugador import Jugador


def main():
    jugadores = [
        Jugador(
            nombre="Jugador 1",
            ruta_imagen="assets/images/players/Fichas/ficha_brook.png",
            ruta_ficha="assets/images/players/Barcos/barco_brook.png"
        ),
        Jugador(
            nombre="Jugador 2",
            ruta_imagen="assets/images/players/Fichas/ficha_sanji.png",
            ruta_ficha="assets/images/players/Barcos/barco_sanji.png"
        ),
        Jugador(
            nombre="Jugador 3",
            ruta_imagen="assets/images/players/Fichas/ficha_zoro.png",
            ruta_ficha="assets/images/players/Barcos/barco_zoro.png"
        ),
        Jugador(
            nombre="Jugador 4",
            ruta_imagen="assets/images/players/Fichas/ficha_nami.png",
            ruta_ficha="assets/images/players/Barcos/barco_nami.png"
        ),
    ]

    game_manager = GameManager(jugadores, ventana_completa=True)
    game_manager.run()


if __name__ == "__main__":
    main()