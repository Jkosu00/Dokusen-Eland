class TurnManager:
    def __init__(self, jugadores, dice):
        self.jugadores = jugadores
        self.dice = dice

        self.indice_turno_actual = 0
        self.turno_numero = 1

        self.orden_definido = False
        self.ultimo_dado_1 = 0
        self.ultimo_dado_2 = 0
        self.ultima_suma = 0

    def definir_orden_inicial(self):
        """
        Cada jugador lanza dos dados.
        El orden se define de mayor a menor según la suma.
        """

        resultados = []

        for jugador in self.jugadores:
            dado_1, dado_2, suma = self.dice.lanzar_directo()

            jugador.ultima_tirada = suma

            resultados.append({
                "jugador": jugador,
                "dado_1": dado_1,
                "dado_2": dado_2,
                "suma": suma
            })

        resultados.sort(key=lambda item: item["suma"], reverse=True)

        self.jugadores = []

        for indice, item in enumerate(resultados):
            jugador = item["jugador"]
            jugador.orden_turno = indice + 1
            self.jugadores.append(jugador)

        self.indice_turno_actual = 0
        self.orden_definido = True

        return resultados

    def obtener_jugador_actual(self):
        """
        Devuelve el jugador al que le toca jugar.
        """
        if not self.jugadores:
            return None

        return self.jugadores[self.indice_turno_actual]

    def lanzar_dados_turno_actual(self):
        """
        Lanza los dados para el jugador actual.
        Esta versión es lógica, sin animación.
        La animación la puedes manejar desde Dice con iniciar_lanzamiento().
        """

        jugador = self.obtener_jugador_actual()

        if jugador is None:
            return None

        dado_1, dado_2, suma = self.dice.lanzar_directo()

        self.ultimo_dado_1 = dado_1
        self.ultimo_dado_2 = dado_2
        self.ultima_suma = suma

        jugador.ultima_tirada = suma

        return dado_1, dado_2, suma

    def registrar_resultado_dados(self, dado_1, dado_2):
        """
        Sirve para cuando uses dados animados.
        Primero Dice anima, luego cuando termina,
        este método guarda el resultado dentro del TurnManager.
        """

        jugador = self.obtener_jugador_actual()

        if jugador is None:
            return None

        suma = dado_1 + dado_2

        self.ultimo_dado_1 = dado_1
        self.ultimo_dado_2 = dado_2
        self.ultima_suma = suma

        jugador.ultima_tirada = suma

        return suma

    def obtuvo_dobles(self):
        """
        Devuelve True si ambos dados tienen el mismo valor.
        """
        return self.ultimo_dado_1 == self.ultimo_dado_2

    def siguiente_turno(self):
        """
        Pasa al siguiente jugador activo.
        """

        if not self.jugadores:
            return None

        cantidad_jugadores = len(self.jugadores)

        for _ in range(cantidad_jugadores):
            self.indice_turno_actual += 1

            if self.indice_turno_actual >= cantidad_jugadores:
                self.indice_turno_actual = 0
                self.turno_numero += 1

            jugador = self.obtener_jugador_actual()

            if jugador.activo:
                return jugador

        return None

    def mantener_turno_por_dobles(self):
        """
        Si después deciden que sacar dobles permite volver a jugar,
        pueden usar este método.
        """
        return self.obtener_jugador_actual()

    def saltar_turno_actual(self):
        """
        Se usa si un jugador pierde turno.
        """
        jugador = self.obtener_jugador_actual()

        if jugador and jugador.turnos_perdidos > 0:
            jugador.actualizar_turno_perdido()
            return self.siguiente_turno()

        return jugador

    def eliminar_jugador_actual(self):
        """
        Marca al jugador actual como inactivo.
        Puede servir para bancarrota.
        """
        jugador = self.obtener_jugador_actual()

        if jugador:
            jugador.activo = False

        return self.siguiente_turno()

    def obtener_orden_jugadores(self):
        """
        Devuelve la lista de jugadores en el orden actual.
        """
        return self.jugadores

    def obtener_resumen_turno(self):
        """
        Devuelve información útil para depurar o mostrar en pantalla.
        """
        jugador = self.obtener_jugador_actual()

        return {
            "turno_numero": self.turno_numero,
            "jugador_actual": jugador.nombre if jugador else None,
            "indice_turno_actual": self.indice_turno_actual,
            "ultimo_dado_1": self.ultimo_dado_1,
            "ultimo_dado_2": self.ultimo_dado_2,
            "ultima_suma": self.ultima_suma,
            "dobles": self.obtuvo_dobles()
        }