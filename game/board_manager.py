from models.casilla import (
    Casilla,
    TIPO_SALIDA,
    TIPO_ISLA,
    TIPO_EVENTO,
    TIPO_ROAD_PONEGLYPH,
    TIPO_YONKO,
    TIPO_CARCEL,
    TIPO_DESCANSO
)


class BoardManager:
    def __init__(
        self,
        board_x=0,
        board_y=0,
        board_width=620,
        board_height=620,
        board_size=None
    ):
        """
        BoardManager adaptado a tablero de 36 casillas.

        Estructura:
        - 4 esquinas
        - 8 casillas abajo
        - 8 casillas izquierda
        - 8 casillas arriba
        - 8 casillas derecha

        Total:
        4 + 8 + 8 + 8 + 8 = 36
        """

        self.board_x = board_x
        self.board_y = board_y

        if board_size is not None:
            self.board_width = board_size
            self.board_height = board_size
        else:
            self.board_width = board_width
            self.board_height = board_height

        self.total_casillas = 36

        self.corner_ratio = 0.138

        self.corner_width = self.board_width * self.corner_ratio
        self.corner_height = self.board_height * self.corner_ratio

        self.horizontal_cells = 8
        self.vertical_cells = 8

        self.horizontal_cell_width = (
            self.board_width - (self.corner_width * 2)
        ) / self.horizontal_cells

        self.vertical_cell_height = (
            self.board_height - (self.corner_height * 2)
        ) / self.vertical_cells

        self.rects_casillas = self._crear_rects_tablero()
        self.casillas = self._crear_casillas()

    def _crear_rects_tablero(self):
        """
        Crea los rectángulos de las 36 casillas.

        Recorrido:
        0  = Salida
        1-8 = fila inferior hacia la izquierda
        9 = Prisión
        10-17 = lado izquierdo hacia arriba
        18 = Descanso
        19-26 = fila superior hacia la derecha
        27 = Yonko
        28-35 = lado derecho hacia abajo
        """

        rects = {}

        x0 = self.board_x
        y0 = self.board_y

        w = self.board_width
        h = self.board_height

        cw = self.corner_width
        ch = self.corner_height

        normal_w = self.horizontal_cell_width
        normal_h = self.vertical_cell_height

        # 0 - Salida, esquina inferior derecha
        rects[0] = (
            x0 + w - cw,
            y0 + h - ch,
            cw,
            ch
        )

        # 1 a 8 - Fila inferior, de derecha a izquierda
        for posicion in range(1, 9):
            x = x0 + w - cw - (posicion * normal_w)
            y = y0 + h - ch

            rects[posicion] = (
                x,
                y,
                normal_w,
                ch
            )

        # 9 - Prisión, esquina inferior izquierda
        rects[9] = (
            x0,
            y0 + h - ch,
            cw,
            ch
        )

        # 10 a 17 - Lado izquierdo, de abajo hacia arriba
        for posicion in range(10, 18):
            slot_desde_abajo = posicion - 9

            x = x0
            y = y0 + h - ch - (slot_desde_abajo * normal_h)

            rects[posicion] = (
                x,
                y,
                cw,
                normal_h
            )

        # 18 - Descanso, esquina superior izquierda
        rects[18] = (
            x0,
            y0,
            cw,
            ch
        )

        # 19 a 26 - Fila superior, de izquierda a derecha
        for posicion in range(19, 27):
            slot_desde_izquierda = posicion - 18

            x = x0 + cw + ((slot_desde_izquierda - 1) * normal_w)
            y = y0

            rects[posicion] = (
                x,
                y,
                normal_w,
                ch
            )

        # 27 - Yonko, esquina superior derecha
        rects[27] = (
            x0 + w - cw,
            y0,
            cw,
            ch
        )

        # 28 a 35 - Lado derecho, de arriba hacia abajo
        for posicion in range(28, 36):
            slot_desde_arriba = posicion - 27

            x = x0 + w - cw
            y = y0 + ch + ((slot_desde_arriba - 1) * normal_h)

            rects[posicion] = (
                x,
                y,
                cw,
                normal_h
            )

        return rects

    def _crear_casillas(self):
        """
        Crea las 36 casillas jugables del tablero.
        """

        datos_casillas = [
            # 0 - Esquina inferior derecha
            ("Salida", TIPO_SALIDA, "salida"),

            # 1 a 8 - Fila inferior, derecha a izquierda
            ("Dawn Island", TIPO_ISLA, "dawn_island"),
            ("Shells Town", TIPO_ISLA, "shells_town"),
            ("Cofre Recompensa", TIPO_EVENTO, "cofre_recompensa"),
            ("Orange Town", TIPO_ISLA, "orange_town"),
            ("Road Poneglyph 1", TIPO_ROAD_PONEGLYPH, "road_poneglyph_1"),
            ("Villa Syrup", TIPO_ISLA, "villa_syrup"),
            ("Baratie", TIPO_ISLA, "baratie"),
            ("Conomi Island", TIPO_ISLA, "conomi_island"),

            # 9 - Esquina inferior izquierda
            ("Prisión", TIPO_CARCEL, "prision"),

            # 10 a 17 - Lado izquierdo, abajo hacia arriba
            ("Little Garden", TIPO_ISLA, "little_garden"),
            ("Drum Island", TIPO_ISLA, "drum_island"),
            ("Evento Riesgo", TIPO_EVENTO, "evento_riesgo"),
            ("Alabasta", TIPO_ISLA, "alabasta"),
            ("Road Poneglyph 2", TIPO_ROAD_PONEGLYPH, "road_poneglyph_2"),
            ("Mock Town", TIPO_ISLA, "mock_town"),
            ("Skypiea", TIPO_ISLA, "skypiea"),
            ("Water 7", TIPO_ISLA, "water_7"),

            # 18 - Esquina superior izquierda
            ("Descanso", TIPO_DESCANSO, "descanso"),

            # 19 a 26 - Fila superior, izquierda a derecha
            ("Thriller Bark", TIPO_ISLA, "thriller_bark"),
            ("Amazon Lily", TIPO_ISLA, "amazon_lily"),
            ("Cofre Recompensa", TIPO_EVENTO, "cofre_recompensa"),
            ("Marineford", TIPO_ISLA, "marineford"),
            ("Road Poneglyph 3", TIPO_ROAD_PONEGLYPH, "road_poneglyph_3"),
            ("Gyojin Island", TIPO_ISLA, "gyojin_island"),
            ("Punk Hazard", TIPO_ISLA, "punk_hazard"),
            ("Dressrosa", TIPO_ISLA, "dressrosa"),

            # 27 - Esquina superior derecha
            ("Yonko", TIPO_YONKO, "yonko"),

            # 28 a 35 - Lado derecho, arriba hacia abajo
            ("Zou Island", TIPO_ISLA, "zou_island"),
            ("Whole Cake", TIPO_ISLA, "whole_cake"),
            ("Cofre Recompensa", TIPO_EVENTO, "cofre_recompensa"),
            ("Wano", TIPO_ISLA, "wano"),
            ("Road Poneglyph 4", TIPO_ROAD_PONEGLYPH, "road_poneglyph_4"),
            ("Egghead", TIPO_ISLA, "egghead"),
            ("Elbaf", TIPO_ISLA, "elbaf"),
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
                x=int(round(x)),
                y=int(round(y)),
                ancho=int(round(ancho)),
                alto=int(round(alto)),
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
        centro_x, centro_y = self.obtener_centro_casilla(posicion)

        offset = int(min(self.board_width, self.board_height) * 0.018)

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

        return int(round(x)), int(round(y))

    def calcular_nueva_posicion(self, posicion_actual, pasos):
        return (posicion_actual + pasos) % self.total_casillas

    def paso_por_salida(self, posicion_actual, pasos):
        return posicion_actual + pasos >= self.total_casillas

    def obtener_ruta_movimiento(
        self,
        posicion_actual,
        pasos,
        indice_jugador=0,
        ficha_size=48
    ):
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

    def mostrar_rects_tablero(self):
        for posicion, rect in self.rects_casillas.items():
            print(posicion, rect)