from casilla import Casilla
from extremos import Head, Tail
from config import LARGO_FICHA, ANCHO_FICHA, MARGEN_TABLERO


class Tablero:

    def __init__(self):

        self.casillas = []
        self.celdas = [None] * 60

        self.head = Head()
        self.tail = Tail()

        self.crear_casillas()


    def agregar_casilla(self, casilla):

        casilla.calcular_posiciones_celdas(
            LARGO_FICHA,
            ANCHO_FICHA
        )

        self.casillas.append(casilla)

        self.celdas[casilla.celda1.numero] = casilla.celda1
        self.celdas[casilla.celda2.numero] = casilla.celda2


    def crear_casillas(self):

        numero = 0

        # -------------------------
        # Superior
        # -------------------------

        x = MARGEN_TABLERO + ANCHO_FICHA
        y = MARGEN_TABLERO

        for _ in range(7):

            casilla = Casilla(
                numero,
                "horizontal",1,
                2 * numero,
                2 * numero + 1,
                x,
                y
            )

            self.agregar_casilla(casilla)

            numero += 1
            x += LARGO_FICHA


        # -------------------------
        # Derecha
        # -------------------------

        x = MARGEN_TABLERO + 8 * LARGO_FICHA - ANCHO_FICHA
        y = MARGEN_TABLERO

        for _ in range(8):

            casilla = Casilla(
                numero,
                "vertical",1,
                2 * numero,
                2 * numero + 1,
                x,
                y
            )

            self.agregar_casilla(casilla)

            numero += 1
            y += LARGO_FICHA


        # -------------------------
        # Inferior
        # -------------------------

        #x = MARGEN_TABLERO + 7 * LARGO_FICHA
        x = MARGEN_TABLERO - ANCHO_FICHA + 7 * LARGO_FICHA #Corrección
        y = MARGEN_TABLERO + 8 * LARGO_FICHA - ANCHO_FICHA

        for _ in range(7):

            casilla = Casilla(
                numero,
                "horizontal",-1,
                2 * numero,
                2 * numero + 1,
                x,
                y
            )

            self.agregar_casilla(casilla)

            numero += 1
            x -= LARGO_FICHA


        # -------------------------
        # Izquierda
        # -------------------------

        x = MARGEN_TABLERO
        y = MARGEN_TABLERO + 7 * LARGO_FICHA

        for _ in range(8):

            casilla = Casilla(
                numero,
                "vertical",-1,
                2 * numero,
                2 * numero + 1,
                x,
                y
            )

            self.agregar_casilla(casilla)

            numero += 1
            y -= LARGO_FICHA



    def colocar_primera_ficha(self, ficha):

        # La primera ficha siempre va en la casilla 3
        casilla = self.casillas[3]

        # La casilla queda ocupada
        casilla.ficha = ficha

        # La ficha sabe dónde está
        ficha.casilla = casilla

        # Guardamos los valores de la ficha en las celdas
        casilla.celda1.valor = ficha.valor1
        casilla.celda2.valor = ficha.valor2

        # El tail queda en la celda de entrada
        # del recorrido de la casilla 3
        self.tail.inicializar(
            casilla,
            casilla.celda_entrada()
        )

        # El head queda en la celda de salida
        # del recorrido de la casilla 3
        self.head.inicializar(
            casilla,
            casilla.celda_salida()
        )


    def mostrar_casillas(self):

        print("\n=== CASILLAS ===\n")

        for casilla in self.casillas:

            print(
                f"{casilla.numero:2d}  "
                f"{casilla.orientacion:10s}  "
                f"({casilla.x:3d},{casilla.y:3d})  "
                f"celdas=({casilla.celda1.numero:2d},{casilla.celda2.numero:2d})"
            )


    def mostrar_celdas(self):

        print("\n=== CELDAS ===\n")

        for celda in self.celdas:

            print(
                f"{celda.numero:2d}  "
                f"({celda.x:6.1f},{celda.y:6.1f})  "
                f"casilla={celda.casilla.numero:2d}"
            )


    def probar_extremos(self):

        print("\n=== EXTREMOS ===")

        self.head.mostrar()

        siguiente = self.head.siguiente_casilla(self)

        print("siguiente casilla :", siguiente.numero)
        print("siguiente celda   :", self.head.siguiente_celda(self).numero)

        self.tail.mostrar()

        siguiente = self.tail.siguiente_casilla(self)

        print("siguiente casilla :", siguiente.numero)
        print("siguiente celda   :", self.tail.siguiente_celda(self).numero)



    def puede_jugar(self, ficha, casilla):

        # -------------------------------------------------
        # 1. La casilla tiene que ser una de las dos
        #    casillas siguientes a los extremos
        # -------------------------------------------------

        casilla_head = self.head.siguiente_casilla(self)
        casilla_tail = self.tail.siguiente_casilla(self)

        if casilla.numero == casilla_head.numero:

            extremo = self.head

        elif casilla.numero == casilla_tail.numero:

            extremo = self.tail

        else:

            return False


        # -------------------------------------------------
        # 2. La orientación de la ficha debe coincidir
        #    con la orientación de la casilla
        # -------------------------------------------------

        if ficha.orientacion != casilla.orientacion:

            return False


        # -------------------------------------------------
        # 3. Identificamos la celda de la casilla que
        #    debe coincidir con el extremo
        # -------------------------------------------------

        celda_conexion = extremo.siguiente_celda(self)


        # -------------------------------------------------
        # 4. Construimos temporalmente cómo quedarían
        #    las dos celdas de la casilla
        # -------------------------------------------------

        if casilla.sentido == 1:

            valor_celda1 = ficha.valor1
            valor_celda2 = ficha.valor2

        else:

            valor_celda1 = ficha.valor2
            valor_celda2 = ficha.valor1


        # -------------------------------------------------
        # 5. Comprobamos la celda de conexión
        # -------------------------------------------------

        if celda_conexion == casilla.celda1:

            return valor_celda1 == extremo.numero

        elif celda_conexion == casilla.celda2:

            return valor_celda2 == extremo.numero

        return False


    def colocar_ficha(self, ficha, casilla):

        # Primero verificamos que la jugada sea válida
        if not self.puede_jugar(ficha, casilla):
            return False

        # -------------------------------------------------
        # Identificar por qué extremo se está jugando
        # -------------------------------------------------

        if casilla.numero == self.head.siguiente_casilla(self).numero:

            extremo = self.head

        else:

            extremo = self.tail


        # -------------------------------------------------
        # Colocar la ficha en la casilla
        # -------------------------------------------------

        casilla.ficha = ficha
        ficha.casilla = casilla
        ficha.estado = "tablero"


        # -------------------------------------------------
        # Determinar qué valor ocupa cada celda
        # -------------------------------------------------

        if casilla.sentido == 1:

            casilla.celda1.valor = ficha.valor1
            casilla.celda2.valor = ficha.valor2

        else:

            casilla.celda1.valor = ficha.valor2
            casilla.celda2.valor = ficha.valor1


        # -------------------------------------------------
        # Actualizar el extremo correspondiente
        # -------------------------------------------------

        if extremo is self.head:

            self.head.inicializar(
                casilla,
                casilla.celda_salida()
            )

        else:

            self.tail.inicializar(
                casilla,
                casilla.celda_entrada()
            )

        return True


    def fichas_jugadas(self):

        jugadas = []

        for casilla in self.casillas:

            if casilla.ficha is not None:

                jugadas.append(
                    (
                        casilla.numero,
                        casilla.ficha,
                        casilla.celda1.numero,
                        casilla.celda2.numero
                    )
                )

        return jugadas