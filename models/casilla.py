
TIPO_SALIDA = "salida"
TIPO_ISLA = "isla"
TIPO_EVENTO = "evento"
TIPO_ROAD_PONEGLYPH = "road_poneglyph"
TIPO_YONKO = "yonko"
TIPO_CARCEL = "carcel"
TIPO_IMPUESTO = "impuesto"
TIPO_DESCANSO = "descanso"

class Casilla:
    def __init__(
        self,
        id_casilla,
        nombre,
        tipo,
        posicion,
        x,
        y,
        ancho=72,
        alto=72,
        referencia=None
    ):
        # Identificación de la casilla
        self.id_casilla = id_casilla
        self.nombre = nombre
        self.tipo = tipo

        # Posición lógica dentro del tablero
        # Ejemplo: 0 = salida, 1 = primera casilla, 35 = última casilla
        self.posicion = posicion

        # Coordenadas visuales donde irá la ficha
        self.x = x
        self.y = y

        # Tamaño visual de la casilla
        self.ancho = ancho
        self.alto = alto

        # Referencia opcional
        # Puede servir para conectar esta casilla con una propiedad, evento, Road Poneglyph, etc.
        self.referencia = referencia

    def obtener_coordenadas(self):
        """
        Devuelve las coordenadas principales de la casilla.
        Sirve para mover la ficha del jugador.
        """
        return self.x, self.y

    def obtener_centro(self):
        """
        Devuelve el centro de la casilla.
        Puede servir si quieres colocar la ficha centrada.
        """
        centro_x = self.x + self.ancho // 2
        centro_y = self.y + self.alto // 2

        return centro_x, centro_y

    def es_tipo(self, tipo):
        """
        Verifica si la casilla es de un tipo específico.
        """
        return self.tipo == tipo

    def obtener_resumen(self):
        """
        Devuelve la información básica de la casilla.
        Sirve para depuración o pruebas.
        """
        return {
            "id_casilla": self.id_casilla,
            "nombre": self.nombre,
            "tipo": self.tipo,
            "posicion": self.posicion,
            "x": self.x,
            "y": self.y,
            "referencia": self.referencia
        }

    def __str__(self):
        return f"Casilla {self.posicion}: {self.nombre} ({self.tipo})"