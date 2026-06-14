class Propiedad:
    def __init__(
        self,
        nombre,
        referencia,
        tipo,
        grupo,
        precio_base
    ):
        self.nombre = nombre
        self.referencia = referencia
        self.tipo = tipo
        self.grupo = grupo
        self.precio_base = precio_base
        self.precio_actual = precio_base

        self.dueno = None
        self.nivel_mejora = 0
        self.tiene_yonkou = False

    def esta_libre(self):
        return self.dueno is None

    def asignar_dueno(self, jugador):
        self.dueno = jugador

    def quitar_dueno(self):
        self.dueno = None

    def es_del_jugador(self, jugador):
        return self.dueno == jugador

    def puede_mejorarse(self):
        return self.nivel_mejora < 4 and self.tipo == "isla"

    def calcular_costo_mejora(self):
        return int(self.precio_actual * 0.25)

    def calcular_impuesto(self):
        impuesto = int(self.precio_actual * 0.12)
        impuesto += int(self.precio_actual * 0.08 * self.nivel_mejora)

        if self.tiene_yonkou:
            impuesto = int(impuesto * 1.75)

        return impuesto

    def calcular_recompra(self, tiene_monopolio=False):
        if tiene_monopolio:
            return int(self.precio_actual * 1.80)

        return int(self.precio_actual * 1.50)

    def mejorar(self):
        if self.puede_mejorarse():
            self.nivel_mejora += 1
            return True

        return False