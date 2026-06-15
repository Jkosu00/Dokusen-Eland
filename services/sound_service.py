import os
import pygame


class SoundService:
    def __init__(self, base_path="assets/sounds"):
        self.base_path = base_path
        self.music_volume = 0.18
        self.effect_volume = 0.75
        self.effects = {}

        if not pygame.mixer.get_init():
            pygame.mixer.init()

        self.music_paths = {
            "menu": os.path.join(base_path, "music", "menu_inicio.mp3"),
            "tablero": os.path.join(base_path, "music", "musica_tablero.mp3"),
        }

        self.effect_paths = {
            "click": os.path.join(base_path, "sound_effects", "click.wav"),
            "cofre": os.path.join(base_path, "sound_effects", "cofre.mp3"),
            "compra": os.path.join(base_path, "sound_effects", "comprar_mejorar_recomprar.mp3"),
            "mejora": os.path.join(base_path, "sound_effects", "comprar_mejorar_recomprar.mp3"),
            "recompra": os.path.join(base_path, "sound_effects", "comprar_mejorar_recomprar.mp3"),
            "yonkou": os.path.join(base_path, "sound_effects", "consigues yonkou.mp3"),
            "dinero": os.path.join(base_path, "sound_effects", "consigues_dinero.mp3"),
            "dados": os.path.join(base_path, "sound_effects", "dados.mp3"),
            "den_den_mushi": os.path.join(base_path, "sound_effects", "den-den-mushi.mp3"),
            "destruir": os.path.join(base_path, "sound_effects", "destuir_propiedad_venderla.mp3"),
            "evento_bueno": os.path.join(base_path, "sound_effects", "evento_bueno.mp3"),
            "evento_malo": os.path.join(base_path, "sound_effects", "evento_malo.mp3"),
            "victoria": os.path.join(base_path, "sound_effects", "pantalla_victoria.mp3"),
            "perder_dinero": os.path.join(base_path, "sound_effects", "perder_dinero.mp3"),
            "prision": os.path.join(base_path, "sound_effects", "prision.mp3"),
        }

        self._cargar_efectos()

    def _cargar_efectos(self):
        for nombre, ruta in self.effect_paths.items():
            if os.path.exists(ruta):
                sonido = pygame.mixer.Sound(ruta)
                sonido.set_volume(self.effect_volume)
                self.effects[nombre] = sonido

    def play_music(self, nombre, loops=-1):
        ruta = self.music_paths.get(nombre)

        if not ruta or not os.path.exists(ruta):
            return

        pygame.mixer.music.load(ruta)
        pygame.mixer.music.set_volume(self.music_volume)
        pygame.mixer.music.play(loops)

    def stop_music(self):
        pygame.mixer.music.stop()

    def play_effect(self, nombre):
        sonido = self.effects.get(nombre)

        if sonido:
            sonido.play()