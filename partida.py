from tablero import Tablero
from pozo import Pozo
from jugador import Jugador


class Partida:

    def __init__(self, archivo_fichas):

        # Tablero
        self.tablero = Tablero()

        # Pozo
        self.pozo = Pozo(archivo_fichas)

        # Jugadores
        self.jugadores = [
            Jugador("Jugador 1"),
            Jugador("Jugador 2")
        ]

        # Turno: índice de jugadores
        self.turno = 0

        # Estado de la partida
        self.terminada = False
        self.ganador = None

        # Reparto inicial
        self.repartir_fichas()


    def repartir_fichas(self):

        for jugador in self.jugadores:

            for _ in range(6):

                ficha = self.pozo.sacar()

                jugador.recibir_ficha(ficha)


    def jugador_actual(self):

        return self.jugadores[self.turno]


    def cambiar_turno(self):

        self.turno = (self.turno + 1) % len(self.jugadores)


    def puede_jugar(self, jugador):

        # Primera jugada
        if self.tablero.primera_jugada:
            return True

        valor_head = self.tablero.head_posible.valor
        valor_tail = self.tablero.tail_posible.valor

        for j in self.jugadores :
            if j.nombre == jugador :
                for ficha in j.fichas :
                    for valor in ficha.valores.values():
                        #print(valor)
                        if valor == valor_head or valor == valor_tail:
                            return True

        return False