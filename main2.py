#tablero.mostrar_casillas()
#tablero.mostrar_celdas()

from tablero import Tablero
from ficha import Ficha


tablero = Tablero()


# Primera ficha
ficha1 = Ficha((1, 12),(2, 12))
ficha2 = Ficha((2, 12),(3, 12))
ficha3 = Ficha((3, 12),(4, 12))
ficha4 = Ficha((4, 12),(5, 12))

ficha5 = Ficha((5, 12),(6, 12))
ficha6 = Ficha((6, 12),(7, 12))
ficha7 = Ficha((7, 12),(8, 12))
ficha8 = Ficha((8, 12),(9, 12))
ficha9 = Ficha((9, 12),(10, 12))
ficha10 = Ficha((10, 12),(11, 12))
ficha11 = Ficha((11, 12),(12, 12))
ficha12 = Ficha((12, 12),(13, 12))

ficha13 = Ficha((13, 12),(14, 12))

tablero.colocar_primera_ficha(ficha1)
tablero.colocar_ficha(ficha2,tablero.casillas[4])
tablero.colocar_ficha(ficha3,tablero.casillas[5])
tablero.colocar_ficha(ficha4,tablero.casillas[6])

ficha5.girar_90()
ficha6.girar_90()
ficha7.girar_90()
ficha8.girar_90()
ficha9.girar_90()
ficha10.girar_90()
ficha11.girar_90()
ficha12.girar_90()

tablero.colocar_ficha(ficha5,tablero.casillas[7])
tablero.colocar_ficha(ficha6,tablero.casillas[8])
tablero.colocar_ficha(ficha7,tablero.casillas[9])
tablero.colocar_ficha(ficha8,tablero.casillas[10])
tablero.colocar_ficha(ficha9,tablero.casillas[11])
tablero.colocar_ficha(ficha10,tablero.casillas[12])
tablero.colocar_ficha(ficha11,tablero.casillas[13])
tablero.colocar_ficha(ficha12,tablero.casillas[14])

#Esto no está funcionando! Interpreta la ficha al revés de lo que debería en la línea de abajo.
ficha13.girar_180()
tablero.colocar_ficha(ficha13,tablero.casillas[15])


tablero.head.mostrar()


# -------------------------------------------------
# Fichas jugadas
# -------------------------------------------------

print("\n=== FICHAS JUGADAS ===")

for casilla, ficha, celda1, celda2 in tablero.fichas_jugadas():

    print(
        f"Casilla {casilla}: "
        f"{ficha} "
        f"celdas {celda1}-{celda2}"
    )

'''
# -------------------------------------------------
# Prueba 1: horizontal en casilla 2
# -------------------------------------------------
#ficha.rotar_90()
casilla = tablero.casillas[2]

print("\nPrueba 1")
print("Ficha:", ficha)
print("Orientación:", ficha.orientacion)
print("Casilla:", casilla.numero)

print("Resultado:", tablero.puede_jugar(ficha, casilla))
'''

