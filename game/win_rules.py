class WinRules:
    def verificar_victoria_road_poneglyphs(self, jugador):
        if jugador.tiene_4_road_poneglyphs():
            return {
                "hay_ganador": True,
                "ganador": jugador,
                "mensaje": f"{jugador.nombre} ganó al reunir los 4 Road Poneglyphs."
            }

        return {
            "hay_ganador": False,
            "ganador": None,
            "mensaje": ""
        }
        