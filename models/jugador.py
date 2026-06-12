import pygame # type: ignore

class Jugador:
    def __init__(self, nombre, ruta_imagen, ruta_ficha, dinero_inicial=1500):
        # Datos principales del jugador
        self.nombre = nombre
        self.ruta_imagen = ruta_imagen      # Imagen que identifica al jugador, por ejemplo avatar o retrato
        self.ruta_ficha = ruta_ficha        # Imagen de la ficha que se moverá en el tablero
        self.dinero = dinero_inicial

        # Posición dentro del tablero
        self.posicion = 0                   # Casilla actual, de 0 a 39
        self.posicion_anterior = 0

        # Coordenadas visuales en pantalla
        self.x = 0
        self.y = 0
        self.objetivo_x = 0
        self.objetivo_y = 0

        # Turnos
        self.orden_turno = None
        self.ultima_tirada = 0
        self.turnos_perdidos = 0
        self.activo = True

        # Estado del jugador
        self.en_carcel = False

        # Propiedades
        self.propiedades = []
        self.road_poneglyphs = []

        # Imágenes cargadas en Pygame
        self.imagen = None
        self.ficha = None
        self.rect = None

    def cargar_imagenes(self, tamaño_ficha=(48, 48), tamaño_imagen=(80, 80)):
        """
        Carga las imágenes del jugador usando las rutas guardadas.
        Esta función debe llamarse después de pygame.init().
        """

        self.imagen = pygame.image.load(self.ruta_imagen).convert_alpha()
        self.imagen = pygame.transform.scale(self.imagen, tamaño_imagen)

        self.ficha = pygame.image.load(self.ruta_ficha).convert_alpha()
        self.ficha = pygame.transform.scale(self.ficha, tamaño_ficha)

        self.rect = self.ficha.get_rect()
        self.rect.topleft = (self.x, self.y)

    def establecer_coordenadas(self, x, y):
        """
        Coloca visualmente la ficha del jugador en una coordenada del tablero.
        """
        self.x = x
        self.y = y
        self.objetivo_x = x
        self.objetivo_y = y

        if self.rect:
            self.rect.topleft = (self.x, self.y)

    def mover_a_casilla(self, nueva_posicion, nueva_x, nueva_y):
        """
        Actualiza la posición lógica y visual del jugador.
        """
        self.posicion_anterior = self.posicion
        self.posicion = nueva_posicion

        self.objetivo_x = nueva_x
        self.objetivo_y = nueva_y

        self.x = nueva_x
        self.y = nueva_y

        if self.rect:
            self.rect.topleft = (self.x, self.y)

    def sumar_dinero(self, cantidad):
        self.dinero += cantidad

    def restar_dinero(self, cantidad):
        self.dinero -= cantidad

        if self.dinero < 0:
            self.dinero = 0

    def puede_pagar(self, cantidad):
        return self.dinero >= cantidad

    def agregar_propiedad(self, propiedad):
        self.propiedades.append(propiedad)

    def quitar_propiedad(self, propiedad):
        if propiedad in self.propiedades:
            self.propiedades.remove(propiedad)

    def agregar_road_poneglyph(self, road_poneglyph):
        self.road_poneglyphs.append(road_poneglyph)

    def cantidad_road_poneglyphs(self):
        return len(self.road_poneglyphs)

    def tiene_4_road_poneglyphs(self):
        return len(self.road_poneglyphs) >= 4

    def perder_turno(self, cantidad=1):
        self.turnos_perdidos += cantidad

    def puede_jugar_turno(self):
        return self.activo and self.turnos_perdidos == 0 and not self.en_carcel

    def actualizar_turno_perdido(self):
        if self.turnos_perdidos > 0:
            self.turnos_perdidos -= 1

    def dibujar_ficha(self, pantalla):
        """
        Dibuja la ficha del jugador en pantalla.
        """
        if self.ficha:
            pantalla.blit(self.ficha, (self.x, self.y))

    def dibujar_imagen(self, pantalla, x, y):
        """
        Dibuja la imagen identificadora del jugador, por ejemplo en el panel lateral.
        """
        if self.imagen:
            pantalla.blit(self.imagen, (x, y))

    def obtener_resumen(self):
        """
        Devuelve información básica del jugador.
        Sirve para mostrar en consola, depurar o guardar datos.
        """
        return {
            "nombre": self.nombre,
            "dinero": self.dinero,
            "posicion": self.posicion,
            "orden_turno": self.orden_turno,
            "propiedades": len(self.propiedades),
            "road_poneglyphs": len(self.road_poneglyphs),
            "es_yonkou": self.es_yonkou,
            "activo": self.activo
        }

    def __str__(self):
        return f"{self.nombre} | Dinero: {self.dinero} | Posición: {self.posicion}"