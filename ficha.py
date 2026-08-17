from fractions import Fraction


class Ficha:

    def __init__(self, valor1, valor2):

        # -------------------------------------------------
        # Valores matemáticos
        # -------------------------------------------------

        self.valores = {}
        self.valores["O"] = Fraction(*valor1)
        self.valores["E"] = Fraction(*valor2)

        self.valores["N"] = None
        self.valores["S"] = None


        # -------------------------------------------------
        # Textos para mostrar
        # -------------------------------------------------

        self.textos = {}
        self.textos["O"] = f"{valor1[0]}/{valor1[1]}"
        self.textos["E"] = f"{valor2[0]}/{valor2[1]}"

        self.textos["N"] = None
        self.textos["S"] = None


        # -------------------------------------------------
        # Orientación visual
        # -------------------------------------------------

        self.orientacion = "horizontal"


        # -------------------------------------------------
        # Casilla que ocupa en el tablero
        # -------------------------------------------------

        self.casilla = None


        # -------------------------------------------------
        # Estado de la ficha
        # "pozo", "mano", "tablero"
        # -------------------------------------------------

        self.estado = "pozo"


        # -------------------------------------------------
        # Jugador dueño
        # None si está en el tablero
        # -------------------------------------------------

        self.duenio = None


    def girar_90(self):
        """
        Gira la ficha 90 grados en sentido antihorario.
        """

        # Guardamos los cuatro valores actuales
        O = self.valores["O"]
        E = self.valores["E"]
        N = self.valores["N"]
        S = self.valores["S"]

        # Guardamos los cuatro textos actuales
        texto_O = self.textos["O"]
        texto_E = self.textos["E"]
        texto_N = self.textos["N"]
        texto_S = self.textos["S"]


        # -------------------------------------------------
        # Rotación antihoraria:
        #
        # E → N
        # S → E
        # O → S
        # N → O
        # -------------------------------------------------

        self.valores["N"] = E
        self.valores["O"] = N
        self.valores["S"] = O
        self.valores["E"] = S

        self.textos["N"] = texto_E
        self.textos["O"] = texto_N
        self.textos["S"] = texto_O
        self.textos["E"] = texto_S


        # Cambia la orientación
        if self.orientacion == "horizontal":
            self.orientacion = "vertical"
        else:
            self.orientacion = "horizontal"


    def mostrar_ficha(self):

        print(
            self.orientacion,
            f"O:{self.textos["O"]}",
            f"E:{self.textos["E"]}",
            f"N:{self.textos["N"]}",
            f"S:{self.textos["S"]}"
        )

    # Agregados por DeepSeek
    def mostrar_valores(self):
        """Devuelve una representación legible de la ficha con las fracciones originales"""
        if self.orientacion == "horizontal":
            return f"[{self.textos['O']} | {self.textos['E']}]"
        else:
            return f"[{self.textos['N']} | {self.textos['S']}]"

    def __str__(self):
        """Representación en string de la ficha"""
        return self.mostrar_valores()

    def __repr__(self):
        return self.mostrar_valores()
