from tablero import Tablero
from ficha import Ficha
from posicion_posible import PosicionPosible

tablero = Tablero()
#tablero.mostrar_casillas()
#tablero.mostrar_celdas()

f1 = Ficha((1, 7), (2, 7))
f2 = Ficha((2, 7), (3, 7))
f3 = Ficha((3, 7), (4, 7))
f4 = Ficha((4, 7), (5, 7))
f5 = Ficha((5, 7), (6, 7))
f6 = Ficha((6, 7), (7, 7))
f7 = Ficha((8, 7), (7, 7))
f8 = Ficha((9, 7), (8, 7))
f9 = Ficha((10, 7), (9, 7))
f10 = Ficha((11, 7), (10, 7))
f11 = Ficha((12, 7), (11, 7))
f12 = Ficha((13, 7), (12, 7))
f13 = Ficha((14, 7), (13, 7))
f14 = Ficha((15, 7), (14, 7))
f15 = Ficha((16, 7), (15, 7))

f7.girar_90()
f8.girar_90()
f9.girar_90()
f10.girar_90()
f11.girar_90()
f12.girar_90()
f13.girar_90()
f14.girar_90()

tablero.colocar_primera_ficha(f1,tablero.casillas[1])
tablero.colocar_ficha(f2, tablero.casillas[2])
tablero.colocar_ficha(f3, tablero.casillas[3])
tablero.colocar_ficha(f4, tablero.casillas[4])
tablero.colocar_ficha(f5, tablero.casillas[5])
tablero.colocar_ficha(f6, tablero.casillas[6])
tablero.colocar_ficha(f7, tablero.casillas[7])
tablero.colocar_ficha(f8, tablero.casillas[8])
tablero.colocar_ficha(f9, tablero.casillas[9])
tablero.colocar_ficha(f10, tablero.casillas[10])
tablero.colocar_ficha(f11, tablero.casillas[11])
tablero.colocar_ficha(f12, tablero.casillas[12])
tablero.colocar_ficha(f13, tablero.casillas[13])
tablero.colocar_ficha(f14, tablero.casillas[14])
tablero.colocar_ficha(f15, tablero.casillas[15])

g1 = Ficha((1, 5), (1, 7))
g2 = Ficha((2, 5), (1, 5))
g3 = Ficha((3, 5), (2, 5))
g4 = Ficha((4, 5), (3, 5))
g5 = Ficha((5, 5), (4, 5))
g6 = Ficha((6, 5), (5, 5))
g7 = Ficha((7, 5), (6, 5))
g8 = Ficha((8, 5), (7, 5))
g9 = Ficha((9, 5), (8, 5))
g10 = Ficha((9,5),(2,17))

tablero.colocar_ficha(g1, tablero.casillas[0])

g2.girar_90()
g3.girar_90()
g4.girar_90()
g5.girar_90()
g6.girar_90()
g7.girar_90()
g8.girar_90()
g9.girar_90()

tablero.colocar_ficha(g2, tablero.casillas[29])
tablero.colocar_ficha(g3, tablero.casillas[28])
tablero.colocar_ficha(g4, tablero.casillas[27])
tablero.colocar_ficha(g5, tablero.casillas[26])
tablero.colocar_ficha(g6, tablero.casillas[25])
tablero.colocar_ficha(g7, tablero.casillas[24])
tablero.colocar_ficha(g8, tablero.casillas[23])
tablero.colocar_ficha(g9, tablero.casillas[22])

tablero.colocar_ficha(g10, tablero.casillas[21])



for i in range(35):
	print(i,tablero.celdas[i].valor)

print("\n=== TAIL POSIBLE ===")
tablero.tail_posible.mostrar()

print("\n=== HEAD POSIBLE ===")
tablero.head_posible.mostrar()

#resultado = tablero.puede_colocar(f2,tablero.casillas[2])

#print("¿Puede colocar?", resultado)
#print("¿Puede colocar?", resultado[0].posicion, resultado[0].casilla.numero, resultado[0].celda.numero, resultado[0].valor, resultado[1])
