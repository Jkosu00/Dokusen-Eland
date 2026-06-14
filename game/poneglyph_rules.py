from models.propiedad import Propiedad
from services.price_service import calcular_precio_propiedad


class PoneglyphRules:
    def __init__(self):
        self.poneglyphs = {}
        self._crear_poneglyphs()

    def _crear_poneglyphs(self):
        datos = [
            ("Road Poneglyph 1", "road_poneglyph_1", 450),
            ("Road Poneglyph 2", "road_poneglyph_2", 500),
            ("Road Poneglyph 3", "road_poneglyph_3", 550),
            ("Road Poneglyph 4", "road_poneglyph_4", 600),
        ]

        for nombre, referencia, precio in datos:
            self.poneglyphs[referencia] = Propiedad(
                nombre=nombre,
                referencia=referencia,
                tipo="road_poneglyph",
                grupo="road_poneglyph",
                precio_base=precio
            )
    def actualizar_todos_con_lagrange(self, turno_actual):
        total = 0

        for poneglyph in self.poneglyphs.values():
            resultado = self.actualizar_precio_con_lagrange(
                poneglyph,
                turno_actual
            )

            if resultado is not None:
                total += 1

        return total
    def actualizar_precio_con_lagrange(self, poneglyph, turno_actual=1):
        try:
            resultado = calcular_precio_propiedad(
                nombre_propiedad=poneglyph.nombre,
                turno_actual=turno_actual,
                cantidad_puntos=4
            )

            poneglyph.precio_actual = int(resultado["valor_estimado"])
            return resultado

        except Exception as error:
            print(f"No se pudo calcular precio con Lagrange para {poneglyph.nombre}: {error}")
            return None

    def obtener_poneglyph(self, referencia):
        return self.poneglyphs.get(referencia)

    def analizar_poneglyph(self, jugador, casilla,turno_actual=1):
        poneglyph = self.obtener_poneglyph(casilla.referencia)
        
        if poneglyph is not None:
            self.actualizar_precio_con_lagrange(poneglyph, turno_actual)

        if poneglyph is None:
            return {
                "accion": "sin_accion",
                "mensaje": f"No existe Road Poneglyph para {casilla.nombre}."
            }

        if poneglyph.esta_libre():
            precio = self.calcular_precio_compra(jugador, poneglyph)

            return {
                "accion": "preguntar_compra_poneglyph",
                "propiedad": poneglyph,
                "precio": precio,
                "mensaje": f"{poneglyph.nombre} está libre. Precio: ${precio}. Presiona C para comprar o N para pasar."
            }

        if poneglyph.es_del_jugador(jugador):
            return {
                "accion": "sin_accion",
                "propiedad": poneglyph,
                "mensaje": f"{poneglyph.nombre} ya pertenece a {jugador.nombre}."
            }

        impuesto = self.calcular_impuesto_poneglyph(poneglyph)

        return {
            "accion": "pagar_impuesto_poneglyph",
            "propiedad": poneglyph,
            "impuesto": impuesto,
            "mensaje": f"{poneglyph.nombre} pertenece a {poneglyph.dueno.nombre}. Debes pagar ${impuesto}."
        }

    def calcular_precio_compra(self, jugador, poneglyph):
        cantidad = jugador.cantidad_road_poneglyphs()

        multiplicadores = {
            0: 0.50,
            1: 0.65,
            2: 0.80,
            3: 1.00
        }
        
        multiplicador = multiplicadores.get(cantidad, 3.50)
        return int(poneglyph.precio_actual * multiplicador)

    def calcular_impuesto_poneglyph(self, poneglyph):
        dueno = poneglyph.dueno

        if dueno is None:
            return 0

        cantidad = dueno.cantidad_road_poneglyphs()
        return int(poneglyph.precio_actual * 0.10 * cantidad)


    def comprar_poneglyph(self, jugador, poneglyph, precio):
        if not poneglyph.esta_libre():
            return f"{poneglyph.nombre} ya tiene dueño."

        if not jugador.puede_pagar(precio):
            return f"{jugador.nombre} no tiene suficiente dinero para comprar {poneglyph.nombre}."

        jugador.restar_dinero(precio)
        poneglyph.asignar_dueno(jugador)
        jugador.agregar_road_poneglyph(poneglyph)

        if jugador.tiene_4_road_poneglyphs():
            return f"{jugador.nombre} compró los 4 Road Poneglyphs y ganó la partida."

        return f"{jugador.nombre} compró {poneglyph.nombre} por ${precio}."

    def pagar_impuesto_poneglyph(self, jugador, poneglyph):
        impuesto = self.calcular_impuesto_poneglyph(poneglyph)
        dueno = poneglyph.dueno

        if dueno is None or dueno == jugador:
            return "No hay impuesto que pagar."

        pago = min(jugador.dinero, impuesto)
        jugador.restar_dinero(pago)
        dueno.sumar_dinero(pago)

        return f"{jugador.nombre} pagó ${pago} a {dueno.nombre} por caer en {poneglyph.nombre}."