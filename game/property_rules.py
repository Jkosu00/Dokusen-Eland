from models.propiedad import Propiedad
from services.price_service import calcular_precio_propiedad


class PropertyRules:
    def __init__(self):
        self.propiedades = {}
        self._crear_propiedades_base()

    def _crear_propiedades_base(self):
        datos = [
            ("Dawn Island", "dawn_island", "east_blue", 120),
            ("Shells Town", "shells_town", "east_blue", 140),
            ("Orange Town", "orange_town", "east_blue", 160),
            ("Villa Syrup", "villa_syrup", "east_blue", 180),
            ("Baratie", "baratie", "east_blue", 200),
            ("Conomi Island", "conomi_island", "east_blue", 220),

            ("Little Garden", "little_garden", "grand_line_1", 240),
            ("Drum Island", "drum_island", "grand_line_1", 260),
            ("Alabasta", "alabasta", "grand_line_1", 280),
            ("Mock Town", "mock_town", "grand_line_1", 300),
            ("Skypiea", "skypiea", "grand_line_1", 320),
            ("Water 7", "water_7", "grand_line_1", 340),

            ("Thriller Bark", "thriller_bark", "grand_line_2", 360),
            ("Amazon Lily", "amazon_lily", "grand_line_2", 380),
            ("Marineford", "marineford", "grand_line_2", 400),
            ("Gyojin Island", "gyojin_island", "grand_line_2", 420),
            ("Punk Hazard", "punk_hazard", "grand_line_2", 440),
            ("Dressrosa", "dressrosa", "grand_line_2", 460),

            ("Zou Island", "zou_island", "new_world", 480),
            ("Whole Cake", "whole_cake", "new_world", 500),
            ("Wano", "wano", "new_world", 520),
            ("Egghead", "egghead", "new_world", 540),
            ("Elbaf", "elbaf", "new_world", 560),
            ("Laugh Tale", "laugh_tale", "new_world", 600),
        ]

        for nombre, referencia, grupo, precio in datos:
            self.propiedades[referencia] = Propiedad(
                nombre=nombre,
                referencia=referencia,
                tipo="isla",
                grupo=grupo,
                precio_base=precio
            )

    def obtener_propiedad(self, referencia):
        return self.propiedades.get(referencia)

    def actualizar_precio_con_lagrange(self, propiedad, turno_actual=7):
        try:
            resultado = calcular_precio_propiedad(
                nombre_propiedad=propiedad.nombre,
                turno_actual=turno_actual,
                cantidad_puntos=4
            )

            propiedad.precio_actual = int(resultado["valor_estimado"])
            return resultado

        except Exception as error:
            print(f"No se pudo calcular precio con Lagrange para {propiedad.nombre}: {error}")
            return None

    def analizar_isla(self, jugador, casilla):
        propiedad = self.obtener_propiedad(casilla.referencia)

        if propiedad is not None:
            self.actualizar_precio_con_lagrange(propiedad)

        if propiedad is None:
            return {
                "accion": "sin_accion",
                "mensaje": f"No existe propiedad para {casilla.nombre}."
            }

        if propiedad.esta_libre():
            return {
                "accion": "preguntar_compra",
                "propiedad": propiedad,
                "mensaje": f"{propiedad.nombre} está libre. Precio: ${propiedad.precio_actual}. Presiona C para comprar o N para pasar."
            }

        if propiedad.es_del_jugador(jugador):
            costo = propiedad.calcular_costo_mejora()

            return {
                "accion": "preguntar_mejora",
                "propiedad": propiedad,
                "mensaje": f"{propiedad.nombre} es tuya. Mejora cuesta ${costo}. Presiona M para mejorar o N para pasar."
            }

        impuesto = propiedad.calcular_impuesto()
        recompra = propiedad.calcular_recompra()

        return {
            "accion": "preguntar_recompra",
            "propiedad": propiedad,
            "impuesto": impuesto,
            "recompra": recompra,
            "mensaje": f"{propiedad.nombre} es de {propiedad.dueno.nombre}. Impuesto ${impuesto}. Presiona R para recomprar o N para solo pagar."
        }

    def comprar_propiedad(self, jugador, propiedad):
        precio = propiedad.precio_actual

        if not propiedad.esta_libre():
            return f"{propiedad.nombre} ya tiene dueño."

        if not jugador.puede_pagar(precio):
            return f"{jugador.nombre} no tiene suficiente dinero para comprar {propiedad.nombre}."

        jugador.restar_dinero(precio)
        propiedad.asignar_dueno(jugador)
        jugador.agregar_propiedad(propiedad)

        return f"{jugador.nombre} compró {propiedad.nombre} por ${precio}."

    def mejorar_propiedad(self, jugador, propiedad):
        if not propiedad.es_del_jugador(jugador):
            return f"{propiedad.nombre} no pertenece a {jugador.nombre}."

        if not propiedad.puede_mejorarse():
            return f"{propiedad.nombre} ya tiene mejora máxima."

        costo = propiedad.calcular_costo_mejora()

        if not jugador.puede_pagar(costo):
            return f"{jugador.nombre} no tiene suficiente dinero para mejorar."

        jugador.restar_dinero(costo)
        propiedad.mejorar()

        return f"{jugador.nombre} mejoró {propiedad.nombre} al nivel {propiedad.nivel_mejora}."

    def pagar_impuesto(self, jugador, propiedad):
        impuesto = propiedad.calcular_impuesto()
        dueno = propiedad.dueno

        if dueno is None or dueno == jugador:
            return f"No hay impuesto que pagar."

        pago = min(jugador.dinero, impuesto)

        jugador.restar_dinero(pago)
        dueno.sumar_dinero(pago)

        return f"{jugador.nombre} pagó ${pago} a {dueno.nombre} por caer en {propiedad.nombre}."

    def recomprar_propiedad(self, jugador, propiedad):
        dueno_anterior = propiedad.dueno
        costo = propiedad.calcular_recompra()

        if dueno_anterior is None:
            return f"{propiedad.nombre} está libre, no se recompra."

        if dueno_anterior == jugador:
            return f"{propiedad.nombre} ya pertenece a {jugador.nombre}."

        if not jugador.puede_pagar(costo):
            return f"{jugador.nombre} no tiene suficiente dinero para recomprar {propiedad.nombre}."

        jugador.restar_dinero(costo)
        dueno_anterior.sumar_dinero(costo)

        dueno_anterior.quitar_propiedad(propiedad)
        propiedad.asignar_dueno(jugador)
        jugador.agregar_propiedad(propiedad)

        return f"{jugador.nombre} recompró {propiedad.nombre} por ${costo}."