#tablero.mostrar_casillas()
#tablero.mostrar_celdas()


from tablero import Tablero
from ficha import Ficha
from posicion_posible import PosicionPosible

tablero = Tablero()

primera = Ficha((2, 7), (1, 12))
primera.mostrar_ficha()

tablero.colocar_primera_ficha(primera,tablero.casillas[6])

print("\n=== TAIL POSIBLE ===")
tablero.tail_posible.mostrar()

print("\n=== HEAD POSIBLE ===")
tablero.head_posible.mostrar()

segunda = Ficha((1, 12), (1, 7))
segunda.girar_90()
segunda.girar_90()
segunda.girar_90()
segunda.mostrar_ficha()


resultado = tablero.puede_colocar(segunda,tablero.casillas[7])

#print("¿Puede colocar?", resultado)
print("¿Puede colocar?", resultado[0].posicion, resultado[0].casilla.numero, resultado[0].celda.numero, resultado[0].valor, resultado[1])

tablero.colocar_ficha(segunda, tablero.casillas[7])

print("\n=== TAIL POSIBLE ===")
tablero.tail_posible.mostrar()

print("\n=== HEAD POSIBLE ===")
tablero.head_posible.mostrar()