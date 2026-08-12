from pozo import Pozo

pozo = Pozo("fichas.csv")

print("Cantidad de fichas:", pozo.cantidad())

ficha = pozo.sacar()

print("\nFicha extraída:")
ficha.mostrar_ficha()

print("\nQuedan:", pozo.cantidad())