# partida.py

from tablero import Tablero
from pozo import Pozo
from jugador import Jugador


class Partida:

    def __init__(self, archivo_fichas):

        # Tablero
        self.tablero = Tablero()

        # Pozo
        self.pozo = Pozo(archivo_fichas)

        # Jugadores
        self.jugadores = [
            Jugador("Jugador 1"),
            Jugador("Jugador 2")
        ]

        # Turno: índice de jugadores
        self.turno = 0

        # Estado de la partida
        self.terminada = False
        self.ganador = None

        # Flag: el jugador actual ya robó en este turno?
        self.ya_robo_en_turno = False
        self.ficha_robada = None  # <--- NUEVO: guardar la ficha robada

        # Reparto inicial
        self.repartir_fichas()


    def repartir_fichas(self):
        """Reparte 6 fichas a cada jugador"""
        for jugador in self.jugadores:
            for _ in range(6):
                ficha = self.pozo.sacar()
                if ficha is not None:
                    jugador.recibir_ficha(ficha)


    def jugador_actual(self):
        """Devuelve el jugador que tiene el turno"""
        return self.jugadores[self.turno]


    def cambiar_turno(self):
        """Cambia al siguiente jugador y resetea el flag de robo"""
        self.turno = (self.turno + 1) % len(self.jugadores)
        self.ya_robo_en_turno = False
        self.ficha_robada = None  # <--- NUEVO: resetear


    def puede_jugar(self, jugador):
        """Verifica si el jugador tiene alguna jugada posible con sus fichas actuales"""
        # Si no tiene fichas, no puede jugar
        if jugador.cantidad_fichas() == 0:
            return False
        
        # Primera jugada: siempre puede jugar si tiene fichas
        if self.tablero.primera_jugada:
            return True
        
        valor_head = self.tablero.head_posible.valor
        valor_tail = self.tablero.tail_posible.valor
        
        for ficha in jugador.fichas:
            # Verificar todos los valores de la ficha (O, E, N, S)
            for clave, valor in ficha.valores.items():
                if valor is not None:
                    if valor == valor_head or valor == valor_tail:
                        return True
        
        return False


    def puede_robar(self, jugador=None):
        """Verifica si el jugador puede robar del pozo"""
        if jugador is None:
            jugador = self.jugador_actual()
        
        # Ya robó en este turno
        if self.ya_robo_en_turno:
            return False
        
        # Pozo vacío
        if self.pozo.cantidad() == 0:
            return False
        
        return True


    def robar_ficha(self, jugador=None):
        """
        Roba una ficha del pozo.
        Retorna la ficha robada o None si no se puede.
        """
        if jugador is None:
            jugador = self.jugador_actual()
        
        if not self.puede_robar(jugador):
            return None
        
        ficha = self.pozo.sacar()
        if ficha is None:
            return None
        
        jugador.recibir_ficha(ficha)
        self.ya_robo_en_turno = True
        self.ficha_robada = ficha  # <--- NUEVO: guardar la ficha robada
        return ficha


    def pasar_turno(self, jugador=None):
        """
        Pasa el turno al siguiente jugador sin colocar ficha.
        Retorna True si se pudo pasar, False si no está permitido.
        """
        if jugador is None:
            jugador = self.jugador_actual()
        
        # Solo se puede pasar si ya se robó en este turno
        if not self.ya_robo_en_turno:
            return False
        
        self.cambiar_turno()
        return True

        

    def jugar_ficha(self, ficha, casilla):
        """
        Intenta colocar una ficha en una casilla.
        Solo cambia turno si tiene éxito.
        Retorna True si se colocó correctamente.
        """
        jugador = self.jugador_actual()
        
        # La ficha debe estar en la mano del jugador
        if ficha not in jugador.fichas:
            return False
        
        # Primera jugada
        if self.tablero.primera_jugada:
            colocada = self.tablero.colocar_primera_ficha(ficha, casilla)
        else:
            colocada = self.tablero.colocar_ficha(ficha, casilla)
        
        if not colocada:
            return False
        
        # La ficha deja de estar en la mano
        jugador.sacar_ficha(ficha)
        
        # Verificar si ganó
        if self.jugador_gano():
            self.terminada = True
            self.ganador = jugador
        
        # Cambiar turno (solo si se colocó correctamente)
        self.cambiar_turno()
        
        return True


    def jugador_gano(self):
        """Verifica si el jugador actual ganó (sin fichas)"""
        jugador = self.jugador_actual()
        return jugador.cantidad_fichas() == 0


    def partida_bloqueada(self):
        """Verifica si la partida está bloqueada (nadie puede jugar ni robar)"""
        for jugador in self.jugadores:
            if self.puede_jugar(jugador) or self.puede_robar(jugador):
                return False
        return True


    def obtener_ganador_por_menos_fichas(self):
        """
        Cuando la partida se bloquea, gana el que tiene menos fichas.
        Si empatan en cantidad, gana el que tiene menos suma de valores.
        Retorna el jugador ganador o None si hay empate total.
        """
        j1 = self.jugadores[0]
        j2 = self.jugadores[1]
        
        # Primero por cantidad de fichas
        if j1.cantidad_fichas() < j2.cantidad_fichas():
            return j1
        elif j2.cantidad_fichas() < j1.cantidad_fichas():
            return j2
        
        # Empate en cantidad: por suma de valores
        suma_j1 = 0
        for ficha in j1.fichas:
            for valor in ficha.valores.values():
                if valor is not None:
                    suma_j1 += valor
        
        suma_j2 = 0
        for ficha in j2.fichas:
            for valor in ficha.valores.values():
                if valor is not None:
                    suma_j2 += valor
        
        if suma_j1 < suma_j2:
            return j1
        elif suma_j2 < suma_j1:
            return j2
        else:
            return None  # Empate total


    def mostrar_estado(self):
        """Muestra el estado actual del juego (para consola)"""
        print("\n" + "="*60)
        print(f"TURNO: {self.jugador_actual().nombre}")
        print(f"Fichas en pozo: {self.pozo.cantidad()}")
        print(f"Fichas jugadas: {len(self.tablero.fichas_jugadas)}")
        if self.ya_robo_en_turno:
            print("📍 Ya robaste en este turno")
        print("="*60)