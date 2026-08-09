class Extremo:

    def __init__(self, nombre):

        self.nombre = nombre

        # Casilla donde termina la cadena
        self.casilla = None

        # Celda que contiene el número a matchear
        self.celda = None

        # Fracción que debe igualarse
        self.numero = None


    def inicializar(self, casilla, celda):

        self.casilla = casilla
        self.celda = celda
        self.numero = celda.valor


    def siguiente_casilla(self, tablero):

        raise NotImplementedError


    def siguiente_celda(self, tablero):

        casilla = self.siguiente_casilla(tablero)

        return self.celda_siguiente_en_casilla(casilla)


    def celda_siguiente_en_casilla(self, casilla):

        raise NotImplementedError


    def mostrar(self):

        print(f"\n{self.nombre.upper()}")

        print("casilla :", self.casilla.numero)
        print("celda   :", self.celda.numero)
        print("numero  :", self.numero)


class Head(Extremo):

    def __init__(self):

        super().__init__("head")


    def siguiente_casilla(self, tablero):

        numero = (self.casilla.numero + 1) % len(tablero.casillas)

        return tablero.casillas[numero]


    def celda_siguiente_en_casilla(self, casilla):

        return casilla.celda_entrada()


class Tail(Extremo):

    def __init__(self):

        super().__init__("tail")


    def siguiente_casilla(self, tablero):

        numero = (self.casilla.numero - 1) % len(tablero.casillas)

        return tablero.casillas[numero]


    def celda_siguiente_en_casilla(self, casilla):

        return casilla.celda_salida()