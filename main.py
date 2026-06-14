import pygame
import sys
import ctypes

from models.jugador import Jugador
from game.game_manager import GameManager
from ui.screens.start_screen import StartScreen
from ui.screens.character_selection_screen import CharacterSelectionScreen


PERSONAJES = [
    {
        "nombre": "Brook",
        "banner": "assets/images/players/banners/banner_brook.png",
        "imagen": "assets/images/players/Fichas/ficha_brook.png",
        "barco": "assets/images/players/Barcos/barco_brook.png",
        "card": "assets/images/players/Cards/brook_card.png"
    },
    {
        "nombre": "Chopper",
        "banner": "assets/images/players/banners/banner_chopper.png",
        "imagen": "assets/images/players/Fichas/ficha_chopper.png",
        "barco": "assets/images/players/Barcos/barco_chopper.png",
        "card": "assets/images/players/Cards/chopper_card.png"
    },
    {
        "nombre": "Luffy",
        "banner": "assets/images/players/banners/banner_luffy.png",
        "imagen": "assets/images/players/Fichas/ficha_luffy.png",
        "barco": "assets/images/players/Barcos/barco_luffy.png",
        "card": "assets/images/players/Cards/luffy_card.png"
    },
    {
        "nombre": "Nami",
        "banner": "assets/images/players/banners/banner_nami.png",
        "imagen": "assets/images/players/Fichas/ficha_nami.png",
        "barco": "assets/images/players/Barcos/barco_nami.png",
        "card": "assets/images/players/Cards/nami_card.png"
    },
    {
        "nombre": "Sanji",
        "banner": "assets/images/players/banners/banner_sanji.png",
        "imagen": "assets/images/players/Fichas/ficha_sanji.png",
        "barco": "assets/images/players/Barcos/barco_sanji.png",
        "card": "assets/images/players/Cards/sanji_card.png"
    },
    {
        "nombre": "Usopp",
        "banner": "assets/images/players/banners/banner_usopp.png",
        "imagen": "assets/images/players/Fichas/ficha_usopp.png",
        "barco": "assets/images/players/Barcos/barco_usopp.png",
        "card": "assets/images/players/Cards/usopp_card.png"
    },
    {
        "nombre": "Zoro",
        "banner": "assets/images/players/banners/banner_zoro.png",
        "imagen": "assets/images/players/Fichas/ficha_zoro.png",
        "barco": "assets/images/players/Barcos/barco_zoro.png",
        "card": "assets/images/players/Cards/zoro_card.png"
    },
]


def crear_jugadores(configuraciones):
    jugadores = []

    for config in configuraciones:
        personaje = config["personaje"]

        jugador = Jugador(
            nombre=config["nombre"],
            ruta_imagen=personaje["imagen"],
            ruta_ficha=personaje["barco"],
            ruta_carta=personaje["card"]
        )

        jugadores.append(jugador)

    return jugadores


def maximizar_ventana():
    try:
        hwnd = pygame.display.get_wm_info()["window"]
        ctypes.windll.user32.ShowWindow(hwnd, 3)
    except Exception:
        pass


def iniciar_musica_menu():
    if not pygame.mixer.get_init():
        pygame.mixer.init()

    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.load("assets/sounds/music/Bink-Sake-Instrumental.mp3")
        pygame.mixer.music.set_volume(0.45)
        pygame.mixer.music.play(-1)

def main():
    pygame.init()

    info = pygame.display.Info()
    screen = pygame.display.set_mode(
        (info.current_w, info.current_h),
        pygame.RESIZABLE
    )

    pygame.display.set_caption("Monopoly One Piece")
    maximizar_ventana()
    iniciar_musica_menu()

    while True:
        start_screen = StartScreen(screen)
        resultado = start_screen.run()

        print("Resultado:", resultado)

        if resultado != "jugar":
            pygame.quit()
            sys.exit()

        selector = CharacterSelectionScreen(
            screen=screen,
            personajes=PERSONAJES,
            cantidad_jugadores=4,
            fondo_path="assets/images/UI_Eventos/Select_Background.png"
        )

        configuraciones = selector.run()

        if configuraciones is None:
            continue

        jugadores = crear_jugadores(configuraciones)
        pygame.mixer.music.stop()
        game_manager = GameManager(
            jugadores=jugadores,
            ancho=1280,
            alto=720,
            ventana_completa=False
        )
        maximizar_ventana()
        game_manager.run()


if __name__ == "__main__":
    main()