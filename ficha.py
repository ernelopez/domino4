from fractions import Fraction

# IMPORTANTE:
# La orientación y los valores son estados independientes.
#
# girar_90() cambia solamente la orientación visual:
#     horizontal <-> vertical
#
# girar_180() intercambia valor1 y valor2.
#
# Ninguno de estos métodos intenta determinar si la ficha
# puede jugarse. El jugador decide la orientación de la ficha
# y, al soltarla, el Tablero/Juego verifica si esa configuración
# es válida para la casilla y el extremo elegido.
#
# NO hacer giros automáticamente dentro de puede_jugar().

class Ficha:

    def __init__(self, valor1, valor2):

        # Valores matemáticos
        self.valor1 = Fraction(*valor1)
        self.valor2 = Fraction(*valor2)

        # Textos para mostrar
        self.texto1 = f"{valor1[0]}/{valor1[1]}"
        self.texto2 = f"{valor2[0]}/{valor2[1]}"

        # Orientación visual
        self.orientacion = "horizontal"

        # Casilla que ocupa en el tablero
        self.casilla = None

        # Estado de la ficha:
        # "pozo", "mano", "tablero"
        self.estado = "pozo"

        # Jugador dueño
        # None si está en el tablero
        self.duenio = None


    def girar_90(self):
        """
        Gira la ficha 90 grados.
        """

        if self.orientacion == "horizontal":
            self.orientacion = "vertical"
        else:
            self.orientacion = "horizontal"


    def girar_180(self):
        """
        Invierte los extremos de la ficha.
        """

        self.valor1, self.valor2 = self.valor2, self.valor1

        self.texto1, self.texto2 = self.texto2, self.texto1


    def extremos(self):
        """
        Devuelve los dos valores actuales de la ficha.
        """

        return self.valor1, self.valor2


    def __str__(self):

        return f"( {self.texto1} | {self.texto2} )"