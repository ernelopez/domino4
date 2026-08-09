from tablero import Tablero
from ficha import Ficha


tablero = Tablero()

#tablero.mostrar_casillas()
#tablero.mostrar_celdas()


# Primera ficha: (3/12 | 4/12)
primera = Ficha(
    (3, 12),
    (4, 12)
)

tablero.colocar_primera_ficha(primera)


# -------------------------------------------------
# Ficha de prueba
# -------------------------------------------------


ficha = Ficha(
    (4, 12),
    (1, 3)
)

casilla = tablero.casillas[4]

print(
    "¿Puede jugar?",
    tablero.puede_jugar(ficha, casilla)
)

print(
    "¿Se colocó?",
    tablero.colocar_ficha(ficha, casilla)
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

