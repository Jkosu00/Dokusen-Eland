from models.propiedad import Propiedad
from services.price_service import calcular_precio_propiedad


class PropertyRules:
    def __init__(self):
        self.propiedades = {}
        self._crear_propiedades_base()

    def _crear_propiedades_base(self):
        datos = [
            # MONOPOLIO 1 - East Blue inicial
            ("Dawn Island", "dawn_island", "east_blue_1", 120),
            ("Shells Town", "shells_town", "east_blue_1", 140),
            ("Orange Town", "orange_town", "east_blue_1", 160),

            # MONOPOLIO 2 - East Blue final
            ("Villa Syrup", "villa_syrup", "east_blue_2", 180),
            ("Baratie", "baratie", "east_blue_2", 200),
            ("Conomi Island", "conomi_island", "east_blue_2", 220),

            # MONOPOLIO 3 - Grand Line inicial
            ("Little Garden", "little_garden", "grand_line_1", 240),
            ("Drum Island", "drum_island", "grand_line_1", 260),
            ("Alabasta", "alabasta", "grand_line_1", 280),

            # MONOPOLIO 4 - Grand Line avanzada
            ("Mock Town", "mock_town", "grand_line_2", 300),
            ("Skypiea", "skypiea", "grand_line_2", 320),
            ("Water 7", "water_7", "grand_line_2", 340),

            # MONOPOLIO 5 - Saga de guerra
            ("Thriller Bark", "thriller_bark", "grand_line_3", 360),
            ("Amazon Lily", "amazon_lily", "grand_line_3", 380),
            ("Marineford", "marineford", "grand_line_3", 400),

            # MONOPOLIO 6 - Nuevo Mundo inicial
            ("Gyojin Island", "gyojin_island", "new_world_1", 420),
            ("Punk Hazard", "punk_hazard", "new_world_1", 440),
            ("Dressrosa", "dressrosa", "new_world_1", 460),

            # MONOPOLIO 7 - Territorios Yonkou
            ("Zou Island", "zou_island", "new_world_2", 480),
            ("Whole Cake", "whole_cake", "new_world_2", 500),
            ("Wano", "wano", "new_world_2", 520),

            # MONOPOLIO 8 - Final del Nuevo Mundo
            ("Egghead", "egghead", "new_world_3", 540),
            ("Elbaf", "elbaf", "new_world_3", 560),
            ("Laugh Tale", "laugh_tale", "new_world_3", 600),
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

    def obtener_propiedades_por_grupo(self, grupo):
        return [
            propiedad for propiedad in self.propiedades.values()
            if propiedad.grupo == grupo
        ]

    def jugador_tiene_monopolio(self, jugador, grupo):
        if jugador is None:
            return False

        propiedades_grupo = self.obtener_propiedades_por_grupo(grupo)

        if len(propiedades_grupo) != 3:
            return False

        return all(
            propiedad.dueno == jugador
            for propiedad in propiedades_grupo
        )

    def contar_monopolios(self, jugador):
        grupos = set(
            propiedad.grupo
            for propiedad in self.propiedades.values()
        )

        total = 0

        for grupo in grupos:
            if self.jugador_tiene_monopolio(jugador, grupo):
                total += 1

        return total

    def obtener_monopolios_jugador(self, jugador):
        grupos = set(
            propiedad.grupo
            for propiedad in self.propiedades.values()
        )

        monopolios = []

        for grupo in grupos:
            if self.jugador_tiene_monopolio(jugador, grupo):
                monopolios.append(grupo)

        return monopolios

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

        tiene_monopolio_dueno = self.jugador_tiene_monopolio(
            propiedad.dueno,
            propiedad.grupo
        )

        recompra = propiedad.calcular_recompra(
            tiene_monopolio=tiene_monopolio_dueno
        )

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

        jugador.restar_dinero(impuesto)
        dueno.sumar_dinero(impuesto)

        return f"{jugador.nombre} pagó ${impuesto} a {dueno.nombre} por caer en {propiedad.nombre}."

    def recomprar_propiedad(self, jugador, propiedad):
        dueno_anterior = propiedad.dueno

        if dueno_anterior is None:
            return f"{propiedad.nombre} está libre, no se recompra."

        if dueno_anterior == jugador:
            return f"{propiedad.nombre} ya pertenece a {jugador.nombre}."

        tiene_monopolio_dueno = self.jugador_tiene_monopolio(
            dueno_anterior,
            propiedad.grupo
        )

        costo = propiedad.calcular_recompra(
            tiene_monopolio=tiene_monopolio_dueno
        )

        if not jugador.puede_pagar(costo):
            return f"{jugador.nombre} no tiene suficiente dinero para recomprar {propiedad.nombre}."

        jugador.restar_dinero(costo)
        dueno_anterior.sumar_dinero(costo)

        dueno_anterior.quitar_propiedad(propiedad)
        propiedad.asignar_dueno(jugador)
        jugador.agregar_propiedad(propiedad)

        return f"{jugador.nombre} recompró {propiedad.nombre} por ${costo}."
    
    def calcular_precio_compra_con_nivel(self, propiedad, nivel_objetivo):
        """
        Calcula el precio total de comprar una propiedad con mejoras iniciales.

        nivel_objetivo:
        1 = compra base
        2 = compra con 1 mejora
        3 = compra con 2 mejoras
        """

        if nivel_objetivo < 1:
            nivel_objetivo = 1

        if nivel_objetivo > 3:
            nivel_objetivo = 3

        precio_base = propiedad.precio_actual
        mejoras_a_comprar = nivel_objetivo - 1
        costo_mejora = propiedad.calcular_costo_mejora()

        return precio_base + (costo_mejora * mejoras_a_comprar)


    def comprar_propiedad_con_nivel(self, jugador, propiedad, nivel_objetivo):
        """
        Compra una propiedad y la deja con el nivel indicado.
        Nivel 1 = sin mejoras.
        Nivel 2 = 1 mejora.
        Nivel 3 = 2 mejoras.
        """

        if not propiedad.esta_libre():
            return f"{propiedad.nombre} ya tiene dueño."

        precio_total = self.calcular_precio_compra_con_nivel(
            propiedad,
            nivel_objetivo
        )

        if not jugador.puede_pagar(precio_total):
            return f"{jugador.nombre} no tiene suficiente dinero para comprar {propiedad.nombre} en nivel {nivel_objetivo}."

        jugador.restar_dinero(precio_total)
        propiedad.asignar_dueno(jugador)
        jugador.agregar_propiedad(propiedad)

        propiedad.nivel_mejora = nivel_objetivo - 1

        if nivel_objetivo == 1:
            return f"{jugador.nombre} compró {propiedad.nombre} por ${precio_total}."

        return f"{jugador.nombre} compró {propiedad.nombre} en nivel {nivel_objetivo} por ${precio_total}."