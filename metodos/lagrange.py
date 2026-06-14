"""Metodos de lagrange chatttt"""

def validar_puntos(puntos):
    if not puntos:
        raise ValueError("La lista de puntos no puede estar vacía.")

    valores_x = set()

    for punto in puntos:
        if len(punto) != 2:
            raise ValueError("Cada punto debe tener el formato (x, y).")

        x, y = punto

        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
            raise TypeError("Los valores de x e y deben ser numéricos.")

        if x in valores_x:
            raise ValueError("No pueden existir dos puntos con el mismo valor de x.")

        valores_x.add(x)


def interpolar_lagrange(puntos, x_eval):
    """
    Realiza la interpolación de Lagrange para estimar el valor en x_eval dado un conjunto de puntos (x, y).
    """

    validar_puntos(puntos)

    resultado = 0

    for i in range(len(puntos)):
        xi, yi = puntos[i]
        termino = yi

        for j in range(len(puntos)):
            if i != j:
                xj, _ = puntos[j]
                termino *= (x_eval - xj) / (xi - xj)

        resultado += termino

    return resultado


def calcular_error_absoluto(valor_estimado, valor_real):
    """
    Calcula el error absoluto entre el valor real y el estimado.
    """

    return abs(valor_real - valor_estimado)


def calcular_error_porcentual(valor_estimado, valor_real):
    """
    Calcula el error porcentual.
    """

    if valor_real == 0:
        return 0

    error_absoluto = calcular_error_absoluto(valor_estimado, valor_real)
    return (error_absoluto / abs(valor_real)) * 100


def seleccionar_ultimos_puntos(puntos, cantidad):
    """
    Selecciona los últimos puntos históricos disponibles.
    """

    validar_puntos(puntos)

    if cantidad <= 0:
        raise ValueError("La cantidad de puntos debe ser mayor que cero.")

    if cantidad > len(puntos):
        raise ValueError("No hay suficientes puntos históricos.")

    return puntos[-cantidad:]


def estimar_valor(puntos, x_eval, cantidad_puntos=None, valor_real=None):
    """
    Estima un valor con Lagrange y opcionalmente calcula errores.
    """

    if cantidad_puntos is not None:
        puntos_usados = seleccionar_ultimos_puntos(puntos, cantidad_puntos)
    else:
        validar_puntos(puntos)
        puntos_usados = puntos

    valor_estimado = interpolar_lagrange(puntos_usados, x_eval)

    resultado = {
        "x_eval": x_eval,
        "puntos_usados": len(puntos_usados),
        "puntos": puntos_usados,
        "valor_estimado": round(valor_estimado, 2),
        "valor_real": valor_real,
        "error_absoluto": None,
        "error_porcentual": None
    }

    if valor_real is not None:
        resultado["error_absoluto"] = round(
            calcular_error_absoluto(valor_estimado, valor_real), 2
        )

        resultado["error_porcentual"] = round(
            calcular_error_porcentual(valor_estimado, valor_real), 2
        )

    return resultado


def comparar_estimaciones(puntos, x_eval, valor_real=None, cantidades=(3, 4, 5)):
    """
    Compara estimaciones usando diferentes cantidades de puntos históricos.
    """

    resultados = []

    for cantidad in cantidades:
        if cantidad <= len(puntos):
            resultado = estimar_valor(
                puntos=puntos,
                x_eval=x_eval,
                cantidad_puntos=cantidad,
                valor_real=valor_real
            )
            resultados.append(resultado)

    return resultados


def detectar_posible_runge(resultados):
    """
    Detecta si hay un posible fenómeno de Runge al observar el comportamiento del error porcentual.
    """

    resultados_con_error = [
        r for r in resultados if r["error_porcentual"] is not None
    ]

    if len(resultados_con_error) < 2:
        return False

    for i in range(1, len(resultados_con_error)):
        error_anterior = resultados_con_error[i - 1]["error_porcentual"]
        error_actual = resultados_con_error[i]["error_porcentual"]

        if error_actual > error_anterior:
            return True

    return False


if __name__ == "__main__":
    puntos_historicos = [
        (1, 300),
        (2, 340),
        (3, 390),
        (4, 450),
        (5, 520),
        (6, 610)
    ]

    x_eval = 7
    valor_real_simulado = 690

    print("PRUEBA INDIVIDUAL DE LAGRANGE")
    resultado = estimar_valor(
        puntos=puntos_historicos,
        x_eval=x_eval,
        cantidad_puntos=4,
        valor_real=valor_real_simulado
    )

    print(resultado)

    print("\nCOMPARACIÓN CON DIFERENTES PUNTOS")
    comparacion = comparar_estimaciones(
        puntos=puntos_historicos,
        x_eval=x_eval,
        valor_real=valor_real_simulado,
        cantidades=(3, 4, 5, 6)
    )

    for item in comparacion:
        print(item)

    print("\nPOSIBLE FENÓMENO DE RUNGE")
    print(detectar_posible_runge(comparacion))