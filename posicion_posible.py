class PosicionPosible:

    def __init__(self):

        # Casilla donde se puede colocar la ficha
        self.casilla = None

        # Celda concreta de la casilla donde debe
        # caer el extremo que hace match
        self.celda = None

        # Valor que debe coincidir
        self.valor = None

        # Orientación que debe tener la ficha
        self.orientacion = None

        # Posición de la ficha que debe matchear
        # esa celda: "O", "E", "N" o "S"
        self.posicion = None


    def inicializar(self, casilla, celda, valor):

        direccion = casilla.orientacion
        self.casilla = casilla
        self.celda = celda
        #self.direccion = direccion
        self.valor = valor
        self.orientacion = direccion
        
        if direccion == "horizontal" and celda.numero in [0,2,4,6,8,10,12] :
            self.posicion = "O"
        elif direccion == "horizontal" and celda.numero in [1,3,5,7,9,11,13] :
            self.posicion = "E"
        elif direccion == "vertical" and celda.numero in [14,16,18,20,22,24,26,28] :
            self.posicion = "N"
        elif direccion == "vertical" and celda.numero in [15,17,19,21,23,25,27,29] :
            self.posicion = "S"
        elif direccion == "horizontal" and celda.numero in [30,32,34,36,38,40,42] :
            self.posicion = "E"
        elif direccion == "horizontal" and celda.numero in [31,33,35,37,39,41,43] :
            self.posicion = "O"
        elif direccion == "vertical" and celda.numero in [44,46,48,50,52,54,56,58] :
            self.posicion = "S"
        elif direccion == "vertical" and celda.numero in [45,47,49,51,53,55,57,59] :
            self.posicion = "N"


    def mostrar(self):
        print(f"Casilla     : {self.casilla.numero}")
        print(f"Celda       : {self.celda.numero}")
        print(f"Debe haber  : {self.valor}")
        print(f"Orientación : {self.orientacion}")
        print(f"Posición    : {self.posicion}")