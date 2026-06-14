class YonkouRules:
    def __init__(self, property_rules):
        self.property_rules = property_rules
        self.jugador_yonkou = None
        self.propiedad_yonkou = None

    def analizar_yonkou(self, jugador):
        propiedades_isla = [
            propiedad for propiedad in jugador.propiedades
            if propiedad.tipo == "isla"
        ]

        if not propiedades_isla:
            self.jugador_yonkou = jugador
            jugador.es_yonkou = True

            return {
                "accion": "sin_accion",
                "mensaje": f"{jugador.nombre} ahora es Yonkou, pero no tiene islas para mejorar."
            }

        return {
            "accion": "seleccionar_isla_yonkou",
            "propiedades": propiedades_isla,
            "mensaje": f"{jugador.nombre} debe elegir una isla para aplicar Bounty Yonkou."
        }

    def aplicar_yonkou(self, jugador, propiedad):
        if self.propiedad_yonkou is not None:
            self.propiedad_yonkou.tiene_yonkou = False

        if self.jugador_yonkou is not None:
            self.jugador_yonkou.es_yonkou = False

        self.jugador_yonkou = jugador
        self.propiedad_yonkou = propiedad

        jugador.es_yonkou = True
        propiedad.tiene_yonkou = True

        return f"{propiedad.nombre} recibió Bounty Yonkou."
