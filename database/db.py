"""
Maneja la conexión con SQLite, creación de tablas, registros y consultas básicas del juego.
"""

import sqlite3
from pathlib import Path


RUTA_BD = Path("data/monopoly.db")
RUTA_SCHEMA = Path("database/schema.sql")


def conectar():
    RUTA_BD.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(RUTA_BD)


def crear_base_datos():
    """
    Ejecuta el schema.sql para crear las tablas si no existen.
    No borra datos anteriores siempre que schema.sql use CREATE TABLE IF NOT EXISTS.
    """

    if not RUTA_SCHEMA.exists():
        raise FileNotFoundError("No se encontró database/schema.sql")

    with conectar() as conexion:
        with open(RUTA_SCHEMA, "r", encoding="utf-8") as archivo:
            conexion.executescript(archivo.read())

    print("Base de datos lista.")


def inicializar_base_datos():
    """
    Prepara la base de datos para usarse en el juego.
    Si la base no existe, la crea.
    Si ya existe, conserva los datos anteriores.
    """

    crear_base_datos()


def obtener_siguiente_partida_id():
    """
    Devuelve cuál sería el próximo ID de partida.
    SQLite asigna el ID real al llamar guardar_partida().
    """

    inicializar_base_datos()

    with conectar() as conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM partidas")
        return cursor.fetchone()[0]


def guardar_partida(cantidad_jugadores, ganador=None, condicion_victoria=None):
    with conectar() as conexion:
        cursor = conexion.cursor()
        cursor.execute(
            """
            INSERT INTO partidas (cantidad_jugadores, ganador, condicion_victoria)
            VALUES (?, ?, ?)
            """,
            (cantidad_jugadores, ganador, condicion_victoria)
        )
        return cursor.lastrowid


def guardar_jugador(partida_id, nombre, berries=3000):
    with conectar() as conexion:
        cursor = conexion.cursor()
        cursor.execute(
            """
            INSERT INTO jugadores (partida_id, nombre, berries)
            VALUES (?, ?, ?)
            """,
            (partida_id, nombre, berries)
        )
        return cursor.lastrowid


def guardar_propiedad(
    partida_id,
    nombre,
    tipo,
    grupo_color=None,
    propietario=None,
    nivel_mejora=0,
    precio_actual=0
):
    with conectar() as conexion:
        cursor = conexion.cursor()
        cursor.execute(
            """
            INSERT INTO propiedades (
                partida_id, nombre, tipo, grupo_color,
                propietario, nivel_mejora, precio_actual
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                partida_id,
                nombre,
                tipo,
                grupo_color,
                propietario,
                nivel_mejora,
                precio_actual
            )
        )
        return cursor.lastrowid


def guardar_calculo_lagrange(
    partida_id,
    turno,
    propiedad,
    puntos_usados,
    x_eval,
    precio_estimado,
    precio_real=None,
    error_absoluto=None,
    error_porcentual=None
):
    with conectar() as conexion:
        cursor = conexion.cursor()
        cursor.execute(
            """
            INSERT INTO calculos_lagrange (
                partida_id, turno, propiedad, puntos_usados,
                x_eval, precio_estimado, precio_real,
                error_absoluto, error_porcentual
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                partida_id,
                turno,
                propiedad,
                puntos_usados,
                x_eval,
                precio_estimado,
                precio_real,
                error_absoluto,
                error_porcentual
            )
        )
        return cursor.lastrowid


def guardar_transaccion(
    partida_id,
    turno,
    jugador,
    tipo,
    monto,
    propiedad=None,
    descripcion=None
):
    with conectar() as conexion:
        cursor = conexion.cursor()
        cursor.execute(
            """
            INSERT INTO transacciones (
                partida_id, turno, jugador, tipo,
                monto, propiedad, descripcion
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                partida_id,
                turno,
                jugador,
                tipo,
                monto,
                propiedad,
                descripcion
            )
        )
        return cursor.lastrowid


def guardar_evento(
    partida_id,
    turno,
    jugador,
    tipo_evento,
    efecto,
    monto=0
):
    with conectar() as conexion:
        cursor = conexion.cursor()
        cursor.execute(
            """
            INSERT INTO eventos (
                partida_id, turno, jugador,
                tipo_evento, efecto, monto
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                partida_id,
                turno,
                jugador,
                tipo_evento,
                efecto,
                monto
            )
        )
        return cursor.lastrowid


