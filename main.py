#tablero.mostrar_casillas()
#tablero.mostrar_celdas()

from tablero import Tablero
from ficha import Ficha


tablero = Tablero()


# Primera ficha
primera = Ficha(
    (3, 12),
    (4, 12)
)

tablero.colocar_primera_ficha(primera)


# Segunda ficha: head
ficha2 = Ficha(
    (4, 12),
    (1, 3)
)

tablero.colocar_ficha(
    ficha2,
    tablero.casillas[4]
)


# Tercera ficha: tail
ficha3 = Ficha(
    (2, 10),
    (1, 4)
)

tablero.colocar_ficha(
    ficha3,
    tablero.casillas[2]
)


# Cuarta ficha: head → casilla 5
ficha4 = Ficha(
    (1, 3),
    (2, 7)
)

tablero.colocar_ficha(
    ficha4,
    tablero.casillas[5]
)


# Quinta ficha: head → casilla 6
ficha5 = Ficha(
    (2, 7),
    (5, 8)
)

tablero.colocar_ficha(
    ficha5,
    tablero.casillas[6]
)


# Sexta ficha: head → casilla 7
ficha6 = Ficha(
    (5, 8),
    (3, 10)
)

ficha6.girar_90()

print(
    "\n¿Puede jugar la sexta ficha?",
    tablero.puede_jugar(ficha6, tablero.casillas[7])
)

print(
    "Orientación:",
    ficha6.orientacion
)

print(
    "Casilla:",
    tablero.casillas[7].orientacion
)


tablero.colocar_ficha(
    ficha6,
    tablero.casillas[7]
)

# Séptima ficha: head → casilla 8
ficha7 = Ficha(
    (3, 10),
    (1, 2)
)

print(
    "\n¿Puede jugar en casilla 8?",
    tablero.puede_jugar(ficha7, tablero.casillas[8])
)

ficha7.girar_90()

print(
    "\n¿Puede jugar en casilla 8?",
    tablero.puede_jugar(ficha7, tablero.casillas[8])
)

tablero.colocar_ficha(
    ficha7,
    tablero.casillas[8]
)


ficha8 = Ficha(
    (1, 2),
    (3, 5)
)

ficha8.girar_90()

print(
    "\n¿Puede jugar en casilla 9?",
    tablero.puede_jugar(ficha8, tablero.casillas[9])
)

tablero.colocar_ficha(
    ficha8,
    tablero.casillas[9]
)

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

