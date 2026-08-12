import csv
import random
from ficha import Ficha


class Pozo:

    def __init__(self, archivo):

        self.fichas = []

        self.cargar(archivo)


    def cargar(self, archivo):

        with open(archivo, newline="", encoding="utf-8") as f:

            lector = csv.DictReader(f)

            for fila in lector:

                ficha = Ficha(
                    (
                        int(fila["izq_num"]),
                        int(fila["izq_den"])
                    ),
                    (
                        int(fila["der_num"]),
                        int(fila["der_den"])
                    )
                )

                self.fichas.append(ficha)

        random.shuffle(self.fichas)


    def sacar(self):

        if not self.fichas:
            return None

        return self.fichas.pop()


    def cantidad(self):

        return len(self.fichas)