def guardar_yonkou(
    partida_id,
    turno,
    jugador_yonkou,
    isla_mejorada=None,
    jugador_anterior=None,
    isla_anterior=None
):
    with conectar() as conexion:
        cursor = conexion.cursor()
        cursor.execute(
            """
            INSERT INTO mejora_yonkou (
                partida_id, turno, jugador_yonkou,
                isla_mejorada, jugador_anterior, isla_anterior
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                partida_id,
                turno,
                jugador_yonkou,
                isla_mejorada,
                jugador_anterior,
                isla_anterior
            )
        )
        return cursor.lastrowid


def actualizar_ganador(partida_id, ganador, condicion_victoria):
    with conectar() as conexion:
        cursor = conexion.cursor()
        cursor.execute(
            """
            UPDATE partidas
            SET ganador = ?, condicion_victoria = ?
            WHERE id = ?
            """,
            (ganador, condicion_victoria, partida_id)
        )


def actualizar_jugador_estado(
    partida_id,
    nombre,
    berries,
    riqueza_total=0,
    monopolios=0,
    road_poneglyphs=0
):
    """
    Actualiza el estado final/parcial de un jugador dentro de una partida.
    """

    with conectar() as conexion:
        cursor = conexion.cursor()
        cursor.execute(
            """
            UPDATE jugadores
            SET berries = ?, riqueza_total = ?, monopolios = ?, road_poneglyphs = ?
            WHERE partida_id = ? AND nombre = ?
            """,
            (
                berries,
                riqueza_total,
                monopolios,
                road_poneglyphs,
                partida_id,
                nombre
            )
        )


def actualizar_propiedad_estado(
    partida_id,
    nombre,
    propietario=None,
    nivel_mejora=0,
    precio_actual=0
):
    """
    Actualiza propietario, nivel de mejora y precio actual de una propiedad.
    """

    with conectar() as conexion:
        cursor = conexion.cursor()
        cursor.execute(
            """
            UPDATE propiedades
            SET propietario = ?, nivel_mejora = ?, precio_actual = ?
            WHERE partida_id = ? AND nombre = ?
            """,
            (
                propietario,
                nivel_mejora,
                precio_actual,
                partida_id,
                nombre
            )
        )


def consultar_tabla(nombre_tabla):
    tablas_permitidas = {
        "partidas",
        "jugadores",
        "propiedades",
        "calculos_lagrange",
        "transacciones",
        "eventos",
        "mejora_yonkou"
    }

    if nombre_tabla not in tablas_permitidas:
        raise ValueError("Tabla no permitida.")

    with conectar() as conexion:
        cursor = conexion.cursor()
        cursor.execute(f"SELECT * FROM {nombre_tabla}")
        return cursor.fetchall()


def obtener_calculos_lagrange(partida_id=None):
    with conectar() as conexion:
        cursor = conexion.cursor()

        if partida_id is None:
            cursor.execute("SELECT * FROM calculos_lagrange")
        else:
            cursor.execute(
                "SELECT * FROM calculos_lagrange WHERE partida_id = ?",
                (partida_id,)
            )

        return cursor.fetchall()


def obtener_transacciones(partida_id=None):
    with conectar() as conexion:
        cursor = conexion.cursor()

        if partida_id is None:
            cursor.execute("SELECT * FROM transacciones")
        else:
            cursor.execute(
                "SELECT * FROM transacciones WHERE partida_id = ?",
                (partida_id,)
            )

        return cursor.fetchall()


def obtener_eventos(partida_id=None):
    with conectar() as conexion:
        cursor = conexion.cursor()

        if partida_id is None:
            cursor.execute("SELECT * FROM eventos")
        else:
            cursor.execute(
                "SELECT * FROM eventos WHERE partida_id = ?",
                (partida_id,)
            )

        return cursor.fetchall()
