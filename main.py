#tablero.mostrar_casillas()
#tablero.mostrar_celdas()


from tablero import Tablero
from ficha import Ficha
from posicion_posible import PosicionPosible

tablero = Tablero()

primera = Ficha((2, 7), (1, 12))
#primera.girar_90()
#primera.girar_90()

tablero.colocar_primera_ficha(primera,tablero.casillas[3])

print("\n=== TAIL POSIBLE ===")
tablero.tail_posible.mostrar()

print("\n=== HEAD POSIBLE ===")
tablero.head_posible.mostrar()

segunda = Ficha((1, 15), (2, 7))
tablero.puede_colocar(segunda,tablero.casillas[2])