import random
from pathlib import Path

import pygame # type: ignore


class Dice:
    def __init__(
        self,
        faces_dir="assets/images/dice/faces",
        animation_dir="assets/images/dice/animation",
        size=(64, 64),
        animation_duration=900
    ):
        self.faces_dir = Path(faces_dir)
        self.animation_dir = Path(animation_dir)

        self.size = size
        self.animation_duration = animation_duration  # milisegundos

        self.resultado_1 = 1
        self.resultado_2 = 1

        self.animando = False
        self.tiempo_inicio_animacion = 0
        self.frame_actual = 0

        self.caras = self._cargar_caras()
        self.frames_animacion = self._cargar_frames_animacion()

    def _cargar_imagen(self, path, texto_fallback="?", color=(230, 230, 230)):
        """
        Carga una imagen. Si no existe, crea una imagen simple temporal.
        Esto sirve para que el juego no se rompa mientras aún no tienes assets finales.
        """
        if path.exists():
            imagen = pygame.image.load(str(path)).convert_alpha()
            imagen = pygame.transform.scale(imagen, self.size)
            return imagen

        # Imagen temporal si falta el asset
        superficie = pygame.Surface(self.size, pygame.SRCALPHA)
        superficie.fill(color)

        pygame.draw.rect(
            superficie,
            (40, 40, 40),
            superficie.get_rect(),
            width=2,
            border_radius=8
        )

        fuente = pygame.font.SysFont("arial", 28, bold=True)
        texto = fuente.render(str(texto_fallback), True, (20, 20, 20))
        texto_rect = texto.get_rect(center=superficie.get_rect().center)
        superficie.blit(texto, texto_rect)

        return superficie

    def _cargar_caras(self):
        """
        Carga las 6 caras finales del dado.
        Los archivos deben llamarse:
        dado_1.png, dado_2.png, dado_3.png, dado_4.png, dado_5.png, dado_6.png
        """
        caras = {}

        for numero in range(1, 7):
            ruta = self.faces_dir / f"dado_{numero}.png"
            caras[numero] = self._cargar_imagen(
                ruta,
                texto_fallback=numero,
                color=(245, 245, 245)
            )

        return caras

    def _cargar_frames_animacion(self):
        """
        Carga los sprites de animación del dado.
        Se recomienda usar nombres como:
        dado_anim_1.png, dado_anim_2.png, dado_anim_3.png...
        """
        frames = []

        if self.animation_dir.exists():
            archivos = sorted(self.animation_dir.glob("*.png"))

            for archivo in archivos:
                imagen = pygame.image.load(str(archivo)).convert_alpha()
                imagen = pygame.transform.scale(imagen, self.size)
                frames.append(imagen)

        # Si no hay sprites de animación, usa imágenes temporales
        if not frames:
            for i in range(1, 5):
                frames.append(
                    self._cargar_imagen(
                        self.animation_dir / f"dado_frame_{i}.png",
                        texto_fallback="?",
                        color=(210, 210, 210)
                    )
                )

        return frames

    def lanzar_directo(self):
        """
        Lanza los dados sin animación.
        Útil para definir el orden inicial de turnos.
        """
        self.resultado_1 = random.randint(1, 6)
        self.resultado_2 = random.randint(1, 6)

        return self.resultado_1, self.resultado_2, self.obtener_suma()

    def iniciar_lanzamiento(self):
        """
        Inicia la animación de lanzamiento.
        El resultado se genera desde el inicio, pero se muestra hasta que termina la animación.
        """
        if self.animando:
            return False

        self.resultado_1 = random.randint(1, 6)
        self.resultado_2 = random.randint(1, 6)

        self.animando = True
        self.tiempo_inicio_animacion = pygame.time.get_ticks()
        self.frame_actual = 0

        return True

    def actualizar(self):
        """
        Actualiza la animación de los dados.
        Debe llamarse en cada vuelta del game loop.
        """
        if not self.animando:
            return

        tiempo_actual = pygame.time.get_ticks()
        tiempo_transcurrido = tiempo_actual - self.tiempo_inicio_animacion

        if tiempo_transcurrido >= self.animation_duration:
            self.animando = False
            return

        velocidad_frame = 100  # cada cuántos ms cambia de frame
        self.frame_actual = (tiempo_transcurrido // velocidad_frame) % len(self.frames_animacion)

    def dibujar(self, pantalla, x, y, separacion=20):
        """
        Dibuja los dos dados en pantalla.
        Mientras animan, muestra los frames de animación.
        Al terminar, muestra la cara real de cada dado.
        """
        if self.animando:
            imagen_1 = self.frames_animacion[self.frame_actual]
            imagen_2 = self.frames_animacion[(self.frame_actual + 1) % len(self.frames_animacion)]
        else:
            imagen_1 = self.caras[self.resultado_1]
            imagen_2 = self.caras[self.resultado_2]

        pantalla.blit(imagen_1, (x, y))
        pantalla.blit(imagen_2, (x + self.size[0] + separacion, y))

    def obtener_resultados(self):
        """
        Devuelve los dos dados y la suma.
        """
        return self.resultado_1, self.resultado_2, self.obtener_suma()

    def obtener_suma(self):
        return self.resultado_1 + self.resultado_2

    def esta_animando(self):
        return self.animando