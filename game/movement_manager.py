import math
import pygame


class MovementManager:
    def __init__(self, board_manager, velocidad=260):
        self.board_manager = board_manager
        self.velocidad = velocidad  # pixeles por segundo

        self.jugador = None
        self.ruta = []
        self.indice_ruta = 0

        self.moviendose = False
        self.posicion_final = None
        self.casilla_final = None

        self.ultima_casilla_final = None

    def iniciar_movimiento(self, jugador, pasos, indice_jugador=0, ficha_size=48):
        """
        Inicia el movimiento animado del jugador.
        No cambia la posicion lógica hasta que termina la animación.
        """

        if self.moviendose:
            return False

        self.jugador = jugador

        self.ruta = self.board_manager.obtener_ruta_movimiento(
            posicion_actual=jugador.posicion,
            pasos=pasos,
            indice_jugador=indice_jugador,
            ficha_size=ficha_size
        )

        if not self.ruta:
            return False

        self.indice_ruta = 0
        self.moviendose = True

        self.posicion_final = self.board_manager.calcular_nueva_posicion(
            jugador.posicion,
            pasos
        )

        self.casilla_final = self.board_manager.obtener_casilla(self.posicion_final)
        self.ultima_casilla_final = None

        return True

    def actualizar(self, dt):
        """
        Mueve al jugador poco a poco hacia el siguiente punto de la ruta.

        dt = tiempo en segundos desde el último frame.
        """

        if not self.moviendose or self.jugador is None:
            return

        destino = self.ruta[self.indice_ruta]

        destino_x = destino["x"]
        destino_y = destino["y"]

        dx = destino_x - self.jugador.x
        dy = destino_y - self.jugador.y

        distancia = math.sqrt(dx ** 2 + dy ** 2)

        if distancia == 0:
            self._avanzar_siguiente_punto()
            return

        avance = self.velocidad * dt

        if avance >= distancia:
            self.jugador.x = destino_x
            self.jugador.y = destino_y

            if self.jugador.rect:
                self.jugador.rect.topleft = (self.jugador.x, self.jugador.y)

            self._avanzar_siguiente_punto()
        else:
            self.jugador.x += (dx / distancia) * avance
            self.jugador.y += (dy / distancia) * avance

            if self.jugador.rect:
                self.jugador.rect.topleft = (self.jugador.x, self.jugador.y)

    def _avanzar_siguiente_punto(self):
        self.indice_ruta += 1

        if self.indice_ruta >= len(self.ruta):
            self._terminar_movimiento()

    def _terminar_movimiento(self):
        """
        Cuando termina la animación, ahora sí actualiza la posición lógica.
        """

        self.jugador.posicion = self.posicion_final
        self.ultima_casilla_final = self.casilla_final

        self.jugador = None
        self.ruta = []
        self.indice_ruta = 0
        self.moviendose = False

    def esta_moviendose(self):
        return self.moviendose

    def obtener_ultima_casilla_final(self):
        return self.ultima_casilla_final

    def limpiar_ultima_casilla(self):
        self.ultima_casilla_final = None

    def obtener_posicion_con_efecto_barco(self, jugador):
        """
        Devuelve una posición con efecto de balanceo.
        Sirve para dibujar el barco con un movimiento suave.
        """

        tiempo = pygame.time.get_ticks()

        balanceo_y = math.sin(tiempo * 0.008) * 3

        return int(jugador.x), int(jugador.y + balanceo_y)