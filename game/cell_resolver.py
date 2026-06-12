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


class CellResolver:
    def __init__(self):
        pass

    def resolver_casilla(self, jugador, casilla):
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
            return self.resolver_isla(jugador, casilla)

        elif casilla.tipo == TIPO_EVENTO:
            return self.resolver_evento(jugador, casilla)

        elif casilla.tipo == TIPO_ROAD_PONEGLYPH:
            return self.resolver_road_poneglyph(jugador, casilla)

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
        """
        Aquí después se conectará la lógica de cobrar Berries al pasar o caer en salida.
        """

        print(f"{jugador.nombre} cayó en SALIDA.")
        print("Acción futura: entregar Berries al jugador.")
        return {
            "tipo": TIPO_SALIDA,
            "mensaje": f"{jugador.nombre} cayó en salida."
        }

    def resolver_isla(self, jugador, casilla):
        """
        Aquí después se conectará la lógica de propiedades:
        comprar, pagar impuesto, mejorar o recomprar.
        """

        print(f"{jugador.nombre} cayó en una ISLA.")
        print(f"Referencia de isla: {casilla.referencia}")
        print("Acción futura: llamar a property_rules.py.")
        return {
            "tipo": TIPO_ISLA,
            "mensaje": f"{jugador.nombre} cayó en {casilla.nombre}.",
            "referencia": casilla.referencia
        }

    def resolver_evento(self, jugador, casilla):
        """
        Aquí después se conectará la lógica de eventos:
        evento aleatorio, decisión en pantalla, recompensa o castigo.
        """

        print(f"{jugador.nombre} cayó en EVENTO.")
        print(f"Referencia de evento: {casilla.referencia}")
        print("Acción futura: llamar a event_rules.py o event_service.py.")
        return {
            "tipo": TIPO_EVENTO,
            "mensaje": f"{jugador.nombre} cayó en evento.",
            "referencia": casilla.referencia
        }

    def resolver_road_poneglyph(self, jugador, casilla):
        """
        Aquí después se conectará la lógica de Road Poneglyph:
        compra, precio especial y victoria por tener los 4.
        """

        print(f"{jugador.nombre} cayó en ROAD PONEGLYPH.")
        print(f"Referencia: {casilla.referencia}")
        print("Acción futura: llamar a poneglyph_rules.py.")
        return {
            "tipo": TIPO_ROAD_PONEGLYPH,
            "mensaje": f"{jugador.nombre} cayó en {casilla.nombre}.",
            "referencia": casilla.referencia
        }

    def resolver_yonko(self, jugador, casilla):
        """
        Aquí después se conectará la lógica de Yonko:
        elegir una isla propia y potenciar su impuesto.
        """

        print(f"{jugador.nombre} cayó en la casilla YONKO.")
        print("Acción futura: llamar a yonko_rules.py.")
        print("Debe permitir elegir una propiedad para mejorar su bounty.")
        return {
            "tipo": TIPO_YONKO,
            "mensaje": f"{jugador.nombre} cayó en la casilla Yonko.",
            "referencia": casilla.referencia
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
        """
        Aquí después se conectará la lógica de descanso.
        Puede no hacer nada.
        """

        print(f"{jugador.nombre} cayó en DESCANSO.")
        print("Acción futura: no ocurre nada o se muestra mensaje.")
        return {
            "tipo": TIPO_DESCANSO,
            "mensaje": f"{jugador.nombre} descansó en esta casilla.",
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