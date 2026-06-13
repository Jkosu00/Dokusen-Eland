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


def calcular_precio_propiedad(nombre_propiedad, turno_actual, cantidad_puntos=4):
    """
    Calcula el precio estimado de una isla o Road Poneglyph.
    """

    propiedad = obtener_propiedad(nombre_propiedad)

    resultado = estimar_valor(
        puntos=propiedad["puntos"],
        x_eval=turno_actual,
        cantidad_puntos=cantidad_puntos,
        valor_real=propiedad.get("valor_real_simulado")
    )

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