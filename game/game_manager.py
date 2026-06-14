import os
import pygame

from game.dice import Dice
from game.turn_manager import TurnManager
from game.board_manager import BoardManager
from game.movement_manager import MovementManager
from game.cell_resolver import CellResolver


class GameManager:
    def __init__(
        self,
        jugadores,
        ancho=1280,
        alto=720,
        board_size=600,
        board_path="assets/images/board/tablero.png",
        background_path="assets/images/board/fondo.png"
    ):
        pygame.init()

        self.ancho = ancho
        self.alto = alto
        self.board_size = board_size

        self.board_x = (self.ancho - self.board_size) // 2
        self.board_y = (self.alto - self.board_size) // 2

        self.board_path = board_path
        self.background_path = background_path

        self.pantalla = pygame.display.set_mode((self.ancho, self.alto))
        pygame.display.set_caption("Dokusen Eland - Ruta del Rey Pirata")

        self.reloj = pygame.time.Clock()
        self.running = True

        self.jugadores = jugadores

        self.dice = Dice(size=(72, 72))

        self.board_manager = BoardManager(
            board_x=self.board_x,
            board_y=self.board_y,
            board_size=self.board_size
        )

        self.movement_manager = MovementManager(
            board_manager=self.board_manager,
            velocidad=260
        )

        self.turn_manager = TurnManager(
            jugadores=self.jugadores,
            dice=self.dice
        )

        self.cell_resolver = CellResolver()

        self.estado = "esperando_lanzamiento"
        self.accion_pendiente = None
        self.propiedad_pendiente = None
        self.casilla_yonkou = None
        self.modal_titulo = ""
        self.modal_lineas = []
        self.modal_opciones = []
        self.mensaje_temporal_tiempo = 0
        self.mensaje_salida_pendiente = ""
        self.ganador = None
        self.motivo_victoria = ""
        self.propiedades_yonkou_disponibles = []

        self.mensaje = "Presiona ESPACIO para lanzar los dados"
        self.detalle_casilla = ""

        self.dado_1 = 0
        self.dado_2 = 0
        self.suma_dados = 0

        self.fondo = self._cargar_fondo()
        self.tablero = self._cargar_tablero()

        self._preparar_jugadores()
        self._definir_orden_inicial()


    def _cargar_imagen_segura(self, path, size=None, usar_alpha=False):
        """
        Carga una imagen si existe.
        Si no existe, devuelve None.
        """

        if not path or not os.path.exists(path):
            return None

        if usar_alpha:
            imagen = pygame.image.load(path).convert_alpha()
        else:
            imagen = pygame.image.load(path).convert()

        if size:
            imagen = pygame.transform.scale(imagen, size)

        return imagen

    def _abrir_modal(self, titulo, lineas, opciones):
        self.modal_titulo = titulo
        self.modal_lineas = lineas
        self.modal_opciones = opciones

    def _cargar_fondo(self):
        """
        Carga el fondo completo de pantalla.
        Si no existe, crea un fondo temporal.
        """

        fondo = self._cargar_imagen_segura(
            self.background_path,
            size=(self.ancho, self.alto),
            usar_alpha=False
        )

        if fondo:
            return fondo

        fondo_temporal = pygame.Surface((self.ancho, self.alto))
        fondo_temporal.fill((18, 28, 45))

        return fondo_temporal

    def _cargar_tablero(self):
        """
        Carga el tablero centrado.
        Si no existe, crea un tablero temporal.
        """

        tablero = self._cargar_imagen_segura(
            self.board_path,
            size=(self.board_size, self.board_size),
            usar_alpha=False
        )

        if tablero:
            return tablero

        tablero_temporal = pygame.Surface((self.board_size, self.board_size))
        tablero_temporal.fill((180, 150, 100))

        return tablero_temporal

    def _preparar_jugadores(self):
        """
        Coloca los jugadores en la casilla de salida y carga sus imágenes si existen.
        """

        for i, jugador in enumerate(self.jugadores):
            x, y = self.board_manager.obtener_coordenadas_ficha(
                posicion=0,
                indice_jugador=i,
                ficha_size=48
            )

            jugador.establecer_coordenadas(x, y)
            jugador.posicion = 0

            imagen = self._cargar_imagen_segura(
                getattr(jugador, "ruta_imagen", ""),
                size=(64, 64),
                usar_alpha=True
            )

            ficha = self._cargar_imagen_segura(
                getattr(jugador, "ruta_ficha", ""),
                size=(48, 48),
                usar_alpha=True
            )

            jugador.imagen = imagen
            jugador.ficha = ficha

            if ficha:
                jugador.rect = ficha.get_rect()
                jugador.rect.topleft = (jugador.x, jugador.y)

    def _definir_orden_inicial(self):
        """
        Lanza dados para definir el orden inicial.
        """

        resultados = self.turn_manager.definir_orden_inicial()

        print("\n=== ORDEN INICIAL ===")

        for item in resultados:
            jugador = item["jugador"]

            print(
                f"{jugador.nombre}: "
                f"{item['dado_1']} + {item['dado_2']} = {item['suma']}"
            )

        print("\n=== ORDEN FINAL ===")

        for jugador in self.turn_manager.obtener_orden_jugadores():
            print(f"Orden {jugador.orden_turno}: {jugador.nombre}")

    def run(self):
        """
        Loop principal del juego.
        """

        while self.running:
            dt = self.reloj.tick(60) / 1000

            self._manejar_eventos()
            self._actualizar(dt)
            self._dibujar()

        pygame.quit()

    def _manejar_eventos(self):
        """
        Maneja teclado, mouse y cierre de ventana.
        """

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.estado == "seleccionando_yonkou":
                    self._manejar_click_yonkou(event.pos)
                    continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                # Atajo de prueba: fuerza victoria por 4 Road Poneglyphs
                if event.key == pygame.K_F4:
                    jugador_actual = self.turn_manager.obtener_jugador_actual()
                    jugador_actual.road_poneglyphs = [1, 2, 3, 4]
                    self.ganador = jugador_actual
                    self.motivo_victoria = "reunió los 4 Road Poneglyphs"
                    self.estado = "fin_partida"
                    self.mensaje = f"{jugador_actual.nombre} ganó: {self.motivo_victoria}."
                    self.detalle_casilla = ""
                    print(self.mensaje)
                    continue

                if self.estado in [
                    "decidiendo_compra",
                    "decidiendo_mejora",
                    "decidiendo_recompra",
                    "decidiendo_compra_poneglyph",
                    "mostrando_evento"
                ]:
                    self._manejar_decision_propiedad(event.key)
                    continue

                if event.key == pygame.K_SPACE:
                    self._intentar_lanzar_dados()

    def _manejar_decision_propiedad(self, tecla):
        jugador_actual = self.turn_manager.obtener_jugador_actual()

        if self.estado == "decidiendo_compra":
            if tecla == pygame.K_c:
                self.detalle_casilla = self.cell_resolver.property_rules.comprar_propiedad(
                    jugador_actual,
                    self.propiedad_pendiente
                )
                self._finalizar_decision()

            elif tecla == pygame.K_n:
                self.detalle_casilla = f"{jugador_actual.nombre} decidió no comprar."
                self._finalizar_decision()

        elif self.estado == "decidiendo_mejora":
            if tecla == pygame.K_m:
                self.detalle_casilla = self.cell_resolver.property_rules.mejorar_propiedad(
                    jugador_actual,
                    self.propiedad_pendiente
                )
                self._finalizar_decision()

            elif tecla == pygame.K_n:
                self.detalle_casilla = f"{jugador_actual.nombre} decidió no mejorar."
                self._finalizar_decision()

        elif self.estado == "decidiendo_recompra":
            if tecla == pygame.K_r:
                pago = self.cell_resolver.property_rules.pagar_impuesto(
                    jugador_actual,
                    self.propiedad_pendiente
                )

                recompra = self.cell_resolver.property_rules.recomprar_propiedad(
                    jugador_actual,
                    self.propiedad_pendiente
                )

                self.detalle_casilla = f"{pago} {recompra}"
                self._finalizar_decision()

            elif tecla == pygame.K_n:
                self.detalle_casilla = self.cell_resolver.property_rules.pagar_impuesto(
                    jugador_actual,
                    self.propiedad_pendiente
                )
                self._finalizar_decision()

        elif self.estado == "decidiendo_compra_poneglyph":
            if tecla == pygame.K_c:
                precio = self.cell_resolver.poneglyph_rules.calcular_precio_compra(
                    jugador_actual,
                    self.propiedad_pendiente
                )

                self.detalle_casilla = self.cell_resolver.poneglyph_rules.comprar_poneglyph(
                    jugador_actual,
                    self.propiedad_pendiente,
                    precio
                )
                if jugador_actual.tiene_4_road_poneglyphs():
                    self.ganador = jugador_actual
                    self.motivo_victoria = "reunió los 4 Road Poneglyphs"
                    self.estado = "fin_partida"
                    self.mensaje = f"{jugador_actual.nombre} ganó: {self.motivo_victoria}."
                    return

                self._finalizar_decision()

            elif tecla == pygame.K_n:
                self.detalle_casilla = f"{jugador_actual.nombre} decidió no comprar el Road Poneglyph."
                self._finalizar_decision()    

        elif self.estado == "decidiendo_yonkou":
            if tecla == pygame.K_y:
                self.detalle_casilla = self.cell_resolver.yonkou_rules.aplicar_yonkou(
                    jugador_actual,
                    self.propiedad_pendiente
                )
                self._finalizar_decision()

            elif tecla == pygame.K_n:
                self.detalle_casilla = f"{jugador_actual.nombre} decidió no aplicar Bounty Yonkou."
                self._finalizar_decision()

        elif self.estado == "mostrando_evento":
            if tecla == pygame.K_n or tecla == pygame.K_RETURN:
                self._finalizar_decision()

    def _manejar_click_yonkou(self, pos_mouse):
        jugador_actual = self.turn_manager.obtener_jugador_actual()
        referencias = [p.referencia for p in self.propiedades_yonkou_disponibles]

        for casilla in self.board_manager.obtener_todas_las_casillas():
            rect = pygame.Rect(casilla.x, casilla.y, casilla.ancho, casilla.alto)

            if rect.collidepoint(pos_mouse) and casilla.referencia in referencias:
                propiedad = None

                for p in self.propiedades_yonkou_disponibles:
                    if p.referencia == casilla.referencia:
                        propiedad = p
                        break

                if propiedad:
                    self.casilla_yonkou = casilla.referencia
                    self.detalle_casilla = self.cell_resolver.yonkou_rules.aplicar_yonkou(
                        jugador_actual,
                        propiedad
                    )

                    self.propiedades_yonkou_disponibles = []
                    self._finalizar_decision()

                return

    def _finalizar_decision(self):
        self.accion_pendiente = None
        self.propiedad_pendiente = None

        self.turn_manager.siguiente_turno()
        self.estado = "esperando_lanzamiento"

        if self.detalle_casilla:
            self.mensaje = self.detalle_casilla
            self.mensaje_temporal_tiempo = pygame.time.get_ticks()
        else:
            self.mensaje = "Presiona ESPACIO para lanzar los dados"

        self.modal_titulo = ""
        self.modal_lineas = []
        self.modal_opciones = []

    def _intentar_lanzar_dados(self):
        """
        Inicia el lanzamiento de dados solo si el juego está listo.
        """
        if self.estado == "fin_partida":
            return

        if self.estado != "esperando_lanzamiento":
            return

        if self.dice.esta_animando():
            return

        if self.movement_manager.esta_moviendose():
            return

        self.mensaje_temporal_tiempo = 0
        self.detalle_casilla = ""
        self.mensaje_salida_pendiente = ""

        jugador_actual = self.turn_manager.obtener_jugador_actual()

        self.dice.iniciar_lanzamiento()

        self.estado = "animando_dados"
        self.mensaje = f"{jugador_actual.nombre} está lanzando los dados..."

    def _actualizar(self, dt):
        """
        Actualiza dados, movimiento y estados del juego.
        """

        self.dice.actualizar()
        self.movement_manager.actualizar(dt)

        if self.estado == "animando_dados":
            self._actualizar_animacion_dados()

        elif self.estado == "moviendo_ficha":
            self._actualizar_movimiento_ficha()

        if self.mensaje_temporal_tiempo > 0:
            tiempo_actual = pygame.time.get_ticks()

            if tiempo_actual - self.mensaje_temporal_tiempo >= 3000:
                self.mensaje = "Presiona ESPACIO para lanzar los dados"
                self.detalle_casilla = ""
                self.mensaje_temporal_tiempo = 0

    def _actualizar_animacion_dados(self):
        """
        Cuando termina la animación de dados, inicia el movimiento.
        """

        if self.dice.esta_animando():
            return

        self.dado_1, self.dado_2, self.suma_dados = self.dice.obtener_resultados()

        self.turn_manager.registrar_resultado_dados(
            self.dado_1,
            self.dado_2
        )

        jugador_actual = self.turn_manager.obtener_jugador_actual()

        self.mensaje = (
            f"{jugador_actual.nombre} sacó "
            f"{self.dado_1} + {self.dado_2} = {self.suma_dados}"
        )

        # Cobro por dar vuelta al tablero. Se hace una sola vez, antes de mover.
        if self.board_manager.paso_por_salida(jugador_actual.posicion, self.suma_dados):
            jugador_actual.sumar_dinero(350)
            self.mensaje_salida_pendiente = (
                f"{jugador_actual.nombre} pasó por Salida y recibió $350 Berries."
            )
        else:
            self.mensaje_salida_pendiente = ""

        self.detalle_casilla = "Moviendo ficha..."

        self.movement_manager.iniciar_movimiento(
            jugador=jugador_actual,
            pasos=self.suma_dados,
            indice_jugador=self.turn_manager.indice_turno_actual,
            ficha_size=48
        )

        self.estado = "moviendo_ficha"

    def _actualizar_movimiento_ficha(self):
        """
        Cuando termina el movimiento, resuelve la casilla.
        """

        if self.movement_manager.esta_moviendose():
            return

        casilla_final = self.movement_manager.obtener_ultima_casilla_final()
        jugador_actual = self.turn_manager.obtener_jugador_actual()

        if casilla_final:
            resultado = self.cell_resolver.resolver_casilla(
                jugador_actual,
                casilla_final
            )

            self.detalle_casilla = resultado["mensaje"]
            accion = resultado.get("accion")

            # Eventos: se muestran en ventana emergente y se confirma con N o Enter.
            if resultado.get("tipo") == "evento":
                self.estado = "mostrando_evento"
                self.mensaje = f"{jugador_actual.nombre} cayó en {casilla_final.nombre}."

                self._abrir_modal(
                    titulo=casilla_final.nombre,
                    lineas=[resultado["mensaje"]],
                    opciones=["[N] Continuar"]
                )

                self.movement_manager.limpiar_ultima_casilla()
                return

            # Road Poneglyph de otro jugador: solo se paga impuesto, no se recompra.
            if accion == "pagar_impuesto_poneglyph":
                self.detalle_casilla = self.cell_resolver.poneglyph_rules.pagar_impuesto_poneglyph(
                    jugador_actual,
                    resultado.get("propiedad")
                )
                self.mensaje = self.detalle_casilla
                self.mensaje_temporal_tiempo = pygame.time.get_ticks()

                self.movement_manager.limpiar_ultima_casilla()
                self.turn_manager.siguiente_turno()
                self.estado = "esperando_lanzamiento"
                return

            if accion in [
                "preguntar_compra",
                "preguntar_mejora",
                "preguntar_recompra",
                "preguntar_compra_poneglyph",
                "seleccionar_isla_yonkou"
            ]:
                self.accion_pendiente = accion
                self.propiedad_pendiente = resultado.get("propiedad")
                propiedad = self.propiedad_pendiente

                if accion == "preguntar_compra":
                    if not jugador_actual.puede_pagar(propiedad.precio_actual):
                        self.detalle_casilla = (
                            f"{jugador_actual.nombre} no tiene saldo suficiente para comprar {propiedad.nombre}."
                        )
                        self.mensaje = self.detalle_casilla
                        self.mensaje_temporal_tiempo = pygame.time.get_ticks()

                        self.movement_manager.limpiar_ultima_casilla()
                        self.turn_manager.siguiente_turno()
                        self.estado = "esperando_lanzamiento"
                        return

                    self.estado = "decidiendo_compra"

                    self._abrir_modal(
                        titulo=propiedad.nombre,
                        lineas=[
                            "Esta isla está libre.",
                            f"Precio: ${propiedad.precio_actual}"
                        ],
                        opciones=[
                            "[C] Comprar isla",
                            "[N] Pasar turno"
                        ]
                    )

                elif accion == "preguntar_mejora":
                    self.estado = "decidiendo_mejora"

                    self._abrir_modal(
                        titulo=propiedad.nombre,
                        lineas=[
                            "Esta isla ya te pertenece.",
                            f"Nivel actual: {propiedad.nivel_mejora}",
                            f"Costo mejora: ${propiedad.calcular_costo_mejora()}"
                        ],
                        opciones=[
                            "[M] Mejorar isla",
                            "[N] No mejorar"
                        ]
                    )

                elif accion == "preguntar_recompra":
                    impuesto = resultado.get("impuesto")
                    recompra = resultado.get("recompra")

                    # Primero paga impuesto. Si no alcanza para impuesto + recompra,
                    # no se muestra opción de recomprar.
                    if not jugador_actual.puede_pagar(impuesto + recompra):
                        self.detalle_casilla = self.cell_resolver.property_rules.pagar_impuesto(
                            jugador_actual,
                            propiedad
                        )
                        self.mensaje = f"{self.detalle_casilla} No tiene fondos para recomprar."
                        self.mensaje_temporal_tiempo = pygame.time.get_ticks()

                        self.movement_manager.limpiar_ultima_casilla()
                        self.turn_manager.siguiente_turno()
                        self.estado = "esperando_lanzamiento"
                        return

                    self.estado = "decidiendo_recompra"

                    self._abrir_modal(
                        titulo=propiedad.nombre,
                        lineas=[
                            f"Dueño: {propiedad.dueno.nombre}",
                            f"Impuesto: ${impuesto}",
                            f"Recompra: ${recompra}"
                        ],
                        opciones=[
                            "[R] Pagar y recomprar",
                            "[N] Solo pagar impuesto"
                        ]
                    )

                elif accion == "preguntar_compra_poneglyph":
                    precio = resultado.get("precio")

                    if not jugador_actual.puede_pagar(precio):
                        self.detalle_casilla = (
                            f"{jugador_actual.nombre} no tiene fondos suficientes para comprar {propiedad.nombre}."
                        )
                        self.mensaje = self.detalle_casilla
                        self.mensaje_temporal_tiempo = pygame.time.get_ticks()

                        self.movement_manager.limpiar_ultima_casilla()
                        self.turn_manager.siguiente_turno()
                        self.estado = "esperando_lanzamiento"
                        return

                    self.estado = "decidiendo_compra_poneglyph"

                    self._abrir_modal(
                        titulo=propiedad.nombre,
                        lineas=[
                            "Road Poneglyph especial.",
                            f"Precio: ${precio}",
                            "No se puede recomprar."
                        ],
                        opciones=[
                            "[C] Comprar Road Poneglyph",
                            "[N] Pasar turno"
                        ]
                    )

                elif accion == "seleccionar_isla_yonkou":
                    self.estado = "seleccionando_yonkou"
                    self.propiedades_yonkou_disponibles = resultado.get("propiedades", [])

                    self._abrir_modal(
                        titulo="Yonkou",
                        lineas=[
                            "Elige una de tus islas marcadas en rojo",
                            "para aplicar el Bounty Yonkou."
                        ],
                        opciones=[
                            "Haz clic sobre una isla marcada"
                        ]
                    )

                self.movement_manager.limpiar_ultima_casilla()
                return

            # Casillas sin modal: descanso, salida, cárcel normal, etc.
            if self.mensaje_salida_pendiente:
                self.mensaje = f"{self.mensaje_salida_pendiente} {resultado['mensaje']}"
                self.mensaje_salida_pendiente = ""
            else:
                self.mensaje = resultado["mensaje"]

            self.mensaje_temporal_tiempo = pygame.time.get_ticks()
            self.movement_manager.limpiar_ultima_casilla()

        self.turn_manager.siguiente_turno()
        self.estado = "esperando_lanzamiento"

    def _dibujar(self):
        """
        Dibuja todo en pantalla.
        """

        self.pantalla.blit(self.fondo, (0, 0))
        self.pantalla.blit(self.tablero, (self.board_x, self.board_y))

        self._dibujar_casilla_yonkou()
        self._dibujar_casillas_seleccion_yonkou()

        self._dibujar_jugadores()
        self._dibujar_paneles_jugadores()
        self._dibujar_dados_centro()
        self._dibujar_msgbox()
        self._dibujar_modal_decision()

        pygame.display.flip()        

    def _dibujar_casilla_yonkou(self):
        if not self.casilla_yonkou:
            return

        for casilla in self.board_manager.obtener_todas_las_casillas():
            if casilla.referencia == self.casilla_yonkou:
                pygame.draw.rect(
                    self.pantalla,
                    (255, 215, 0),
                    (casilla.x, casilla.y, casilla.ancho, casilla.alto),
                    width=6,
                    border_radius=6
                )
                break                

    def _dibujar_casilla_yonkou(self):
        if not self.casilla_yonkou:
            return

        for casilla in self.board_manager.obtener_todas_las_casillas():
            if casilla.referencia == self.casilla_yonkou:
                pygame.draw.rect(
                    self.pantalla,
                    (255, 215, 0),
                    (casilla.x, casilla.y, casilla.ancho, casilla.alto),
                    width=6,
                    border_radius=6
                )
                break

    def _dibujar_casillas_seleccion_yonkou(self):
        if self.estado != "seleccionando_yonkou":
            return

        referencias = [p.referencia for p in self.propiedades_yonkou_disponibles]

        for casilla in self.board_manager.obtener_todas_las_casillas():
            if casilla.referencia in referencias:
                pygame.draw.rect(
                    self.pantalla,
                    (255, 0, 0),
                    (casilla.x, casilla.y, casilla.ancho, casilla.alto),
                    width=4,
                    border_radius=6
                )

    def _dibujar_modal_decision(self):
        if self.estado not in ["decidiendo_compra", "decidiendo_mejora", "decidiendo_recompra", "decidiendo_compra_poneglyph", "decidiendo_yonkou", "seleccionando_yonkou", "mostrando_evento"]:
            return

        ancho_modal = 430
        alto_modal = 230

        x = (self.ancho - ancho_modal) // 2
        y = (self.alto - alto_modal) // 2

        pygame.draw.rect(
            self.pantalla,
            (18, 18, 28),
            (x, y, ancho_modal, alto_modal),
            border_radius=18
        )

        pygame.draw.rect(
            self.pantalla,
            (230, 190, 80),
            (x, y, ancho_modal, alto_modal),
            width=3,
            border_radius=18
        )

        self._dibujar_texto_centrado(
            self.modal_titulo,
            x + ancho_modal // 2,
            y + 35,
            size=26,
            color=(255, 230, 130)
        )

        pos_y = y + 65

        for linea in self.modal_lineas:
            self._dibujar_texto_centrado(
                linea,
                x + ancho_modal // 2,
                pos_y,
                size=17,
                color=(255, 255, 255)
            )
            pos_y += 28

        for opcion in self.modal_opciones:
            self._dibujar_texto_centrado(
                opcion,
                x + ancho_modal // 2,
                pos_y,
                size=16,
                color=(180, 220, 255)
            )
            pos_y += 26

    def _dibujar_jugadores(self):
        """
        Dibuja las fichas dentro del tablero.
        Si hay asset, dibuja el barco.
        Si no hay asset, dibuja un círculo temporal.
        """

        colores = [
            (255, 80, 80),
            (80, 190, 60),
            (80, 160, 255),
            (255, 220, 80),
        ]

        for i, jugador in enumerate(self.jugadores):
            x, y = self.movement_manager.obtener_posicion_con_efecto_barco(jugador)

            if getattr(jugador, "ficha", None):
                self.pantalla.blit(jugador.ficha, (x, y))
            else:
                color = colores[i % len(colores)]

                pygame.draw.circle(
                    self.pantalla,
                    color,
                    (int(x) + 24, int(y) + 24),
                    22
                )

                pygame.draw.circle(
                    self.pantalla,
                    (20, 20, 20),
                    (int(x) + 24, int(y) + 24),
                    22,
                    2
                )

                self._dibujar_texto(
                    str(i + 1),
                    int(x) + 16,
                    int(y) + 8,
                    size=22,
                    color=(0, 0, 0)
                )

    def _dibujar_paneles_jugadores(self):
        """
        Dibuja los 4 jugadores en las esquinas de la pantalla.
        """

        posiciones_paneles = [
            (25, 25),
            (self.ancho - 305, 25),
            (25, self.alto - 105),
            (self.ancho - 305, self.alto - 105)
        ]

        colores = [
            (220, 40, 30),
            (80, 190, 60),
            (220, 40, 30),
            (220, 40, 30)
        ]

        for i, jugador in enumerate(self.jugadores):
            x, y = posiciones_paneles[i]
            color = colores[i % len(colores)]

            es_turno = jugador == self.turn_manager.obtener_jugador_actual()

            self._dibujar_panel_jugador(
                jugador=jugador,
                x=x,
                y=y,
                color=color,
                es_turno=es_turno
            )

    def _dibujar_panel_jugador(self, jugador, x, y, color, es_turno=False):
        """
        Dibuja una tarjeta pequeña de jugador.
        """

        ancho_panel = 280
        alto_panel = 80

        if es_turno:
            borde_color = (255, 230, 90)
            borde_width = 4
        else:
            borde_color = (25, 25, 25)
            borde_width = 2

        pygame.draw.rect(
            self.pantalla,
            color,
            (x, y, ancho_panel, alto_panel),
            border_radius=18
        )

        pygame.draw.rect(
            self.pantalla,
            borde_color,
            (x, y, ancho_panel, alto_panel),
            width=borde_width,
            border_radius=18
        )

        pygame.draw.circle(
            self.pantalla,
            (240, 220, 120),
            (x + 40, y + 40),
            32
        )

        pygame.draw.circle(
            self.pantalla,
            (30, 30, 30),
            (x + 40, y + 40),
            32,
            3
        )

        if getattr(jugador, "imagen", None):
            imagen_rect = jugador.imagen.get_rect(center=(x + 40, y + 40))
            self.pantalla.blit(jugador.imagen, imagen_rect)
        else:
            self._dibujar_texto(
                jugador.nombre[0].upper(),
                x + 28,
                y + 20,
                size=28,
                color=(30, 30, 30)
            )

        self._dibujar_texto(
            jugador.nombre,
            x + 90,
            y + 10,
            size=18,
            color=(20, 20, 20)
        )

        pygame.draw.rect(
            self.pantalla,
            (20, 20, 25),
            (x + 90, y + 38, 165, 28),
            border_radius=12
        )

        self._dibujar_texto(
            f"${jugador.dinero}",
            x + 105,
            y + 42,
            size=15,
            color=(255, 255, 255)
        )

    def _dibujar_dados_centro(self):
        """
        Dibuja los dados en el centro del tablero, sin fondo.
        """

        centro_x = self.board_x + self.board_size // 2
        centro_y = self.board_y + self.board_size // 2

        dado_ancho = 72
        separacion = 20
        total_ancho = dado_ancho * 2 + separacion

        x = centro_x - total_ancho // 2
        y = centro_y - 45

        self.dice.dibujar(
            self.pantalla,
            x,
            y,
            separacion=separacion
        )

    def _dibujar_msgbox(self):
        """
        Dibuja un cuadro pequeño de mensaje debajo del tablero.
        """

        ancho_box = 520
        alto_box = 46

        x = (self.ancho - ancho_box) // 2
        y = self.board_y + self.board_size + 8

        if y + alto_box > self.alto:
            y = self.alto - alto_box - 8

        pygame.draw.rect(
            self.pantalla,
            (20, 20, 28),
            (x, y, ancho_box, alto_box),
            border_radius=14
        )

        pygame.draw.rect(
            self.pantalla,
            (230, 190, 80),
            (x, y, ancho_box, alto_box),
            width=2,
            border_radius=14
        )

        texto = str(self.mensaje)

        if len(texto) > 72:
            texto = texto[:69] + "..."

        self._dibujar_texto(
            texto,
            x + 15,
            y + 13,
            size=14,
            color=(255, 255, 255)
        )

    def _dibujar_texto(self, texto, x, y, size=24, color=(255, 255, 255)):
        """
        Dibuja texto simple en pantalla.
        """

        fuente = pygame.font.SysFont("arial", size, bold=True)
        render = fuente.render(str(texto), True, color)
        self.pantalla.blit(render, (x, y))

    def _dibujar_texto_centrado(self, texto, centro_x, y, size=24, color=(255, 255, 255)):
        fuente = pygame.font.SysFont("arial", size, bold=True)
        render = fuente.render(str(texto), True, color)
        rect = render.get_rect(center=(centro_x, y))
        self.pantalla.blit(render, rect)