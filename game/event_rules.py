import random


class EventRules:

    def __init__(self):
        self.eventos_riesgo = [
            {
                "mensaje": "Tormenta en Grand Line. Pierdes $150.",
                "tipo": "dinero",
                "valor": -150
            },
            {
                "mensaje": "Daño en el barco. Pierdes $200.",
                "tipo": "dinero",
                "valor": -200
            },
            {
                "mensaje": "Problemas con la Marina. Pierdes 1 turno.",
                "tipo": "turno",
                "valor": 1
            }
        ]

        self.eventos_recompensa = [
            {
                "mensaje": "Encontraste un tesoro. Ganas $200.",
                "tipo": "dinero",
                "valor": 200
            },
            {
                "mensaje": "Recompensa por captura. Ganas $300.",
                "tipo": "dinero",
                "valor": 300
            }
        ]

        self.eventos_marina = [
            {
                "mensaje": "Inspección naval. Pagas $100.",
                "tipo": "dinero",
                "valor": -100
            },
            {
                "mensaje": "Impuesto especial. Pagas $150.",
                "tipo": "dinero",
                "valor": -150
            }
        ]

    def ejecutar_evento(self, jugador, referencia):

        if referencia == "evento_riesgo":
            evento = random.choice(self.eventos_riesgo)

        elif referencia == "evento_marina":
            evento = random.choice(self.eventos_marina)

        else:
            evento = random.choice(self.eventos_recompensa)

        if evento["tipo"] == "dinero":

            if evento["valor"] > 0:
                jugador.sumar_dinero(evento["valor"])
            else:
                jugador.restar_dinero(abs(evento["valor"]))

        elif evento["tipo"] == "turno":
            jugador.perder_turno(evento["valor"])

        return evento["mensaje"]