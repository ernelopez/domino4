from pozo import Pozo
from jugador import Jugador


pozo = Pozo("fichas.csv")

jugador1 = Jugador("Jugador 1")
jugador2 = Jugador("Jugador 2")


for _ in range(6):
    jugador1.recibir_ficha(pozo.sacar())
    jugador2.recibir_ficha(pozo.sacar())


jugador1.mostrar_fichas()
jugador2.mostrar_fichas()

print("\nFichas en el pozo:", pozo.cantidad())

