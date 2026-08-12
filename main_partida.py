from partida import Partida
from tablero import Tablero
from ficha import Ficha
from posicion_posible import PosicionPosible


partida = Partida("fichas.csv")

print("Fichas en el pozo:", partida.pozo.cantidad())

print("\nJugador actual:")
print(partida.jugador_actual().nombre)

for jugador in partida.jugadores:

    jugador.mostrar_fichas()

print("\nTurno:", partida.jugador_actual().nombre)

partida.cambiar_turno()

print("Turno:", partida.jugador_actual().nombre)

partida.cambiar_turno()

print("Turno:", partida.jugador_actual().nombre)

#partida.tablero.mostrar_casillas()
#partida.tablero.mostrar_celdas()

f1 = Ficha((1, 10), (2, 7))
partida.tablero.colocar_primera_ficha(f1,partida.tablero.casillas[1])

print(partida.tablero.primera_jugada)
print(partida.tablero.head_posible.valor)
print(partida.tablero.tail_posible.valor)
print(partida.puede_jugar("Jugador 1"))
print(partida.puede_jugar("Jugador 2"))