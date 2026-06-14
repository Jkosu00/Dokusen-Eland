from game.game_manager import GameManager
from models.jugador import Jugador


def main():
    jugadores = [
        Jugador(
            nombre="Jugador 1",
            ruta_imagen="assets/images/players/Fichas/ficha_brook.png",
            ruta_ficha="assets/images/players/Barcos/barco_brook.png",
            ruta_carta="assets/images/players/Cards/brook_card.png"
        ),
        Jugador(
            nombre="Jugador 2",
            ruta_imagen="assets/images/players/Fichas/ficha_sanji.png",
            ruta_ficha="assets/images/players/Barcos/barco_sanji.png",
            ruta_carta="assets/images/players/Cards/sanji_card.png"
        ),
        Jugador(
            nombre="Jugador 3",
            ruta_imagen="assets/images/players/Fichas/ficha_zoro.png",
            ruta_ficha="assets/images/players/Barcos/barco_zoro.png",
            ruta_carta="assets/images/players/Cards/zoro_card.png"
        ),
        Jugador(
            nombre="Jugador 4",
            ruta_imagen="assets/images/players/Fichas/ficha_nami.png",
            ruta_ficha="assets/images/players/Barcos/barco_nami.png",
            ruta_carta="assets/images/players/Cards/nami_card.png"
        ),
    ]

    game_manager = GameManager(jugadores, ventana_completa=True)
    game_manager.run()


if __name__ == "__main__":
    main()