"""
Servicio encargado de cargar los datos históricos simulados y calcular precios usando Interpolación de Lagrange.
"""

import json
from pathlib import Path

from metodos.lagrange import (
    estimar_valor,
    comparar_estimaciones,
    detectar_posible_runge
)
RUTA_PRECIOS = Path("data/precios_simulados.json")

def cargar_datos_precios():
    """
    Carga el archivo JSON con los precios históricos simulados.
    """

    if not RUTA_PRECIOS.exists():
        raise FileNotFoundError("No se encontró data/precios_simulados.json")

    with open(RUTA_PRECIOS, "r", encoding="utf-8") as archivo:
        return json.load(archivo)

def obtener_propiedad(nombre_propiedad):
    """
    Busca una propiedad dentro del JSON.
    """

    datos = cargar_datos_precios()
    propiedades = datos.get("propiedades", {})

    if nombre_propiedad not in propiedades:
        raise ValueError(f"No existe la propiedad: {nombre_propiedad}")

    return propiedades[nombre_propiedad]

def seleccionar_puntos_estables(puntos, turno_actual, cantidad_puntos=4):
    """
    Selecciona puntos para evitar explosiones por extrapolación.

    - Si el turno está dentro del rango histórico, usa varios puntos.
    - Si el turno está después del último punto, usa los últimos 2 puntos.
      Eso equivale a Lagrange lineal y evita curvas absurdas.
    """

    puntos_ordenados = sorted(puntos, key=lambda punto: punto[0])

    primer_turno = puntos_ordenados[0][0]
    ultimo_turno = puntos_ordenados[-1][0]

    if turno_actual > ultimo_turno:
        return puntos_ordenados[-2:]

    if turno_actual < primer_turno:
        return puntos_ordenados[:2]

    return puntos_ordenados[-cantidad_puntos:]

def calcular_precio_propiedad(nombre_propiedad, turno_actual, cantidad_puntos=4):
    propiedad = obtener_propiedad(nombre_propiedad)
    puntos = propiedad["puntos"]

    puntos_usados = seleccionar_puntos_estables(
        puntos,
        turno_actual,
        cantidad_puntos
    )

    resultado = estimar_valor(
        puntos=puntos_usados,
        x_eval=turno_actual,
        cantidad_puntos=None,
        valor_real=propiedad.get("valor_real_simulado")
    )

    precio_estimado = int(round(resultado["valor_estimado"]))

    precios_historicos = [punto[1] for punto in puntos]
    ultimo_precio = puntos[-1][1]

    precio_minimo = int(min(precios_historicos) * 0.85)

    # Tope económico razonable. Evita que una isla destruya la partida.
    precio_maximo = int(ultimo_precio * 1.80)

    precio_estimado = max(precio_minimo, min(precio_estimado, precio_maximo))

    resultado["valor_estimado"] = precio_estimado
    resultado["nombre_propiedad"] = nombre_propiedad
    resultado["tipo"] = propiedad["tipo"]
    resultado["grupo"] = propiedad["grupo"]
    resultado["posicion_tablero"] = propiedad["posicion_tablero"]

    return resultado

def comparar_precio_propiedad(nombre_propiedad, turno_actual, cantidades=(3, 4, 5, 6)):
    """
    Compara el precio de una propiedad usando distintas cantidades de puntos, sirve para mostrar errores en la defensa.
    """

    propiedad = obtener_propiedad(nombre_propiedad)

    resultados = comparar_estimaciones(
        puntos=propiedad["puntos"],
        x_eval=turno_actual,
        valor_real=propiedad.get("valor_real_simulado"),
        cantidades=cantidades
    )

    for resultado in resultados:
        resultado["nombre_propiedad"] = nombre_propiedad
        resultado["tipo"] = propiedad["tipo"]

    return resultados


def analizar_runge():
    """
    Analiza el caso especial de Runge definido en el JSON.
    """

    datos = cargar_datos_precios()
    caso = datos["caso_runge"]["Isla Runge"]

    resultados = comparar_estimaciones(
        puntos=caso["puntos"],
        x_eval=caso["x_eval"],
        valor_real=caso["valor_real_simulado"],
        cantidades=(3, 4, 5, 6, 7)
    )

    return {
        "descripcion": caso["descripcion"],
        "resultados": resultados,
        "posible_runge": detectar_posible_runge(resultados)
    }


def listar_propiedades():
    """
    Devuelve la lista de propiedades disponibles.
    """

    datos = cargar_datos_precios()
    return list(datos.get("propiedades", {}).keys())

def calcular_bono_lagrange(nombre_bono, turno_actual, cantidad_puntos=4):
    """
    Calcula recompensas dinámicas usando Lagrange.
    Se usa para salida, cofres, descanso y eventos favorables.
    """

    bonos = {
        "salida": {
            "puntos": [(1, 350), (2, 375), (3, 400), (4, 425), (5, 450), (6, 475)],
            "minimo": 300,
            "maximo": 700
        },
        "cofre": {
            "puntos": [(1, 150), (2, 180), (3, 210), (4, 240), (5, 270), (6, 300)],
            "minimo": 100,
            "maximo": 500
        },
        "riesgo_bueno": {
            "puntos": [(1, 150), (2, 175), (3, 200), (4, 225), (5, 250), (6, 275)],
            "minimo": 100,
            "maximo": 500
        },
        "descanso": {
            "puntos": [(1, 200), (2, 220), (3, 240), (4, 260), (5, 280), (6, 300)],
            "minimo": 150,
            "maximo": 450
        }
    }

    if nombre_bono not in bonos:
        raise ValueError(f"No existe el bono dinámico: {nombre_bono}")

    bono = bonos[nombre_bono]

    resultado = estimar_valor(
        puntos=bono["puntos"],
        x_eval=turno_actual,
        cantidad_puntos=cantidad_puntos
    )

    valor_estimado = int(round(resultado["valor_estimado"]))

    valor_estimado = max(
        bono["minimo"],
        min(valor_estimado, bono["maximo"])
    )

    resultado["valor_estimado"] = valor_estimado
    resultado["nombre_bono"] = nombre_bono

    return resultado

if __name__ == "__main__":
    print("PROPIEDADES DISPONIBLES")
    print(listar_propiedades())

    print("\nPRECIO ESTIMADO")
    precio = calcular_precio_propiedad(
        nombre_propiedad="Baratie",
        turno_actual=7,
        cantidad_puntos=4
    )
    print(precio)

    print("\nCOMPARACIÓN DE ERRORES")
    comparacion = comparar_precio_propiedad(
        nombre_propiedad="Baratie",
        turno_actual=7
    )
    for item in comparacion:
        print(item)

    print("\nANÁLISIS RUNGE")
    print(analizar_runge())