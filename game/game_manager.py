import os
import random
import pygame

from game.dice import Dice
from game.turn_manager import TurnManager
from game.board_manager import BoardManager
from game.movement_manager import MovementManager
from game.cell_resolver import CellResolver
from ui.components.purchase_modal import PurchaseModal
from ui.components.event_modal import EventModal
from models.casilla import TIPO_EVENTO, TIPO_DESCANSO, TIPO_CARCEL
from ui.components.cell_info_panel import CellInfoPanel
from services.price_service import calcular_bono_lagrange
from services.sound_service import SoundService

class GameManager:
    def __init__(
        self,
        jugadores,
        ancho=1280,
        alto=720,
        board_size=None,
        board_path="assets/images/board/tablero.png",
        background_path="assets/images/board/background.png",
        ventana_completa=True
    ):
        pygame.init()
        self.sounds = SoundService()
        self.sounds.play_music("tablero")
        self.board_path = board_path
        self.background_path = background_path

        if ventana_completa:
            info = pygame.display.Info()
            self.ancho = info.current_w
            self.alto = info.current_h
            self.pantalla = pygame.display.set_mode(
                (self.ancho, self.alto),
                pygame.NOFRAME
            )
        else:
            self.ancho = ancho
            self.alto = alto
            self.pantalla = pygame.display.set_mode(
                (self.ancho, self.alto),
                pygame.RESIZABLE
            )

        pygame.display.set_caption("Dokusen Eland - Ruta del Rey Pirata")

        self.reloj = pygame.time.Clock()
        self.running = True

        self.jugadores = jugadores
        self.ficha_size = 64

        if board_size is None:
            self.board_size = self._calcular_tamano_tablero()
        else:
            self.board_size = board_size

        self.board_x = (self.ancho - self.board_size) // 2
        self.board_y = (self.alto - self.board_size) // 2

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

        self.purchase_modal = PurchaseModal(
            ancho_pantalla=self.ancho,
            alto_pantalla=self.alto,
            cargar_imagen_segura=self._cargar_imagen_segura
        )

        self.event_modal = EventModal(
            ancho_pantalla=self.ancho,
            alto_pantalla=self.alto,
            cargar_imagen_segura=self._cargar_imagen_segura
        )

        self.cell_info_panel = CellInfoPanel(
            ancho_pantalla=self.ancho,
            alto_pantalla=self.alto
        )

        self.estado = "esperando_lanzamiento"
        self.accion_pendiente = None
        self.propiedad_pendiente = None
        self.evento_cierra_turno = True

        self.casilla_yonkou = None
        self.propiedades_yonkou_disponibles = []
        self.propiedades_destruibles = []

        self.bienes_venta_bancarrota = []
        self.jugador_en_bancarrota = None
        self.boton_victoria_rect = None
        self.mensaje_temporal_tiempo = 0
        self.mensaje_salida_pendiente = ""
        self.mensaje = "Presiona ESPACIO para lanzar los dados"
        self.detalle_casilla = ""
        self.alerta_lagrange = ""
        self.alerta_lagrange_tiempo = 0
        self.alerta_lagrange_duracion = 3500
        self.ganador = None
        self.motivo_victoria = ""

        self.imagen_victoria = self._cargar_imagen_segura(
            "assets/images/UI_Eventos/win.png",
            size=(500, 260),
            usar_alpha=True
        )

        self.volver_menu_pendiente = False
        self.on_volver_menu = None

        self.dado_1 = 0
        self.dado_2 = 0
        self.suma_dados = 0

        self.costo_salida_prision = 150
        self.max_turnos_prision = 3

        self.fondo = self._cargar_fondo()
        self.tablero = self._cargar_tablero()

        self._preparar_jugadores()
        self._definir_orden_inicial()

    # ============================================================
    # CARGA / CONFIGURACIÓN
    # ============================================================

    def _cargar_imagen_segura(self, path, size=None, usar_alpha=False):
        if not path or not os.path.exists(path):
            return None

        if usar_alpha:
            imagen = pygame.image.load(path).convert_alpha()
        else:
            imagen = pygame.image.load(path).convert()

        if size:
            imagen = pygame.transform.smoothscale(imagen, size)

        return imagen
    def _avanzar_turno(self, mostrar_alerta_lagrange=True):
        turno_anterior = self.turn_manager.turno_numero

        jugador_siguiente = self.turn_manager.siguiente_turno()

        turno_nuevo = self.turn_manager.turno_numero

        if turno_nuevo > turno_anterior:
            total_islas = self.cell_resolver.property_rules.actualizar_todas_con_lagrange(
                turno_nuevo
            )

            total_poneglyphs = self.cell_resolver.poneglyph_rules.actualizar_todos_con_lagrange(
                turno_nuevo
            )

            if mostrar_alerta_lagrange:
                self.alerta_lagrange = (
                    f"Turno {turno_anterior} terminado. "
                    f"Precios actualizados por Lagrange para el turno {turno_nuevo}."
                )
                self.alerta_lagrange_tiempo = pygame.time.get_ticks()

        return jugador_siguiente
    def _calcular_tamano_tablero(self):
        margen_superior = 10
        margen_inferior = 10
        margen_lateral = 10

        espacio_horizontal = self.ancho - (margen_lateral * 2)
        espacio_vertical = self.alto - margen_superior - margen_inferior

        return int(min(espacio_horizontal, espacio_vertical))

    def _cargar_fondo(self):
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
        for i, jugador in enumerate(self.jugadores):
            if not hasattr(jugador, "turnos_en_prision"):
                jugador.turnos_en_prision = 0

            if not hasattr(jugador, "es_yonkou"):
                jugador.es_yonkou = False

            jugador.imagen = self._cargar_imagen_segura(
                getattr(jugador, "ruta_imagen", ""),
                size=(64, 64),
                usar_alpha=True
            )

            jugador.ficha = self._cargar_imagen_segura(
                getattr(jugador, "ruta_ficha", ""),
                size=(self.ficha_size, self.ficha_size),
                usar_alpha=True
            )

            jugador.carta = self._cargar_imagen_segura(
                getattr(jugador, "ruta_carta", ""),
                size=(330, 105),
                usar_alpha=True
            )

            x, y = self.board_manager.obtener_coordenadas_ficha(
                posicion=0,
                indice_jugador=i,
                ficha_size=self.ficha_size
            )

            jugador.establecer_coordenadas(x, y)

    def _definir_orden_inicial(self):
        resultados = self.turn_manager.definir_orden_inicial()

        print("\n=== ORDEN INICIAL ===")
        for item in resultados:
            jugador = item["jugador"]
            print(f"{jugador.nombre}: {item['dado_1']} + {item['dado_2']} = {item['suma']}")

        print("\n=== ORDEN FINAL ===")
        for jugador in self.turn_manager.obtener_orden_jugadores():
            print(f"Orden {jugador.orden_turno}: {jugador.nombre}")

    # ============================================================
    # LOOP PRINCIPAL
    # ============================================================

    def run(self):
        while self.running:
            dt = self.reloj.tick(60) / 1000
            self._manejar_eventos()
            self._actualizar(dt)
            self._dibujar()

        pygame.quit()

    def _manejar_eventos(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.estado == "fin_partida":
                    self._manejar_click_victoria(event.pos)
                    continue

                if event.button == 3:
                    self._manejar_click_info_casilla(event.pos)
                    continue
                
                if self.estado in [
                    "modal_compra_isla",
                    "modal_compra_poneglyph",
                    "modal_recompra",
                    "modal_mejora"
                ]:
                    self._manejar_click_modal_compra(event.pos)
                    continue

                if self.estado in [
                    "modal_evento",
                    "modal_yonkou_info",
                    "modal_destruccion_info",
                    "modal_prision"
                ]:
                    self._manejar_click_event_modal(event.pos)
                    continue

                if self.estado == "seleccionando_venta_bancarrota":
                    self._manejar_click_venta_bancarrota(event.pos)
                    continue

                if self.estado == "seleccionando_yonkou":
                    self._manejar_click_yonkou(event.pos)
                    continue

                if self.estado == "seleccionando_destruccion":
                    self._manejar_click_destruccion(event.pos)
                    continue

 

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    continue

                if event.key == pygame.K_F4:
                    self._forzar_victoria_poneglyph()
                    continue

                if event.key == pygame.K_SPACE:
                    self._intentar_lanzar_dados()
                    continue

    def _manejar_click_info_casilla(self, pos_mouse):
        """
        Abre la pestaña lateral con información de la casilla clickeada.
        """

        for casilla in self.board_manager.obtener_todas_las_casillas():
            rect = pygame.Rect(casilla.x, casilla.y, casilla.ancho, casilla.alto)

            if rect.collidepoint(pos_mouse):
                titulo, subtitulo, lineas = self._construir_info_casilla(casilla)
                self.cell_info_panel.abrir(titulo, subtitulo, lineas)
                return

        self.cell_info_panel.cerrar()


    def _construir_info_casilla(self, casilla):
        titulo = casilla.nombre
        subtitulo = f"Tipo: {casilla.tipo}"
        lineas = [
            f"Posición: {casilla.posicion}",
            f"Referencia: {casilla.referencia}"
        ]

        if casilla.tipo == "isla":
            propiedad = self.cell_resolver.property_rules.obtener_propiedad(casilla.referencia)

            if propiedad is None:
                lineas.append("Sin datos de propiedad.")
                return titulo, subtitulo, lineas

            dueno = propiedad.dueno.nombre if propiedad.dueno else "Libre"

            lineas = [
                f"Dueño: {dueno}",
                f"Grupo: {propiedad.grupo}",
                f"Precio actual: ${propiedad.precio_actual}",
                f"Nivel mejora: {propiedad.nivel_mejora}",
                f"Costo mejora: ${propiedad.calcular_costo_mejora()}",
                f"Impuesto: ${propiedad.calcular_impuesto()}",
                f"Recompra: ${propiedad.calcular_recompra()}",
                f"Yonkou: {'Sí' if propiedad.tiene_yonkou else 'No'}"
            ]

            return titulo, subtitulo, lineas

        if casilla.tipo == "road_poneglyph":
            poneglyph = self.cell_resolver.poneglyph_rules.obtener_poneglyph(casilla.referencia)

            if poneglyph is None:
                lineas.append("Sin datos de Road Poneglyph.")
                return titulo, subtitulo, lineas

            dueno = poneglyph.dueno.nombre if poneglyph.dueno else "Libre"

            lineas = [
                f"Dueño: {dueno}",
                f"Precio actual: ${poneglyph.precio_actual}",
                "Tipo especial: Road Poneglyph",
                "Reúne 4 para ganar.",
                "No puede ser recomprado."
            ]

            return titulo, subtitulo, lineas

        if casilla.tipo == "evento":
            if casilla.referencia == "cofre_recompensa":
                lineas = [
                    "Evento positivo.",
                    "Entrega dinero al jugador.",
                    "Se muestra en panel de evento."
                ]
            elif casilla.referencia == "evento_riesgo":
                lineas = [
                    "Evento 50/50.",
                    "Puede ser bueno o malo.",
                    "Puede afectar dinero, islas o Poneglyphs."
                ]
            else:
                lineas = ["Evento especial."]

            return titulo, subtitulo, lineas

        if casilla.tipo == "descanso":
            lineas = [
                "Casilla de descanso.",
                "Entrega un bono de dinero.",
                "No requiere decisión."
            ]

            return titulo, subtitulo, lineas

        if casilla.tipo == "carcel":
            lineas = [
                "Casilla de prisión.",
                "Puedes salir con par.",
                "También puedes pagar salida.",
                "Al tercer intento sales automático."
            ]

            return titulo, subtitulo, lineas

        if casilla.tipo == "yonko":
            lineas = [
                "Casilla Yonkou.",
                "Permite aplicar Bounty Yonkou.",
                "Aumenta el valor de una isla propia."
            ]

            return titulo, subtitulo, lineas

        if casilla.tipo == "salida":
            lineas = [
                "Casilla inicial.",
                "Al pasar por aquí recibes dinero."
            ]

            return titulo, subtitulo, lineas

        return titulo, subtitulo, lineas
    def _manejar_click_victoria(self, pos_mouse):
        if self.boton_victoria_rect and self.boton_victoria_rect.collidepoint(pos_mouse):
            if hasattr(self, "sounds"):
                self.sounds.play_effect("click")

            self._volver_al_menu_desde_victoria()
    def _actualizar_mercado_lagrange(self):
        turno_actual = self.turn_manager.turno_numero

        total_islas = self.cell_resolver.property_rules.actualizar_todas_con_lagrange(
            turno_actual
        )

        total_poneglyphs = self.cell_resolver.poneglyph_rules.actualizar_todos_con_lagrange(
            turno_actual
        )

        self.alerta_lagrange = (
            f"Turno {turno_actual}: precios actualizados por Lagrange "
            f"({total_islas} islas y {total_poneglyphs} Poneglyphs)."
        )
        self.alerta_lagrange_tiempo = pygame.time.get_ticks()

    def _forzar_victoria_poneglyph(self):
        jugador_actual = self.turn_manager.obtener_jugador_actual()
        jugador_actual.road_poneglyphs = [1, 2, 3, 4]
        self.ganador = jugador_actual
        self.motivo_victoria = "reunió los 4 Road Poneglyphs"
        self.estado = "fin_partida"
        self.sounds.stop_music()
        self.sounds.play_effect("victoria")
        self.mensaje = f"{jugador_actual.nombre} ganó: {self.motivo_victoria}."
        self.detalle_casilla = ""
        print(self.mensaje)

    def _volver_al_menu_desde_victoria(self):
        """
        Cuando exista el menú principal, aquí se debe cambiar de pantalla.
        Por ahora solo cierra la ventana del juego.
        """

        self.volver_menu_pendiente = True
        self.running = False

    # ============================================================
    # TURNOS / DADOS / PRISIÓN
    # ============================================================

    def _intentar_lanzar_dados(self):
        if self.estado == "fin_partida":
            return

        if self.estado != "esperando_lanzamiento":
            return

        if self.dice.esta_animando() or self.movement_manager.esta_moviendose():
            return

        jugador_actual = self.turn_manager.obtener_jugador_actual()

        if not getattr(jugador_actual, "activo", True):
            self._saltar_jugadores_eliminados()
            return

        if getattr(jugador_actual, "turnos_perdidos", 0) > 0:
            jugador_actual.actualizar_turno_perdido()
            self._abrir_evento_simple(
                titulo="Turno perdido",
                mensaje=f"{jugador_actual.nombre} pierde este turno.",
                tipo="riesgo_malo",
                cerrar_turno=True
            )
            return

        if getattr(jugador_actual, "en_carcel", False):
            self._abrir_modal_prision(jugador_actual)
            return

        self._iniciar_lanzamiento_normal(jugador_actual)

    def _iniciar_lanzamiento_normal(self, jugador):
        self.mensaje_temporal_tiempo = 0
        self.detalle_casilla = ""
        self.mensaje_salida_pendiente = ""
        self.sounds.play_effect("dados")
        self.dice.iniciar_lanzamiento()
        self.estado = "animando_dados"
        self.mensaje = f"{jugador.nombre} está lanzando los dados..."

    def _abrir_modal_prision(self, jugador):
        intentos = getattr(jugador, "turnos_en_prision", 0)

        self.event_modal.abrir(
            titulo="Prisión",
            mensaje=(
                f"{jugador.nombre} está en prisión. Intento {intentos + 1} de {self.max_turnos_prision}. "
                f"Puedes pagar ${self.costo_salida_prision} para salir o tirar dados. "
                "Si sacas par, sales y avanzas."
            ),
            tipo="prision",
            opciones=[
                {"texto": "Tirar dados", "accion": "tirar_prision", "estilo": "normal"},
                {"texto": f"Pagar ${self.costo_salida_prision}", "accion": "pagar_prision", "estilo": "verde"}
            ]
        )

        self.estado = "modal_prision"
        self.mensaje = f"{jugador.nombre} está en prisión."

    def _manejar_click_event_modal(self, pos_mouse):
        accion = self.event_modal.manejar_click(pos_mouse)

        if accion is None:
            return
        self.sounds.play_effect("click")
        jugador_actual = self.turn_manager.obtener_jugador_actual()

        if self.estado == "modal_prision":
            self._manejar_accion_prision(jugador_actual, accion)
            return

        if accion in ["continuar", "cerrar"]:
            self.event_modal.cerrar()

            if self.evento_cierra_turno:
                self._finalizar_decision()
            else:
                self.estado = "esperando_lanzamiento"
            return

        if accion == "elegir_yonkou":
            self.event_modal.cerrar()
            self.estado = "seleccionando_yonkou"
            self.mensaje = "Elige una isla para aplicar Bounty Yonkou."
            return

        if accion == "elegir_destruccion":
            self.event_modal.cerrar()
            self.estado = "seleccionando_destruccion"
            self.mensaje = "Elige una propiedad enemiga para destruir."
            return

    def _manejar_accion_prision(self, jugador, accion):
        if accion == "pagar_prision":
            if not jugador.puede_pagar(self.costo_salida_prision):
                self.event_modal.mostrar_feedback("No tienes dinero suficiente para pagar la salida.")
                return

            jugador.restar_dinero(self.costo_salida_prision)
            self._liberar_de_prision(jugador)
            self.event_modal.cerrar()
            self.mensaje = f"{jugador.nombre} pagó ${self.costo_salida_prision} y salió de prisión."
            self._iniciar_lanzamiento_normal(jugador)
            return

        if accion == "tirar_prision":
            self.event_modal.cerrar()
            self.dice.iniciar_lanzamiento()
            self.sounds.play_effect("dados")
            self.estado = "animando_dados_prision"
            self.mensaje = f"{jugador.nombre} intenta sacar par para salir de prisión..."
            return

    def _actualizar(self, dt):
        self.dice.actualizar()
        self.movement_manager.actualizar(dt)

        if self.estado == "animando_dados":
            self._actualizar_animacion_dados()

        elif self.estado == "animando_dados_prision":
            self._actualizar_animacion_dados_prision()

        elif self.estado == "moviendo_ficha":
            self._actualizar_movimiento_ficha()

        self._limpiar_mensaje_temporal()

    def _actualizar_animacion_dados(self):
        if self.dice.esta_animando():
            return

        self.dado_1, self.dado_2, self.suma_dados = self.dice.obtener_resultados()
        self.turn_manager.registrar_resultado_dados(self.dado_1, self.dado_2)

        jugador_actual = self.turn_manager.obtener_jugador_actual()
        self.mensaje = f"{jugador_actual.nombre} sacó {self.dado_1} + {self.dado_2} = {self.suma_dados}"
        self._iniciar_movimiento_con_dados(jugador_actual)

    def _actualizar_animacion_dados_prision(self):
        if self.dice.esta_animando():
            return

        self.dado_1, self.dado_2, self.suma_dados = self.dice.obtener_resultados()
        self.turn_manager.registrar_resultado_dados(self.dado_1, self.dado_2)

        jugador_actual = self.turn_manager.obtener_jugador_actual()
        saco_par = self.dado_1 == self.dado_2

        if saco_par:
            self._liberar_de_prision(jugador_actual)
            self.mensaje = (
                f"{jugador_actual.nombre} sacó par "
                f"({self.dado_1} + {self.dado_2}) y sale de prisión."
            )
            self._iniciar_movimiento_con_dados(jugador_actual)
            return

        self._sumar_turno_prision(jugador_actual)

        if getattr(jugador_actual, "turnos_en_prision", 0) >= self.max_turnos_prision:
            self._liberar_de_prision(jugador_actual)
            self.mensaje = (
                f"{jugador_actual.nombre} no sacó par, pero cumplió 3 intentos "
                "y sale automáticamente."
            )
            self._iniciar_movimiento_con_dados(jugador_actual)
            return

        self._cerrar_turno_con_log(
            f"{jugador_actual.nombre} sacó {self.dado_1} + {self.dado_2}. "
            f"No fue par, así que permanece en prisión. "
            f"Intento {jugador_actual.turnos_en_prision}/{self.max_turnos_prision}."
        )

    def _iniciar_movimiento_con_dados(self, jugador):
        if self.board_manager.paso_por_salida(jugador.posicion, self.suma_dados):
            resultado_bono = calcular_bono_lagrange(
                "salida",
                self.turn_manager.turno_numero
            )

            bono = int(resultado_bono["valor_estimado"])
            jugador.sumar_dinero(bono)
            self.sounds.play_effect("dinero")
            self.mensaje_salida_pendiente = (
                f"{jugador.nombre} pasó por Salida y recibió ${bono} Berries por Lagrange."
            )

            self._mostrar_alerta_superior(self.mensaje_salida_pendiente)
        else:
            self.mensaje_salida_pendiente = ""

        self.detalle_casilla = "Moviendo ficha..."
        self.movement_manager.iniciar_movimiento(
            jugador=jugador,
            pasos=self.suma_dados,
            indice_jugador=self.turn_manager.indice_turno_actual,
            ficha_size=self.ficha_size
        )
        self.estado = "moviendo_ficha"

    def _limpiar_mensaje_temporal(self):
        if self.mensaje_temporal_tiempo <= 0:
            return

        tiempo_actual = pygame.time.get_ticks()

        if tiempo_actual - self.mensaje_temporal_tiempo >= 3000:
            self.mensaje = "Presiona ESPACIO para lanzar los dados"
            self.detalle_casilla = ""
            self.mensaje_temporal_tiempo = 0

    def _enviar_a_prision(self, jugador):
        if hasattr(jugador, "enviar_a_prision"):
            jugador.enviar_a_prision()
        else:
            jugador.en_carcel = True
            jugador.turnos_en_prision = 0

    def _liberar_de_prision(self, jugador):
        if hasattr(jugador, "liberar_de_prision"):
            jugador.liberar_de_prision()
        else:
            jugador.en_carcel = False
            jugador.turnos_en_prision = 0

    def _sumar_turno_prision(self, jugador):
        if hasattr(jugador, "sumar_turno_prision"):
            jugador.sumar_turno_prision()
        else:
            jugador.turnos_en_prision = getattr(jugador, "turnos_en_prision", 0) + 1

    # ============================================================
    # RESOLUCIÓN DE CASILLAS
    # ============================================================

    def _actualizar_movimiento_ficha(self):
        if self.movement_manager.esta_moviendose():
            return

        casilla_final = self.movement_manager.obtener_ultima_casilla_final()
        jugador_actual = self.turn_manager.obtener_jugador_actual()

        if not casilla_final:
            self._avanzar_turno()
            self.estado = "esperando_lanzamiento"
            return

        if casilla_final.tipo == TIPO_EVENTO:
            self._manejar_casilla_evento(jugador_actual, casilla_final)
            self.movement_manager.limpiar_ultima_casilla()
            return

        if casilla_final.tipo == TIPO_DESCANSO:
            self._manejar_casilla_descanso(jugador_actual)
            self.movement_manager.limpiar_ultima_casilla()
            return

        if casilla_final.tipo == TIPO_CARCEL:
            self._manejar_casilla_prision(jugador_actual)
            self.movement_manager.limpiar_ultima_casilla()
            return

        turno_actual = self.turn_manager.turno_numero

        resultado = self.cell_resolver.resolver_casilla(
            jugador_actual,
            casilla_final,
            turno_actual
        )
        accion = resultado.get("accion")
        self.detalle_casilla = resultado.get("mensaje", "")

        if accion == "pagar_impuesto_poneglyph":
            self._resolver_impuesto_poneglyph(jugador_actual, resultado)
            self.movement_manager.limpiar_ultima_casilla()
            return

        if accion in [
            "preguntar_compra",
            "preguntar_mejora",
            "preguntar_recompra",
            "preguntar_compra_poneglyph",
            "seleccionar_isla_yonkou"
        ]:
            self._preparar_accion_pendiente(jugador_actual, accion, resultado)
            self.movement_manager.limpiar_ultima_casilla()
            return

        self._mostrar_resultado_simple(resultado)
        self.movement_manager.limpiar_ultima_casilla()
        self._finalizar_decision()

    def _resolver_impuesto_poneglyph(self, jugador, resultado):
        propiedad = resultado.get("propiedad")
        self.detalle_casilla = self.cell_resolver.poneglyph_rules.pagar_impuesto_poneglyph(
            jugador,
            propiedad
        )

        self._finalizar_decision()

    def _preparar_accion_pendiente(self, jugador, accion, resultado):
        self.accion_pendiente = accion
        self.propiedad_pendiente = resultado.get("propiedad")
        propiedad = self.propiedad_pendiente

        if accion == "preguntar_compra":
            self._abrir_compra_isla(jugador, propiedad)
            return

        if accion == "preguntar_mejora":
            self._abrir_mejora_isla(jugador, propiedad)
            return

        if accion == "preguntar_recompra":
            self._abrir_recompra(jugador, propiedad, resultado)
            return

        if accion == "preguntar_compra_poneglyph":
            self._abrir_compra_poneglyph(jugador, propiedad, resultado)
            return

        if accion == "seleccionar_isla_yonkou":
            self._abrir_info_yonkou(jugador, resultado.get("propiedades", []))
            return

    def _abrir_compra_isla(self, jugador, propiedad):
        precio_base = self._calcular_precio_compra_con_nivel(propiedad, 1)
        precio_nivel_2 = self._calcular_precio_compra_con_nivel(propiedad, 2)
        precio_nivel_3 = self._calcular_precio_compra_con_nivel(propiedad, 3)

        if not jugador.puede_pagar(precio_base):
            self._cerrar_turno_con_log(
                f"{jugador.nombre} no tiene saldo suficiente para comprar {propiedad.nombre}."
            )
            return

        self.estado = "modal_compra_isla"
        self.purchase_modal.abrir_compra_isla(
            jugador=jugador,
            propiedad=propiedad,
            precios={
                "base": precio_base,
                "nivel_2": precio_nivel_2,
                "nivel_3": precio_nivel_3
            }
        )

    def _abrir_mejora_isla(self, jugador, propiedad):
        if not propiedad.puede_mejorarse():
            self._abrir_evento_simple(
                titulo="Mejora máxima",
                mensaje=f"{propiedad.nombre} ya tiene mejora máxima.",
                tipo="info",
                cerrar_turno=True
            )
            return

        self.estado = "modal_mejora"
        self.purchase_modal.abrir_mejora(jugador=jugador, propiedad=propiedad)

    def _abrir_recompra(self, jugador, propiedad, resultado):
        impuesto = resultado.get("impuesto", propiedad.calcular_impuesto())
        recompra = resultado.get("recompra", self._calcular_recompra(propiedad))

        self.estado = "modal_recompra"
        self.purchase_modal.abrir_pago_recompra(
            jugador=jugador,
            propiedad=propiedad,
            impuesto=impuesto,
            recompra=recompra
        )

    def _abrir_compra_poneglyph(self, jugador, propiedad, resultado):
        precio = resultado.get("precio")

        if precio is None:
            precio = self.cell_resolver.poneglyph_rules.calcular_precio_compra(jugador, propiedad)

        if not jugador.puede_pagar(precio):
            self._cerrar_turno_con_log(
                f"{jugador.nombre} no tiene fondos suficientes para comprar {propiedad.nombre}."
            )
            return

        self.estado = "modal_compra_poneglyph"
        self.purchase_modal.abrir_compra_poneglyph(
            jugador=jugador,
            propiedad=propiedad,
            precios={"base": precio}
        )

    def _mostrar_resultado_simple(self, resultado):
        if self.mensaje_salida_pendiente:
            texto = f"{self.mensaje_salida_pendiente} {resultado.get('mensaje', '')}"
            self.mensaje_salida_pendiente = ""
        else:
            texto = resultado.get("mensaje", "Presiona ESPACIO para lanzar los dados")

        self.mensaje = texto
        self.detalle_casilla = texto
        self.mensaje_temporal_tiempo = pygame.time.get_ticks()

    # ============================================================
    # EVENTOS / DESCANSO / PRISIÓN
    # ============================================================

    def _manejar_casilla_descanso(self, jugador):
        resultado_bono = calcular_bono_lagrange(
            "descanso",
            self.turn_manager.turno_numero
        )

        bono = int(resultado_bono["valor_estimado"])
        jugador.sumar_dinero(bono)
        self.sounds.play_effect("dinero")
        self._abrir_evento_simple(
            titulo="Descanso",
            mensaje=f"{jugador.nombre} descansó en una zona segura y recibió ${bono} Berries por Lagrange.",
            tipo="descanso",
            cerrar_turno=True
        )

    def _manejar_casilla_prision(self, jugador):
        self._enviar_a_prision(jugador)
        self.sounds.play_effect("prision")
        self._abrir_evento_simple(
            titulo="Prisión",
            mensaje=(
                f"{jugador.nombre} cayó en prisión. En sus próximos turnos deberá sacar par "
                f"o pagar ${self.costo_salida_prision} para salir."
            ),
            tipo="prision",
            cerrar_turno=True
        )

    def _manejar_casilla_evento(self, jugador, casilla):
        if casilla.referencia == "evento_riesgo":
            self._resolver_evento_riesgo(jugador)
            return

        self._resolver_evento_recompensa(jugador)

    def _resolver_evento_recompensa(self, jugador):
        resultado_bono = calcular_bono_lagrange(
            "cofre",
            self.turn_manager.turno_numero
        )

        cantidad = int(resultado_bono["valor_estimado"])
        jugador.sumar_dinero(cantidad)
        self.sounds.play_effect("cofre")

        self._abrir_evento_simple(
            titulo="Cofre Recompensa",
            mensaje=(
                f"Encontraste un tesoro en la ruta. "
                f"Recibes ${cantidad} Berries calculados por Lagrange."
            ),
            tipo="premio",
            cerrar_turno=True
        )

    def _resolver_evento_riesgo(self, jugador):
        es_bueno = random.choice([True, False])

        if es_bueno:
            self._resolver_riesgo_bueno(jugador)
        else:
            self._resolver_riesgo_malo(jugador)

    def _resolver_riesgo_malo(self, jugador):
        self.sounds.play_effect("evento_malo")
        evento = random.choices(
            ["perder_dinero", "perder_propiedad"],
            weights=[70, 30],
            k=1
        )[0]

        if evento == "perder_dinero":
            cantidad = random.choice([100, 150, 200, 250])
            jugador.restar_dinero(cantidad)
            self.sounds.play_effect("perder_dinero")
            self._abrir_evento_simple(
                titulo="Evento de Riesgo",
                mensaje=f"Una tormenta dañó tu barco. Pierdes ${cantidad} Berries.",
                tipo="riesgo_malo",
                cerrar_turno=True
            )
            return

        bienes = list(getattr(jugador, "propiedades", []))

        for poneglyph in self.cell_resolver.poneglyph_rules.poneglyphs.values():
            if poneglyph.dueno == jugador:
                bienes.append(poneglyph)

        if not bienes:
            cantidad = 150
            jugador.restar_dinero(cantidad)

            self._abrir_evento_simple(
                titulo="Evento de Riesgo",
                mensaje=(
                    f"No tenías propiedades ni Road Poneglyphs para perder. "
                    f"En su lugar, pierdes ${cantidad} Berries."
                ),
                tipo="riesgo_malo",
                cerrar_turno=True
            )
            return

        bien = random.choice(bienes)
        self._liberar_propiedad(bien)
        self.sounds.play_effect("destruir")

        self._abrir_evento_simple(
            titulo="Evento de Riesgo",
            mensaje=f"Una crisis te hizo perder {bien.nombre}. Ahora vuelve a estar libre.",
            tipo="riesgo_malo",
            cerrar_turno=True
        )

    def _resolver_riesgo_bueno(self, jugador):
        evento = random.choices(
            ["destruir_propiedad", "conseguir_yonkou", "ganar_dinero"],
            weights=[20, 30, 50],
            k=1
        )[0]

        if evento == "ganar_dinero":
            resultado_bono = calcular_bono_lagrange(
                "riesgo_bueno",
                self.turn_manager.turno_numero
            )

            cantidad = int(resultado_bono["valor_estimado"])
            jugador.sumar_dinero(cantidad)
            self.sounds.play_effect("dinero")

            self._abrir_evento_simple(
                titulo="Evento Favorable",
                mensaje=(
                    f"Encontraste recursos valiosos en la ruta. "
                    f"Ganas ${cantidad} Berries calculados por Lagrange."
                ),
                tipo="riesgo_bueno",
                cerrar_turno=True
            )
            return

        if evento == "conseguir_yonkou":
            propiedades = self._obtener_propiedades_propias(jugador)
            if not propiedades:
                self._abrir_evento_simple(
                    titulo="Evento Favorable",
                    mensaje="Ganaste influencia Yonkou, pero no tienes islas propias para aplicar el efecto.",
                    tipo="riesgo_bueno",
                    cerrar_turno=True
                )
                return
            self.sounds.play_effect("yonkou")
            self._abrir_info_yonkou(jugador, propiedades, desde_evento=True)
            return

        propiedades = self._obtener_propiedades_enemigas(jugador)
        if not propiedades:
            self._abrir_evento_simple(
                titulo="Evento Favorable",
                mensaje="Podías destruir una propiedad enemiga, pero no hay propiedades disponibles.",
                tipo="riesgo_bueno",
                cerrar_turno=True
            )
            return

        self.propiedades_destruibles = propiedades
        self.sounds.play_effect("evento_bueno")
        self.event_modal.abrir(
            titulo="Evento Favorable",
            mensaje=(
                "Puedes destruir una propiedad enemiga. "
                "Después de continuar, elige una casilla marcada en rojo."
            ),
            tipo="riesgo_bueno",
            opciones=[
                {"texto": "Elegir propiedad", "accion": "elegir_destruccion", "estilo": "rojo"}
            ]
        )
        self.evento_cierra_turno = False
        self.estado = "modal_destruccion_info"
        self.mensaje = "Evento favorable: destruye una propiedad enemiga."

    def _abrir_evento_simple(self, titulo, mensaje, tipo="info", cerrar_turno=True):
        self.event_modal.abrir(
            titulo=titulo,
            mensaje=mensaje,
            tipo=tipo,
            opciones=[
                {"texto": "Continuar", "accion": "continuar", "estilo": "verde"}
            ]
        )
        self.evento_cierra_turno = cerrar_turno
        self.estado = "modal_evento"
        self.mensaje = titulo
        self.detalle_casilla = mensaje

    # ============================================================
    # COMPRAS / MEJORAS / RECOMPRAS
    # ============================================================

    def _manejar_click_modal_compra(self, pos_mouse):
        accion_modal = self.purchase_modal.manejar_click(pos_mouse)

        if accion_modal is None:
            return
        self.sounds.play_effect("click")
        jugador_actual = self.turn_manager.obtener_jugador_actual()
        propiedad = self.propiedad_pendiente

        if propiedad is None:
            self.purchase_modal.cerrar()
            self.estado = "esperando_lanzamiento"
            self.mensaje = "No hay propiedad pendiente."
            return

        if accion_modal in ["no_comprar", "no_mejorar"]:
            self.detalle_casilla = f"{jugador_actual.nombre} decidió no realizar la acción en {propiedad.nombre}."
            self._finalizar_decision()
            return

        if self.estado == "modal_compra_isla":
            self._resolver_click_compra_isla(jugador_actual, propiedad, accion_modal)
            return

        if self.estado == "modal_mejora":
            self._resolver_click_mejora(jugador_actual, propiedad, accion_modal)
            return

        if self.estado == "modal_compra_poneglyph":
            self._resolver_click_compra_poneglyph(jugador_actual, propiedad, accion_modal)
            return

        if self.estado == "modal_recompra":
            self._resolver_click_recompra(jugador_actual, propiedad, accion_modal)
            return

    def _resolver_click_compra_isla(self, jugador, propiedad, accion_modal):
        niveles = {
            "comprar_base": 1,
            "comprar_nivel_2": 2,
            "comprar_nivel_3": 3
        }

        nivel_objetivo = niveles.get(accion_modal)
        if nivel_objetivo is None:
            return

        mensaje = self._comprar_propiedad_con_nivel(jugador, propiedad, nivel_objetivo)
        self.detalle_casilla = mensaje

        if propiedad.dueno != jugador:
            self.purchase_modal.mostrar_feedback(mensaje)
            self.mensaje = mensaje
            self.mensaje_temporal_tiempo = pygame.time.get_ticks()
            return
        self.sounds.play_effect("compra")
        cantidad_monopolios = self._contar_monopolios(jugador)
        if cantidad_monopolios >= 3:
            self.purchase_modal.cerrar()
            self._declarar_victoria(jugador, "consiguió 3 monopolios")
            return

        self._finalizar_decision()

    def _resolver_click_mejora(self, jugador, propiedad, accion_modal):
        if accion_modal != "mejorar_propiedad":
            return

        costo = propiedad.calcular_costo_mejora()

        if not propiedad.puede_mejorarse():
            mensaje = f"{propiedad.nombre} ya tiene mejora máxima."
            self.purchase_modal.mostrar_feedback(mensaje)
            return

        if not jugador.puede_pagar(costo):
            mensaje = f"{jugador.nombre} no tiene suficiente dinero para mejorar."
            self.purchase_modal.mostrar_feedback(mensaje)
            return

        self.detalle_casilla = self.cell_resolver.property_rules.mejorar_propiedad(
            jugador,
            propiedad
        )
        self.sounds.play_effect("mejora")
        self._finalizar_decision()

    def _resolver_click_compra_poneglyph(self, jugador, propiedad, accion_modal):
        if accion_modal != "comprar_poneglyph":
            return

        precio = self.cell_resolver.poneglyph_rules.calcular_precio_compra(jugador, propiedad)
        mensaje = self.cell_resolver.poneglyph_rules.comprar_poneglyph(jugador, propiedad, precio)
        self.detalle_casilla = mensaje

        if propiedad.dueno != jugador:
            self.purchase_modal.mostrar_feedback(mensaje)
            return
        self.sounds.play_effect("compra")
        if jugador.tiene_4_road_poneglyphs():
            self.purchase_modal.cerrar()
            self._declarar_victoria(jugador, "reunió los 4 Road Poneglyphs")
            return

        self._finalizar_decision()

    def _resolver_click_recompra(self, jugador, propiedad, accion_modal):
        impuesto = propiedad.calcular_impuesto()
        recompra = self._calcular_recompra(propiedad)

        if accion_modal == "pagar_impuesto":
            self.detalle_casilla = self.cell_resolver.property_rules.pagar_impuesto(jugador, propiedad)
            self.sounds.play_effect("perder_dinero")
            self._finalizar_decision()
            return

        if accion_modal == "pagar_y_recomprar":
            total = impuesto + recompra

            if not jugador.puede_pagar(total):
                self.purchase_modal.mostrar_feedback(
                    f"{jugador.nombre} no tiene suficiente dinero para pagar y recomprar."
                )
                return

            pago = self.cell_resolver.property_rules.pagar_impuesto(jugador, propiedad)
            recompra_msg = self.cell_resolver.property_rules.recomprar_propiedad(jugador, propiedad)
            self.detalle_casilla = f"{pago} {recompra_msg}"
            self.sounds.play_effect("recompra")
            self._finalizar_decision()

    def _calcular_precio_compra_con_nivel(self, propiedad, nivel_objetivo):
        reglas = self.cell_resolver.property_rules
        if hasattr(reglas, "calcular_precio_compra_con_nivel"):
            return reglas.calcular_precio_compra_con_nivel(propiedad, nivel_objetivo)

        nivel_objetivo = max(1, min(3, nivel_objetivo))
        return propiedad.precio_actual + propiedad.calcular_costo_mejora() * (nivel_objetivo - 1)

    def _comprar_propiedad_con_nivel(self, jugador, propiedad, nivel_objetivo):
        reglas = self.cell_resolver.property_rules
        if hasattr(reglas, "comprar_propiedad_con_nivel"):
            return reglas.comprar_propiedad_con_nivel(jugador, propiedad, nivel_objetivo)

        precio_total = self._calcular_precio_compra_con_nivel(propiedad, nivel_objetivo)

        if not propiedad.esta_libre():
            return f"{propiedad.nombre} ya tiene dueño."

        if not jugador.puede_pagar(precio_total):
            return f"{jugador.nombre} no tiene suficiente dinero para comprar {propiedad.nombre} en nivel {nivel_objetivo}."

        jugador.restar_dinero(precio_total)
        propiedad.asignar_dueno(jugador)
        jugador.agregar_propiedad(propiedad)
        propiedad.nivel_mejora = nivel_objetivo - 1

        return f"{jugador.nombre} compró {propiedad.nombre} en nivel {nivel_objetivo} por ${precio_total}."

    def _calcular_recompra(self, propiedad):
        tiene_monopolio = False
        reglas = self.cell_resolver.property_rules

        if propiedad.dueno is not None and hasattr(reglas, "jugador_tiene_monopolio"):
            tiene_monopolio = reglas.jugador_tiene_monopolio(propiedad.dueno, propiedad.grupo)

        return propiedad.calcular_recompra(tiene_monopolio=tiene_monopolio)

    def _contar_monopolios(self, jugador):
        reglas = self.cell_resolver.property_rules
        if hasattr(reglas, "contar_monopolios"):
            return reglas.contar_monopolios(jugador)
        return 0

    # ============================================================
    # YONKOU / DESTRUCCIÓN
    # ============================================================

    def _abrir_info_yonkou(self, jugador, propiedades, desde_evento=False):
        self.propiedades_yonkou_disponibles = propiedades or []

        if not self.propiedades_yonkou_disponibles:
            self._abrir_evento_simple(
                titulo="Yonkou",
                mensaje=f"{jugador.nombre} no tiene islas disponibles para aplicar Bounty Yonkou.",
                tipo="yonkou",
                cerrar_turno=True
            )
            return

        self.event_modal.abrir(
            titulo="Bounty Yonkou",
            mensaje=(
                "Has obtenido el poder Yonkou. "
                "Después de continuar, elige una de tus islas marcadas en dorado."
            ),
            tipo="yonkou",
            opciones=[
                {"texto": "Elegir isla", "accion": "elegir_yonkou", "estilo": "verde"}
            ]
        )
        self.evento_cierra_turno = False
        self.estado = "modal_yonkou_info"
        self.mensaje = "Bounty Yonkou disponible."

    def _manejar_click_yonkou(self, pos_mouse):
        jugador_actual = self.turn_manager.obtener_jugador_actual()
        referencias = [p.referencia for p in self.propiedades_yonkou_disponibles]

        for casilla in self.board_manager.obtener_todas_las_casillas():
            rect = pygame.Rect(casilla.x, casilla.y, casilla.ancho, casilla.alto)

            if rect.collidepoint(pos_mouse) and casilla.referencia in referencias:
                propiedad = self._buscar_propiedad_en_lista(
                    self.propiedades_yonkou_disponibles,
                    casilla.referencia
                )

                if propiedad:
                    self.casilla_yonkou = casilla.referencia
                    self.detalle_casilla = self.cell_resolver.yonkou_rules.aplicar_yonkou(
                        jugador_actual,
                        propiedad
                    )
                    self.propiedades_yonkou_disponibles = []
                    self._finalizar_decision()

                return

    def _manejar_click_destruccion(self, pos_mouse):
        referencias = [p.referencia for p in self.propiedades_destruibles]

        for casilla in self.board_manager.obtener_todas_las_casillas():
            rect = pygame.Rect(casilla.x, casilla.y, casilla.ancho, casilla.alto)

            if rect.collidepoint(pos_mouse) and casilla.referencia in referencias:
                propiedad = self._buscar_propiedad_en_lista(
                    self.propiedades_destruibles,
                    casilla.referencia
                )

                if propiedad:
                    nombre = propiedad.nombre
                    dueno = propiedad.dueno.nombre if propiedad.dueno else "otro jugador"
                    self._liberar_propiedad(propiedad)
                    self.sounds.play_effect("destruir")
                    self.propiedades_destruibles = []

                    self._abrir_evento_simple(
                        titulo="Propiedad destruida",
                        mensaje=f"{nombre}, propiedad de {dueno}, fue destruida y vuelve a quedar libre.",
                        tipo="riesgo_bueno",
                        cerrar_turno=True
                    )

                return

    def _buscar_propiedad_en_lista(self, propiedades, referencia):
        for propiedad in propiedades:
            if propiedad.referencia == referencia:
                return propiedad
        return None

    def _obtener_propiedades_propias(self, jugador):
        return [
            propiedad
            for propiedad in self.cell_resolver.property_rules.propiedades.values()
            if propiedad.dueno == jugador
        ]

    def _obtener_propiedades_enemigas(self, jugador):
        bienes = []

        for propiedad in self.cell_resolver.property_rules.propiedades.values():
            if propiedad.dueno is not None and propiedad.dueno != jugador:
                bienes.append(propiedad)

        for poneglyph in self.cell_resolver.poneglyph_rules.poneglyphs.values():
            if poneglyph.dueno is not None and poneglyph.dueno != jugador:
                bienes.append(poneglyph)

        return bienes
    
    def _liberar_propiedad(self, propiedad):
        dueno = propiedad.dueno

        if dueno is not None:
            if getattr(propiedad, "tipo", "") == "road_poneglyph":
                if hasattr(dueno, "road_poneglyphs") and propiedad in dueno.road_poneglyphs:
                    dueno.road_poneglyphs.remove(propiedad)
            else:
                dueno.quitar_propiedad(propiedad)

        propiedad.quitar_dueno()

        if hasattr(propiedad, "nivel_mejora"):
            propiedad.nivel_mejora = 0

        if hasattr(propiedad, "tiene_yonkou"):
            propiedad.tiene_yonkou = False

        if self.casilla_yonkou == propiedad.referencia:
            self.casilla_yonkou = None

    def _declarar_victoria(self, jugador, motivo):
        self.ganador = jugador
        self.motivo_victoria = motivo
        self.estado = "fin_partida"
        self.sounds.stop_music()
        self.sounds.play_effect("victoria")

        self.mensaje = f"{jugador.nombre} ganó: {motivo}."
        self.detalle_casilla = self.mensaje

        self.accion_pendiente = None
        self.propiedad_pendiente = None
        self.propiedades_yonkou_disponibles = []
        self.propiedades_destruibles = []
        self.bienes_venta_bancarrota = []
        self.jugador_en_bancarrota = None

        self.purchase_modal.cerrar()
        self.event_modal.cerrar()

    # ============================================================
    # FINALIZAR ACCIONES
    # ============================================================

    def _obtener_bienes_del_jugador(self, jugador):
        """
        Devuelve islas y Road Poneglyphs que pertenecen al jugador.
        """

        bienes = []

        for propiedad in self.cell_resolver.property_rules.propiedades.values():
            if propiedad.dueno == jugador:
                bienes.append(propiedad)

        for poneglyph in self.cell_resolver.poneglyph_rules.poneglyphs.values():
            if poneglyph.dueno == jugador:
                bienes.append(poneglyph)

        return bienes


    def _calcular_valor_venta_bien(self, bien):
        """
        Calcula cuánto dinero recibe el jugador al vender un bien.

        Regla usada:
        - Isla o Road Poneglyph: 50% del precio actual.
        - Si la isla tiene mejoras, se agrega un valor extra por mejoras.
        """

        valor = int(bien.precio_actual * 0.50)

        if getattr(bien, "tipo", "") == "isla":
            valor += int(bien.calcular_costo_mejora() * bien.nivel_mejora * 0.50)

        return max(valor, 1)


    def _calcular_valor_total_venta(self, jugador):
        bienes = self._obtener_bienes_del_jugador(jugador)
        total = 0

        for bien in bienes:
            total += self._calcular_valor_venta_bien(bien)

        return total


    def _verificar_bancarrota_actual(self):
        """
        Verifica si el jugador actual quedó con dinero negativo.
        Si puede recuperarse vendiendo propiedades, entra en modo venta.
        Si no puede recuperarse ni vendiendo todo, queda eliminado.
        """

        jugador = self.turn_manager.obtener_jugador_actual()

        if not getattr(jugador, "activo", True):
            return False

        if jugador.dinero >= 0:
            return False

        bienes = self._obtener_bienes_del_jugador(jugador)
        valor_total = self._calcular_valor_total_venta(jugador)

        if jugador.dinero + valor_total < 0:
            self._eliminar_jugador_por_bancarrota(jugador)
            return True

        self.jugador_en_bancarrota = jugador
        self.bienes_venta_bancarrota = bienes
        self.estado = "seleccionando_venta_bancarrota"

        self.mensaje = (
            f"{jugador.nombre} está en bancarrota: ${jugador.dinero}. "
            "Vende propiedades marcadas en rojo."
        )

        self.detalle_casilla = self.mensaje
        self.mensaje_temporal_tiempo = 0

        self.purchase_modal.cerrar()
        self.event_modal.cerrar()

        return True


    def _manejar_click_venta_bancarrota(self, pos_mouse):
        """
        Permite vender bienes propios marcados en rojo hasta volver a dinero positivo.
        """

        jugador = self.jugador_en_bancarrota

        if jugador is None:
            self.estado = "esperando_lanzamiento"
            return

        referencias = [bien.referencia for bien in self.bienes_venta_bancarrota]

        for casilla in self.board_manager.obtener_todas_las_casillas():
            rect = pygame.Rect(casilla.x, casilla.y, casilla.ancho, casilla.alto)

            if rect.collidepoint(pos_mouse) and casilla.referencia in referencias:
                bien = self._buscar_propiedad_en_lista(
                    self.bienes_venta_bancarrota,
                    casilla.referencia
                )

                if bien is None:
                    return

                valor = self._calcular_valor_venta_bien(bien)
                nombre_bien = bien.nombre

                jugador.sumar_dinero(valor)
                self._liberar_propiedad(bien)
                self.sounds.play_effect("destruir")

                self.bienes_venta_bancarrota = self._obtener_bienes_del_jugador(jugador)

                self.mensaje = (
                    f"{jugador.nombre} vendió {nombre_bien} por ${valor}. "
                    f"Dinero actual: ${jugador.dinero}."
                )
                self.detalle_casilla = self.mensaje

                if jugador.dinero >= 0:
                    self.jugador_en_bancarrota = None
                    self.bienes_venta_bancarrota = []
                    self._finalizar_decision()
                    return

                if jugador.dinero + self._calcular_valor_total_venta(jugador) < 0:
                    self._eliminar_jugador_por_bancarrota(jugador)
                    return

                return


    def _eliminar_jugador_por_bancarrota(self, jugador):
        """
        Elimina al jugador porque no puede recuperarse ni vendiendo todo.
        Sus propiedades quedan libres.
        """

        bienes = self._obtener_bienes_del_jugador(jugador)

        for bien in list(bienes):
            self._liberar_propiedad(bien)

        jugador.activo = False
        jugador.en_carcel = False
        jugador.turnos_perdidos = 0

        self.jugador_en_bancarrota = None
        self.bienes_venta_bancarrota = []

        self.mensaje = (
            f"{jugador.nombre} quedó en bancarrota y fue eliminado. "
            "Sus propiedades quedaron libres."
        )
        self.detalle_casilla = self.mensaje
        self.mensaje_temporal_tiempo = pygame.time.get_ticks()

        if self._verificar_victoria_por_supervivencia():
            return

        self.turn_manager.siguiente_turno()
        self._saltar_jugadores_eliminados()

        self.estado = "esperando_lanzamiento"


    def _verificar_victoria_por_supervivencia(self):
        jugadores_activos = [
            jugador for jugador in self.jugadores
            if getattr(jugador, "activo", True)
        ]

        if len(jugadores_activos) == 1:
            ganador = jugadores_activos[0]
            self._declarar_victoria(
                ganador,
                "fue el último jugador activo"
            )
            return True

        return False


    def _saltar_jugadores_eliminados(self):
        """
        Si el turno cae en un jugador eliminado, lo salta hasta encontrar uno activo.
        """

        if self.estado == "fin_partida":
            return

        intentos = 0
        total = len(self.jugadores)

        while intentos < total:
            jugador_actual = self.turn_manager.obtener_jugador_actual()

            if getattr(jugador_actual, "activo", True):
                self.estado = "esperando_lanzamiento"
                self.mensaje = f"Turno de {jugador_actual.nombre}."
                return

            self.turn_manager.siguiente_turno()
            intentos += 1

        self.estado = "fin_partida"
        self.mensaje = "No quedan jugadores activos."

    def _finalizar_decision(self):
        self.purchase_modal.cerrar()
        self.event_modal.cerrar()

        if self._verificar_bancarrota_actual():
            return

        self.accion_pendiente = None
        self.propiedad_pendiente = None
        self.propiedades_yonkou_disponibles = []
        self.propiedades_destruibles = []
        self.evento_cierra_turno = True
        self._avanzar_turno()
        self._saltar_jugadores_eliminados()
        self.estado = "esperando_lanzamiento"

        if self.detalle_casilla:
            self.mensaje = self.detalle_casilla
            self.mensaje_temporal_tiempo = pygame.time.get_ticks()
        else:
            self.mensaje = "Presiona ESPACIO para lanzar los dados"
    
    def _cerrar_turno_con_log(self, mensaje):
        """
        Cierra el turno mostrando solo el mensaje en el log central.
        No abre modal.
        """

        self.detalle_casilla = mensaje
        self.mensaje = mensaje
        self.mensaje_temporal_tiempo = pygame.time.get_ticks()

        if hasattr(self, "movement_manager"):
            self.movement_manager.limpiar_ultima_casilla()

        self.accion_pendiente = None
        self.propiedad_pendiente = None

        self._avanzar_turno()
        self.estado = "esperando_lanzamiento"
    # ============================================================
    # DIBUJO GENERAL
    # ============================================================

    def _dibujar(self):
        self.pantalla.blit(self.fondo, (0, 0))
        self.pantalla.blit(self.tablero, (self.board_x, self.board_y))

        self._dibujar_marcas_propiedades()
        self._dibujar_casilla_yonkou()
        self._dibujar_casillas_seleccion_yonkou()
        self._dibujar_casillas_seleccion_destruccion()
        self._dibujar_casillas_venta_bancarrota()

        self._dibujar_jugadores()
        self._dibujar_paneles_jugadores()
        self._dibujar_dados_centro()
        self._dibujar_contador_turnos()
        self._dibujar_msgbox()
        self._dibujar_alerta_lagrange()
        self.cell_info_panel.dibujar(self.pantalla)
        self._dibujar_modal_compra()
        self._dibujar_event_modal()

        self._dibujar_pantalla_victoria()

        pygame.display.flip()

    def _obtener_casilla_por_referencia(self, referencia):
        for casilla in self.board_manager.obtener_todas_las_casillas():
            if casilla.referencia == referencia:
                return casilla
        return None
    def _dibujar_alerta_lagrange(self):
        if not self.alerta_lagrange:
            return

        tiempo_actual = pygame.time.get_ticks()

        if tiempo_actual - self.alerta_lagrange_tiempo > self.alerta_lagrange_duracion:
            self.alerta_lagrange = ""
            return

        ancho_box = 760
        alto_box = 46

        x = (self.ancho - ancho_box) // 2
        y = self.board_y + 145

        rect = pygame.Rect(x, y, ancho_box, alto_box)

        pygame.draw.rect(
            self.pantalla,
            (18, 24, 36),
            rect,
            border_radius=12
        )

        pygame.draw.rect(
            self.pantalla,
            (255, 205, 80),
            rect,
            width=2,
            border_radius=12
        )

        self._dibujar_texto_centrado(
            self.alerta_lagrange,
            x + ancho_box // 2,
            y + 14,
            size=16,
            color=(255, 235, 170)
        )

    def _mostrar_alerta_superior(self, mensaje):
        self.alerta_lagrange = mensaje
        self.alerta_lagrange_tiempo = pygame.time.get_ticks()

    def _dibujar_pantalla_victoria(self):
        if self.estado != "fin_partida":
            return

        overlay = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.pantalla.blit(overlay, (0, 0))

        panel_ancho = 680
        panel_alto = 560
        panel_x = (self.ancho - panel_ancho) // 2
        panel_y = (self.alto - panel_alto) // 2

        pygame.draw.rect(
            self.pantalla,
            (25, 25, 35),
            (panel_x, panel_y, panel_ancho, panel_alto),
            border_radius=18
        )

        pygame.draw.rect(
            self.pantalla,
            (230, 190, 80),
            (panel_x, panel_y, panel_ancho, panel_alto),
            width=4,
            border_radius=18
        )

        if self.imagen_victoria:
            img_x = panel_x + (panel_ancho - self.imagen_victoria.get_width()) // 2
            img_y = panel_y + 25
            self.pantalla.blit(self.imagen_victoria, (img_x, img_y))

        ganador_nombre = self.ganador.nombre if self.ganador else "Jugador"

        self._dibujar_texto_centrado(
            "VICTORIA",
            panel_x + panel_ancho // 2,
            panel_y + 310,
            size=40,
            color=(255, 220, 80)
        )

        self._dibujar_texto_centrado(
            f"{ganador_nombre} ganó",
            panel_x + panel_ancho // 2,
            panel_y + 365,
            size=25,
            color=(255, 255, 255)
        )

        self._dibujar_texto_centrado(
            self.motivo_victoria,
            panel_x + panel_ancho // 2,
            panel_y + 405,
            size=19,
            color=(220, 220, 220)
        )

        boton_ancho = 240
        boton_alto = 42
        boton_x = panel_x + (panel_ancho - boton_ancho) // 2
        boton_y = panel_y + 465

        self.boton_victoria_rect = pygame.Rect(
            boton_x,
            boton_y,
            boton_ancho,
            boton_alto
        )

        mouse_pos = pygame.mouse.get_pos()
        hover = self.boton_victoria_rect.collidepoint(mouse_pos)

        color_boton = (118, 78, 26) if not hover else (160, 105, 35)
        color_borde = (255, 218, 100)

        pygame.draw.rect(
            self.pantalla,
            color_borde,
            pygame.Rect(boton_x - 3, boton_y - 3, boton_ancho + 6, boton_alto + 6),
            border_radius=12
        )

        pygame.draw.rect(
            self.pantalla,
            color_boton,
            self.boton_victoria_rect,
            border_radius=10
        )

        pygame.draw.rect(
            self.pantalla,
            (45, 25, 10),
            self.boton_victoria_rect,
            width=2,
            border_radius=10
        )

        font_boton = pygame.font.SysFont("arial", 20, bold=True)
        texto_boton = font_boton.render("Continuar", True, (255, 245, 210))
        texto_rect = texto_boton.get_rect(
            center=(
                boton_x + boton_ancho // 2,
                boton_y + boton_alto // 2
            )
        )

        self.pantalla.blit(texto_boton, texto_rect)
    
    def _dibujar_casillas_venta_bancarrota(self):
        if self.estado != "seleccionando_venta_bancarrota":
            return

        referencias = [bien.referencia for bien in self.bienes_venta_bancarrota]

        for casilla in self.board_manager.obtener_todas_las_casillas():
            if casilla.referencia in referencias:
                overlay = pygame.Surface((casilla.ancho, casilla.alto), pygame.SRCALPHA)
                overlay.fill((255, 0, 0, 55))
                self.pantalla.blit(overlay, (casilla.x, casilla.y))

                pygame.draw.rect(
                    self.pantalla,
                    (255, 40, 40),
                    (casilla.x, casilla.y, casilla.ancho, casilla.alto),
                    width=5,
                    border_radius=8
                )

    def _dibujar_marcas_propiedades(self):
        propiedades = list(self.cell_resolver.property_rules.propiedades.values())
        poneglyphs = list(self.cell_resolver.poneglyph_rules.poneglyphs.values())

        for propiedad in propiedades + poneglyphs:
            if propiedad.dueno is None:
                continue

            casilla = self._obtener_casilla_por_referencia(propiedad.referencia)
            if casilla is None:
                continue

            imagen_dueno = getattr(propiedad.dueno, "imagen", None)
            if imagen_dueno is None:
                continue

            marca_size = 42
            marca = pygame.transform.smoothscale(imagen_dueno, (marca_size, marca_size))
            x = casilla.x + (casilla.ancho - marca_size) // 2
            y = casilla.y + (casilla.alto - marca_size) // 2
            self.pantalla.blit(marca, (x, y))

    def _dibujar_modal_compra(self):
        if self.estado not in [
            "modal_compra_isla",
            "modal_compra_poneglyph",
            "modal_recompra",
            "modal_mejora"
        ]:
            return

        self.purchase_modal.dibujar(self.pantalla)

    def _dibujar_event_modal(self):
        if self.estado not in [
            "modal_evento",
            "modal_yonkou_info",
            "modal_destruccion_info",
            "modal_prision"
        ]:
            return

        self.event_modal.dibujar(self.pantalla)

    def _dibujar_casilla_yonkou(self):
        if not self.casilla_yonkou:
            return

        casilla = self._obtener_casilla_por_referencia(self.casilla_yonkou)
        if casilla is None:
            return

        tiempo = pygame.time.get_ticks()
        grosor = 5 + int((tiempo // 250) % 2)

        overlay = pygame.Surface((casilla.ancho, casilla.alto), pygame.SRCALPHA)
        overlay.fill((255, 210, 40, 55))
        self.pantalla.blit(overlay, (casilla.x, casilla.y))

        pygame.draw.rect(
            self.pantalla,
            (255, 215, 0),
            (casilla.x, casilla.y, casilla.ancho, casilla.alto),
            width=grosor,
            border_radius=8
        )

        centro_x = casilla.x + casilla.ancho // 2
        centro_y = casilla.y + casilla.alto // 2
        pygame.draw.circle(self.pantalla, (255, 215, 0), (centro_x, centro_y), 16)
        pygame.draw.circle(self.pantalla, (70, 45, 0), (centro_x, centro_y), 16, 2)
        self._dibujar_texto_centrado("Y", centro_x, centro_y, size=18, color=(70, 45, 0))

    def _dibujar_casillas_seleccion_yonkou(self):
        if self.estado != "seleccionando_yonkou":
            return

        referencias = [p.referencia for p in self.propiedades_yonkou_disponibles]
        for casilla in self.board_manager.obtener_todas_las_casillas():
            if casilla.referencia in referencias:
                pygame.draw.rect(
                    self.pantalla,
                    (255, 215, 0),
                    (casilla.x, casilla.y, casilla.ancho, casilla.alto),
                    width=5,
                    border_radius=8
                )

    def _dibujar_casillas_seleccion_destruccion(self):
        if self.estado != "seleccionando_destruccion":
            return

        referencias = [p.referencia for p in self.propiedades_destruibles]
        for casilla in self.board_manager.obtener_todas_las_casillas():
            if casilla.referencia in referencias:
                overlay = pygame.Surface((casilla.ancho, casilla.alto), pygame.SRCALPHA)
                overlay.fill((255, 0, 0, 45))
                self.pantalla.blit(overlay, (casilla.x, casilla.y))

                pygame.draw.rect(
                    self.pantalla,
                    (255, 60, 60),
                    (casilla.x, casilla.y, casilla.ancho, casilla.alto),
                    width=5,
                    border_radius=8
                )
    def _dibujar_contador_turnos(self):
        turno = self.turn_manager.turno_numero
        jugador_actual = self.turn_manager.obtener_jugador_actual()

        if jugador_actual:
            texto = f"Turno {turno} | {jugador_actual.nombre}"
        else:
            texto = f"Turno {turno}"

        ancho_box = 250
        alto_box = 38

        x = self.board_x + self.board_size + 18
        y = 150

        if x + ancho_box > self.ancho:
            x = self.ancho - ancho_box - 18

        rect = pygame.Rect(x, y, ancho_box, alto_box)

        pygame.draw.rect(
            self.pantalla,
            (18, 24, 36),
            rect,
            border_radius=10
        )

        pygame.draw.rect(
            self.pantalla,
            (255, 205, 80),
            rect,
            width=2,
            border_radius=10
        )

        self._dibujar_texto_centrado(
            texto,
            x + ancho_box // 2,
            y + alto_box // 2,
            size=15,
            color=(255, 235, 170)
        )
    def _dibujar_jugadores(self):
        colores = [
            (255, 80, 80),
            (80, 190, 60),
            (80, 160, 255),
            (255, 220, 80),
        ]

        for i, jugador in enumerate(self.jugadores):
            if not getattr(jugador, "activo", True):
                continue

            x, y = self.movement_manager.obtener_posicion_con_efecto_barco(jugador)

            if getattr(jugador, "ficha", None):
                self.pantalla.blit(jugador.ficha, (x, y))
            else:
                color = colores[i % len(colores)]
                pygame.draw.circle(self.pantalla, color, (int(x) + 24, int(y) + 24), 22)
                pygame.draw.circle(self.pantalla, (20, 20, 20), (int(x) + 24, int(y) + 24), 22, 2)
                self._dibujar_texto(str(i + 1), int(x) + 16, int(y) + 8, size=22, color=(0, 0, 0))

    def _dibujar_paneles_jugadores(self):
        ancho_carta = 330
        alto_carta = 105
        margen_lateral = 5
        margen_superior = 25
        margen_inferior = 35

        posiciones = [
            (margen_lateral, margen_superior),
            (self.ancho - ancho_carta - margen_lateral, margen_superior),
            (margen_lateral, self.alto - alto_carta - margen_inferior),
            (self.ancho - ancho_carta - margen_lateral, self.alto - alto_carta - margen_inferior),
        ]

        for i, jugador in enumerate(self.jugadores):
            if i >= len(posiciones):
                break
            x, y = posiciones[i]
            self._dibujar_tarjeta_jugador(jugador, x, y)

    def _dibujar_tarjeta_jugador(self, jugador, x, y):
        ancho_carta = 330
        alto_carta = 105
        jugador_actual = self.turn_manager.obtener_jugador_actual()
        if jugador == jugador_actual and getattr(jugador, "activo", True) and self.estado != "fin_partida":
            tiempo = pygame.time.get_ticks()
            grosor = 4 + int((tiempo // 300) % 2)

            rect_brillo = pygame.Rect(
                x - 6,
                y - 6,
                ancho_carta + 12,
                alto_carta + 12
            )

            pygame.draw.rect(
                self.pantalla,
                (255, 210, 60),
                rect_brillo,
                width=grosor,
                border_radius=18
            )

        if jugador.carta:
            self.pantalla.blit(jugador.carta, (x, y))
        else:
            pygame.draw.rect(
                self.pantalla,
                (30, 30, 40),
                (x, y, ancho_carta, alto_carta),
                border_radius=15
            )

        nombre_centro_x = x + 200
        nombre_centro_y = y + 30
        dinero_centro_x = x + 200
        dinero_centro_y = y + 70

        self._dibujar_texto_centrado(jugador.nombre, nombre_centro_x, nombre_centro_y, size=18, color=(25, 15, 10))
        self._dibujar_texto_centrado(f"${jugador.dinero}", dinero_centro_x, dinero_centro_y, size=16, color=(255, 255, 255))

        if not getattr(jugador, "activo", True):
            pygame.draw.line(
                self.pantalla,
                (220, 30, 30),
                (x + 20, y + 15),
                (x + ancho_carta - 20, y + alto_carta - 15),
                8
            )

            pygame.draw.line(
                self.pantalla,
                (220, 30, 30),
                (x + ancho_carta - 20, y + 15),
                (x + 20, y + alto_carta - 15),
                8
            )

    def _dibujar_dados_centro(self):
        centro_x = self.board_x + self.board_size // 2
        centro_y = self.board_y + self.board_size // 2

        dado_ancho = 72
        separacion = 20
        total_ancho = dado_ancho * 2 + separacion

        x = centro_x - total_ancho // 2
        y = centro_y - 45

        self.dice.dibujar(self.pantalla, x, y, separacion=separacion)

    def _dibujar_msgbox(self):
        ancho_box = 520
        alto_box = 46
        x = (self.ancho - ancho_box) // 2
        y = self.board_y + self.board_size - 250

        if y + alto_box > self.alto:
            y = self.alto - alto_box - 8

        pygame.draw.rect(self.pantalla, (20, 20, 28), (x, y, ancho_box, alto_box), border_radius=14)
        pygame.draw.rect(self.pantalla, (230, 190, 80), (x, y, ancho_box, alto_box), width=2, border_radius=14)

        texto = str(self.mensaje)
        if len(texto) > 72:
            texto = texto[:69] + "..."

        self._dibujar_texto(texto, x + 15, y + 13, size=14, color=(255, 255, 255))

    def _dibujar_texto(self, texto, x, y, size=24, color=(255, 255, 255)):
        fuente = pygame.font.SysFont("arial", size, bold=True)
        render = fuente.render(str(texto), True, color)
        self.pantalla.blit(render, (x, y))

    def _dibujar_texto_centrado(self, texto, centro_x, y, size=24, color=(255, 255, 255)):
        fuente = pygame.font.SysFont("arial", size, bold=True)
        render = fuente.render(str(texto), True, color)
        rect = render.get_rect(center=(centro_x, y))
        self.pantalla.blit(render, rect)
