import random


class EventRules:
    def __init__(self):
        self.recompensas = [
            {
                "titulo": "Cofre Recompensa",
                "mensaje": "Encontraste un tesoro escondido. Recibes $200.",
                "dinero": 200
            },
            {
                "titulo": "Cofre Recompensa",
                "mensaje": "Una tripulación aliada te entrega provisiones. Recibes $150.",
                "dinero": 150
            },
            {
                "titulo": "Cofre Recompensa",
                "mensaje": "Vendiste recursos encontrados en la ruta. Recibes $250.",
                "dinero": 250
            },
            {
                "titulo": "Cofre Recompensa",
                "mensaje": "Recibiste una recompensa por completar una misión. Ganas $300.",
                "dinero": 300
            }
        ]

        self.riesgos_malos = [
            {
                "tipo": "perder_dinero",
                "peso": 65
            },
            {
                "tipo": "perder_propiedad_aleatoria",
                "peso": 35
            }
        ]

        self.riesgos_buenos = [
            {
                "tipo": "destruir_propiedad",
                "peso": 30
            },
            {
                "tipo": "conseguir_yonkou",
                "peso": 35
            },
            {
                "tipo": "ganar_dinero",
                "peso": 35
            }
        ]

    # ============================================================
    # ENTRADA PRINCIPAL
    # ============================================================

    def ejecutar_evento(self, jugador, casilla):
        referencia = casilla.referencia

        if referencia == "evento_riesgo":
            return self._ejecutar_evento_riesgo(jugador)

        if referencia == "cofre_recompensa":
            return self._ejecutar_recompensa(jugador)

        return self._ejecutar_recompensa(jugador)

    # ============================================================
    # RECOMPENSA
    # ============================================================

    def _ejecutar_recompensa(self, jugador):
        evento = random.choice(self.recompensas)
        dinero = evento["dinero"]

        jugador.sumar_dinero(dinero)

        return {
            "accion": "mostrar_evento",
            "tipo_evento": "premio",
            "titulo": evento["titulo"],
            "mensaje": evento["mensaje"],
            "cerrar_turno": True
        }

    # ============================================================
    # RIESGO 50 / 50
    # ============================================================

    def _ejecutar_evento_riesgo(self, jugador):
        es_bueno = random.choice([True, False])

        if es_bueno:
            return self._ejecutar_riesgo_bueno(jugador)

        return self._ejecutar_riesgo_malo(jugador)

    def _ejecutar_riesgo_malo(self, jugador):
        evento = self._elegir_por_peso(self.riesgos_malos)

        if evento["tipo"] == "perder_dinero":
            return self._riesgo_perder_dinero(jugador)

        if evento["tipo"] == "perder_propiedad_aleatoria":
            return self._riesgo_perder_propiedad_aleatoria(jugador)

        return self._riesgo_perder_dinero(jugador)

    def _ejecutar_riesgo_bueno(self, jugador):
        evento = self._elegir_por_peso(self.riesgos_buenos)

        if evento["tipo"] == "destruir_propiedad":
            return self._riesgo_destruir_propiedad(jugador)

        if evento["tipo"] == "conseguir_yonkou":
            return self._riesgo_conseguir_yonkou(jugador)

        if evento["tipo"] == "ganar_dinero":
            return self._riesgo_ganar_dinero(jugador)

        return self._riesgo_ganar_dinero(jugador)

    # ============================================================
    # RIESGOS MALOS
    # ============================================================

    def _riesgo_perder_dinero(self, jugador):
        cantidad = random.choice([100, 150, 200, 250])

        jugador.restar_dinero(cantidad)

        return {
            "accion": "mostrar_evento",
            "tipo_evento": "riesgo_malo",
            "titulo": "Evento de Riesgo",
            "mensaje": f"Una tormenta dañó tu embarcación. Pierdes ${cantidad}.",
            "cerrar_turno": True
        }

    def _riesgo_perder_propiedad_aleatoria(self, jugador):
        bienes = []

        for propiedad in getattr(jugador, "propiedades", []):
            bienes.append(propiedad)

        for poneglyph in getattr(jugador, "road_poneglyphs", []):
            bienes.append(poneglyph)

        if len(bienes) == 0:
            cantidad = 150
            jugador.restar_dinero(cantidad)

            return {
                "accion": "mostrar_evento",
                "tipo_evento": "riesgo_malo",
                "titulo": "Evento de Riesgo",
                "mensaje": (
                    f"No tenías propiedades ni Road Poneglyphs para perder. "
                    f"En su lugar, pierdes ${cantidad}."
                ),
                "cerrar_turno": True
            }

        bien = random.choice(bienes)

        if bien.tipo == "road_poneglyph":
            if bien in jugador.road_poneglyphs:
                jugador.road_poneglyphs.remove(bien)
        else:
            jugador.quitar_propiedad(bien)

        bien.dueno = None
        bien.nivel_mejora = 0
        bien.tiene_yonkou = False

        return {
            "accion": "mostrar_evento",
            "tipo_evento": "riesgo_malo",
            "titulo": "Evento de Riesgo",
            "mensaje": f"Perdiste {bien.nombre}. Ahora vuelve a estar libre.",
            "cerrar_turno": True
        }

    # ============================================================
    # RIESGOS BUENOS
    # ============================================================

    def _riesgo_destruir_propiedad(self, jugador):
        return {
            "accion": "preparar_destruccion",
            "tipo_evento": "riesgo_bueno",
            "titulo": "Evento Favorable",
            "mensaje": (
                "Puedes destruir una propiedad de otro jugador. "
                "Elige una propiedad enemiga disponible."
            ),
            "cerrar_turno": False
        }

    def _riesgo_conseguir_yonkou(self, jugador):
        return {
            "accion": "preparar_yonkou_evento",
            "tipo_evento": "riesgo_bueno",
            "titulo": "Evento Favorable",
            "mensaje": (
                "Tu tripulación ganó gran influencia. "
                "Puedes aplicar el efecto Yonkou a una de tus islas."
            ),
            "cerrar_turno": False
        }

    def _riesgo_ganar_dinero(self, jugador):
        cantidad = random.choice([150, 200, 250, 300])

        jugador.sumar_dinero(cantidad)

        return {
            "accion": "mostrar_evento",
            "tipo_evento": "riesgo_bueno",
            "titulo": "Evento Favorable",
            "mensaje": f"Encontraste recursos valiosos en la ruta. Ganas ${cantidad}.",
            "cerrar_turno": True
        }

    # ============================================================
    # UTILIDAD
    # ============================================================

    def _elegir_por_peso(self, eventos):
        total = sum(evento["peso"] for evento in eventos)
        numero = random.randint(1, total)

        acumulado = 0

        for evento in eventos:
            acumulado += evento["peso"]

            if numero <= acumulado:
                return evento

        return eventos[-1]