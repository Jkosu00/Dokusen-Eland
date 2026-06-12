from models.casilla import (
    Casilla,
    TIPO_SALIDA,
    TIPO_ISLA,
    TIPO_EVENTO,
    TIPO_ROAD_PONEGLYPH,
    TIPO_YONKO,
    TIPO_CARCEL,
    TIPO_IMPUESTO,
    TIPO_DESCANSO
)


class BoardManager:
    def __init__(self, board_x=0, board_y=0, board_size=720, total_casillas=40):
        self.board_x = board_x
        self.board_y = board_y
        self.board_size = board_size
        self.total_casillas = total_casillas

        # En tu tablero original, las esquinas son más grandes que las casillas normales.
        self.corner_size = self.board_size * 0.125
        self.normal_cell_size = (self.board_size - (self.corner_size * 2)) / 9

        self.rects_casillas = self._crear_rects_tablero()
        self.casillas = self._crear_casillas()

    def _crear_rects_tablero(self):
        """
        Crea los rectángulos reales de las 40 casillas según el tablero subido.

        Retorna:
        {
            posicion: (x, y, ancho, alto)
        }
        """

        rects = {}

        x0 = self.board_x
        y0 = self.board_y
        size = self.board_size
        corner = self.corner_size
        normal = self.normal_cell_size

        # 0 - Salida, esquina inferior derecha
        rects[0] = (
            x0 + size - corner,
            y0 + size - corner,
            corner,
            corner
        )

        # 1 a 9 - Fila inferior, de derecha a izquierda
        for posicion in range(1, 10):
            slot_desde_izquierda = 9 - posicion

            x = x0 + corner + (slot_desde_izquierda * normal)
            y = y0 + size - corner

            rects[posicion] = (x, y, normal, corner)

        # 10 - Prisión, esquina inferior izquierda
        rects[10] = (
            x0,
            y0 + size - corner,
            corner,
            corner
        )

        # 11 a 19 - Lado izquierdo, de abajo hacia arriba
        for posicion in range(11, 20):
            slot_desde_arriba = 19 - posicion

            x = x0
            y = y0 + corner + (slot_desde_arriba * normal)

            rects[posicion] = (x, y, corner, normal)

        # 20 - Descanso, esquina superior izquierda
        rects[20] = (
            x0,
            y0,
            corner,
            corner
        )

        # 21 a 29 - Fila superior, de izquierda a derecha
        for posicion in range(21, 30):
            slot_desde_izquierda = posicion - 21

            x = x0 + corner + (slot_desde_izquierda * normal)
            y = y0

            rects[posicion] = (x, y, normal, corner)

        # 30 - Yonkō, esquina superior derecha
        rects[30] = (
            x0 + size - corner,
            y0,
            corner,
            corner
        )

        # 31 a 39 - Lado derecho, de arriba hacia abajo
        for posicion in range(31, 40):
            slot_desde_arriba = posicion - 31

            x = x0 + size - corner
            y = y0 + corner + (slot_desde_arriba * normal)

            rects[posicion] = (x, y, corner, normal)

        return rects

    def _crear_casillas(self):
        """
        Crea las 40 casillas en el orden real de tu tablero.
        """

        datos_casillas = [
            # Fila inferior: derecha a izquierda
            ("Salida", TIPO_SALIDA, None),
            ("Dawn Island", TIPO_ISLA, "dawn_island"),
            ("Shells Town", TIPO_ISLA, "shells_town"),
            ("Evento de la Marina", TIPO_EVENTO, "evento_marina"),
            ("Orange Town", TIPO_ISLA, "orange_town"),
            ("Road Poneglyph 1", TIPO_ROAD_PONEGLYPH, "road_poneglyph_1"),
            ("Villa Syrup", TIPO_ISLA, "villa_syrup"),
            ("Baratie", TIPO_ISLA, "baratie"),
            ("Cofre Recompensa", TIPO_EVENTO, "cofre_recompensa"),
            ("Conomi Island", TIPO_ISLA, "conomi_island"),

            # Esquina inferior izquierda
            ("Prisión", TIPO_CARCEL, "prision"),

            # Lado izquierdo: abajo hacia arriba
            ("Little Garden", TIPO_ISLA, "little_garden"),
            ("Drum Island", TIPO_ISLA, "drum_island"),
            ("Evento Riesgo", TIPO_EVENTO, "evento_riesgo"),
            ("Alabasta", TIPO_ISLA, "alabasta"),
            ("Road Poneglyph 2", TIPO_ROAD_PONEGLYPH, "road_poneglyph_2"),
            ("Mock Town", TIPO_ISLA, "mock_town"),
            ("Skypiea", TIPO_ISLA, "skypiea"),
            ("Cofre Recompensa", TIPO_EVENTO, "cofre_recompensa"),
            ("Water 7", TIPO_ISLA, "water_7"),

            # Esquina superior izquierda
            ("Descanso", TIPO_DESCANSO, "descanso"),

            # Fila superior: izquierda a derecha
            ("Thriller Bark", TIPO_ISLA, "thriller_bark"),
            ("Amazon Lily", TIPO_ISLA, "amazon_lily"),
            ("Cofre Recompensa", TIPO_EVENTO, "cofre_recompensa"),
            ("Marineford", TIPO_ISLA, "marineford"),
            ("Road Poneglyph 3", TIPO_ROAD_PONEGLYPH, "road_poneglyph_3"),
            ("Gyojin Island", TIPO_ISLA, "gyojin_island"),
            ("Punk Hazard", TIPO_ISLA, "punk_hazard"),
            ("Evento de la Marina", TIPO_EVENTO, "evento_marina"),
            ("Dressrosa", TIPO_ISLA, "dressrosa"),

            # Esquina superior derecha
            ("Yonkō", TIPO_YONKO, "yonko"),

            # Lado derecho: arriba hacia abajo
            ("Zou Island", TIPO_ISLA, "zou_island"),
            ("Whole Cake", TIPO_ISLA, "whole_cake"),
            ("Cofre Recompensa", TIPO_EVENTO, "cofre_recompensa"),
            ("Wano", TIPO_ISLA, "wano"),
            ("Road Poneglyph 4", TIPO_ROAD_PONEGLYPH, "road_poneglyph_4"),
            ("Egghead", TIPO_ISLA, "egghead"),
            ("Elbaf", TIPO_ISLA, "elbaf"),
            ("Evento Riesgo", TIPO_EVENTO, "evento_riesgo"),
            ("Laugh Tale", TIPO_ISLA, "laugh_tale"),
        ]

        casillas = []

        for posicion, datos in enumerate(datos_casillas):
            nombre, tipo, referencia = datos
            x, y, ancho, alto = self.rects_casillas[posicion]

            casilla = Casilla(
                id_casilla=posicion,
                nombre=nombre,
                tipo=tipo,
                posicion=posicion,
                x=int(x),
                y=int(y),
                ancho=int(ancho),
                alto=int(alto),
                referencia=referencia
            )

            casillas.append(casilla)

        return casillas

    def obtener_casilla(self, posicion):
        if posicion < 0 or posicion >= self.total_casillas:
            raise ValueError(f"La posición {posicion} no existe en el tablero.")

        return self.casillas[posicion]

    def obtener_coordenadas_casilla(self, posicion):
        casilla = self.obtener_casilla(posicion)
        return casilla.obtener_coordenadas()

    def obtener_centro_casilla(self, posicion):
        casilla = self.obtener_casilla(posicion)
        return casilla.obtener_centro()

    def obtener_coordenadas_ficha(self, posicion, indice_jugador=0, ficha_size=48):
        """
        Devuelve coordenadas para colocar una ficha dentro de una casilla.

        indice_jugador evita que las fichas queden una encima de otra.
        """

        centro_x, centro_y = self.obtener_centro_casilla(posicion)

        offset = int(self.board_size * 0.017)

        offsets = [
            (-offset, -offset),
            (offset, -offset),
            (-offset, offset),
            (offset, offset),
            (0, 0)
        ]

        offset_x, offset_y = offsets[indice_jugador % len(offsets)]

        x = centro_x - ficha_size // 2 + offset_x
        y = centro_y - ficha_size // 2 + offset_y

        return int(x), int(y)

    def calcular_nueva_posicion(self, posicion_actual, pasos):
        return (posicion_actual + pasos) % self.total_casillas

    def paso_por_salida(self, posicion_actual, pasos):
        return posicion_actual + pasos >= self.total_casillas

    def obtener_ruta_movimiento(self, posicion_actual, pasos, indice_jugador=0, ficha_size=48):
        """
        Devuelve la ruta paso por paso que seguirá la ficha.
        """

        ruta = []

        for paso in range(1, pasos + 1):
            nueva_posicion = (posicion_actual + paso) % self.total_casillas
            x, y = self.obtener_coordenadas_ficha(
                nueva_posicion,
                indice_jugador=indice_jugador,
                ficha_size=ficha_size
            )

            ruta.append({
                "posicion": nueva_posicion,
                "x": x,
                "y": y,
                "casilla": self.obtener_casilla(nueva_posicion)
            })

        return ruta

    def obtener_todas_las_casillas(self):
        return self.casillas

    def mostrar_resumen_tablero(self):
        for casilla in self.casillas:
            print(casilla)