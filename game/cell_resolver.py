from models.casilla import (
    TIPO_SALIDA,
    TIPO_ISLA,
    TIPO_EVENTO,
    TIPO_ROAD_PONEGLYPH,
    TIPO_YONKO,
    TIPO_CARCEL,
    TIPO_IMPUESTO,
    TIPO_DESCANSO
)
from game.property_rules import PropertyRules
from game.poneglyph_rules import PoneglyphRules
from game.yonkou_rules import YonkouRules
from game.event_rules import EventRules


class CellResolver:
    def __init__(self):
        self.property_rules = PropertyRules()
        self.poneglyph_rules = PoneglyphRules()
        self.yonkou_rules = YonkouRules(self.property_rules)
        self.event_rules = EventRules()

    def resolver_casilla(self, jugador, casilla,turno_actual = 1):
        """
        Recibe el jugador y la casilla donde cayó.
        Según el tipo de casilla, llama al método correspondiente.
        """

        print("\n=== RESOLVIENDO CASILLA ===")
        print(f"Jugador: {jugador.nombre}")
        print(f"Casilla: {casilla.nombre}")
        print(f"Tipo: {casilla.tipo}")
        print(f"Posición: {casilla.posicion}")

        if casilla.tipo == TIPO_SALIDA:
            return self.resolver_salida(jugador, casilla)

        elif casilla.tipo == TIPO_ISLA:
            return self.resolver_isla(jugador, casilla, turno_actual)

        elif casilla.tipo == TIPO_EVENTO:
            return self.resolver_evento(jugador, casilla)

        elif casilla.tipo == TIPO_ROAD_PONEGLYPH:
            return self.resolver_road_poneglyph(jugador, casilla, turno_actual)

        elif casilla.tipo == TIPO_YONKO:
            return self.resolver_yonko(jugador, casilla)

        elif casilla.tipo == TIPO_CARCEL:
            return self.resolver_carcel(jugador, casilla)

        elif casilla.tipo == TIPO_IMPUESTO:
            return self.resolver_impuesto(jugador, casilla)

        elif casilla.tipo == TIPO_DESCANSO:
            return self.resolver_descanso(jugador, casilla)

        else:
            return self.resolver_desconocida(jugador, casilla)

    def resolver_salida(self, jugador, casilla):
        mensaje = f"{jugador.nombre} cayó en Salida."

        print(mensaje)

        return {
            "tipo": TIPO_SALIDA,
            "accion": "sin_accion",
            "mensaje": mensaje,
            "referencia": casilla.referencia
        }

    def resolver_isla(self, jugador, casilla, turno_actual):
        resultado = self.property_rules.analizar_isla(jugador, casilla, turno_actual)

        print(resultado["mensaje"])

        return {
            "tipo": TIPO_ISLA,
            "accion": resultado["accion"],
            "mensaje": resultado["mensaje"],
            "referencia": casilla.referencia,
            "propiedad": resultado.get("propiedad"),
            "impuesto": resultado.get("impuesto"),
            "recompra": resultado.get("recompra")
        }

    def resolver_evento(self, jugador, casilla):
        mensaje = self.event_rules.ejecutar_evento(
            jugador,
            casilla.referencia
        )

        print(mensaje)

        return {
            "tipo": TIPO_EVENTO,
            "accion": "sin_accion",
            "mensaje": mensaje,
            "referencia": casilla.referencia
        }

    def resolver_road_poneglyph(self, jugador, casilla, turno_actual):
        resultado = self.poneglyph_rules.analizar_poneglyph(jugador, casilla, turno_actual)

        print(resultado["mensaje"])

        return {
            "tipo": TIPO_ROAD_PONEGLYPH,
            "accion": resultado["accion"],
            "mensaje": resultado["mensaje"],
            "referencia": casilla.referencia,
            "propiedad": resultado.get("propiedad"),
            "precio": resultado.get("precio"),
            "impuesto": resultado.get("impuesto")
        }

    def resolver_yonko(self, jugador, casilla):
        resultado = self.yonkou_rules.analizar_yonkou(jugador)

        print(resultado["mensaje"])

        return {
            "tipo": TIPO_YONKO,
            "accion": resultado["accion"],
            "mensaje": resultado["mensaje"],
            "referencia": casilla.referencia,
            "propiedades": resultado.get("propiedades")
        }        

    def resolver_carcel(self, jugador, casilla):
        """
        Aquí después se conectará la lógica de cárcel o prisión.
        """

        print(f"{jugador.nombre} cayó en CÁRCEL / PRISIÓN.")
        print(f"Referencia: {casilla.referencia}")

        if casilla.referencia == "ir_carcel":
            print("Acción futura: mover jugador directamente a la prisión.")
        else:
            print("Acción futura: aplicar reglas de visita o cárcel.")

        return {
            "tipo": TIPO_CARCEL,
            "mensaje": f"{jugador.nombre} cayó en cárcel.",
            "referencia": casilla.referencia
        }

    def resolver_impuesto(self, jugador, casilla):
        """
        Aquí después se conectará la lógica de pagos obligatorios.
        """

        print(f"{jugador.nombre} cayó en IMPUESTO.")
        print("Acción futura: cobrar Berries al jugador.")
        return {
            "tipo": TIPO_IMPUESTO,
            "mensaje": f"{jugador.nombre} cayó en impuesto.",
            "referencia": casilla.referencia
        }

    def resolver_descanso(self, jugador, casilla):
        jugador.sumar_dinero(200)

        mensaje = f"{jugador.nombre} cayó en Descanso y recibió $200 Berries."

        print(mensaje)

        return {
            "tipo": TIPO_DESCANSO,
            "accion": "sin_accion",
            "mensaje": mensaje,
            "referencia": casilla.referencia
        }

    def resolver_desconocida(self, jugador, casilla):
        """
        Se usa si por error aparece un tipo de casilla no reconocido.
        """

        print(f"Tipo de casilla desconocido: {casilla.tipo}")
        return {
            "tipo": "desconocida",
            "mensaje": f"Tipo de casilla no reconocido: {casilla.tipo}",
            "referencia": casilla.referencia
        }