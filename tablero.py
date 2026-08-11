from casilla import Casilla
from config import LARGO_FICHA, ANCHO_FICHA, MARGEN_TABLERO
from posicion_posible import PosicionPosible


class Tablero:

    def __init__(self):

        self.casillas = []
        self.celdas = [None] * 60

        self.head_posible = PosicionPosible()
        self.tail_posible = PosicionPosible()

        self.crear_casillas()

        self.primera_jugada = True


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



    def colocar_primera_ficha(self, ficha, casilla):

        # La orientación de la ficha debe coincidir
        # con la orientación de la casilla.
        if ficha.orientacion != casilla.orientacion:
            print("MAL")
            return False

        # -------------------------------------------------
        # Colocar la ficha
        # -------------------------------------------------

        casilla.ficha = ficha
        ficha.casilla = casilla
        ficha.estado = "tablero"


        # -------------------------------------------------
        # Guardar los valores de la ficha en las celdas
        # -------------------------------------------------

        if casilla.orientacion == "horizontal":

            casilla.celda1.valor = ficha.valores["O"]
            casilla.celda2.valor = ficha.valores["E"]

        else:

            casilla.celda1.valor = ficha.valores["N"]
            casilla.celda2.valor = ficha.valores["S"]


        # -------------------------------------------------
        # Crear posición posible para TAIL
        # -------------------------------------------------

        casilla_tail = self.casillas[
            (casilla.numero - 1) % 30 ]
        celda_tail = self.celdas[casilla_tail.numero*2+1]
        if casilla.numero < 7 :
            valor_tail = ficha.valores["O"]
        elif casilla.numero < 15 :
            valor_tail = ficha.valores["N"]
        elif casilla.numero < 22 :
            valor_tail = ficha.valores["E"]
        else :
            valor_tail = ficha.valores["S"]

        self.tail_posible.inicializar(casilla_tail,
                                      celda_tail,
                                      casilla_tail.orientacion,
                                      valor_tail)

        # -------------------------------------------------
        # Crear posición posible para HEAD
        # -------------------------------------------------

        casilla_head = self.casillas[
            (casilla.numero + 1) % 30 ]

        celda_head = self.celdas[casilla_head.numero*2]
        if casilla.numero < 7 :
            valor_head = ficha.valores["E"]
        elif casilla.numero < 15 :
            valor_head = ficha.valores["S"]
        elif casilla.numero < 22 :
            valor_head = ficha.valores["O"]
        else :
            valor_head = ficha.valores["N"]

        self.head_posible.inicializar(casilla_head,
                                      celda_head,
                                      casilla_head.orientacion,
                                      valor_head)
        return True


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


    def puede_colocar(self, ficha, casilla):

        resu = False
        #print(casilla.numero,self.head_posible.casilla.numero)
        #print(ficha.orientacion,self.head_posible.orientacion)

        #Chequeo si coincide con head_posible
        if casilla.numero == self.head_posible.casilla.numero and ficha.orientacion == self.head_posible.orientacion : 
            hv , hp = self.head_posible.valor , self.head_posible.posicion
            fv = ficha.valores[hp]
            #print(hv,hp,fv)
            if hv==fv :
                print("Eureka head")
                resu = True
        elif casilla.numero == self.tail_posible.casilla.numero and ficha.orientacion == self.tail_posible.orientacion : 
            tv , tp = self.tail_posible.valor , self.tail_posible.posicion
            fv = ficha.valores[tp]
            if tv==fv :
                print("Eureka tail")
                resu = True
        
        return resu



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
                casilla.celda2
            )

        else:

            self.tail.inicializar(
                casilla,
                casilla.celda1
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