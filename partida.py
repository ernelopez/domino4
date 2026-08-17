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

        # Reparto inicial
        self.repartir_fichas()


    def repartir_fichas(self):

        for jugador in self.jugadores:

            for _ in range(6):

                ficha = self.pozo.sacar()

                jugador.recibir_ficha(ficha)


    def jugador_actual(self):

        return self.jugadores[self.turno]


    def cambiar_turno(self):

        self.turno = (self.turno + 1) % len(self.jugadores)


    def puede_jugar(self, jugador):

        # Primera jugada
        if self.tablero.primera_jugada:
            return True

        valor_head = self.tablero.head_posible.valor
        valor_tail = self.tablero.tail_posible.valor

        for ficha in jugador.fichas:

            for valor in ficha.valores.values():

                if valor == valor_head or valor == valor_tail:
                    return True
        '''
        for j in self.jugadores :
            if j.nombre == jugador :
                for ficha in j.fichas :
                    for valor in ficha.valores.values():
                        #print(valor)
                        if valor == valor_head or valor == valor_tail:
                            return True
        '''
        return False


    def levantar_ficha(self, jugador):
        """Robar una ficha del pozo. Retorna la ficha o None si el pozo está vacío"""
        ficha = self.pozo.sacar()
        
        if ficha is None:
            return None
        
        jugador.recibir_ficha(ficha)
        return ficha



    def comprobar_derrota(self):

        jugador = self.jugador_actual()

        if jugador.cantidad_fichas() == 0:
            return False

        if self.pozo.cantidad() == 0 and not self.puede_jugar(jugador):
            return True

        return False


    def jugador_perdio(self):

        jugador = self.jugador_actual()

        return (
            self.pozo.cantidad() == 0
            and
            not self.puede_jugar(jugador)
        )


    def jugador_gano(self):

        jugador = self.jugador_actual()

        return jugador.cantidad_fichas() == 0


    #corregido por Deep Seek
    def jugar_ficha(self, ficha, casilla):
        """Intenta colocar una ficha en una casilla. Solo cambia turno si tiene éxito."""
        jugador = self.jugador_actual()

        # La ficha debe estar en la mano del jugador actual
        if ficha not in jugador.fichas:
            return False

        if self.tablero.primera_jugada:
            colocada = self.tablero.colocar_primera_ficha(ficha,casilla)
        else :
            colocada = self.tablero.colocar_ficha(ficha, casilla)

        # El tablero rechazó la jugada
        if not colocada:
            return False

        # La ficha deja de estar en la mano
        jugador.sacar_ficha(ficha)

        # ¿Ganó el jugador?
        if self.jugador_gano():
            self.terminada = True
            self.ganador = jugador
            #return True

        # Cambiar turno (solo si se colocó correctamente)
        self.cambiar_turno()

        return True



    #métodos creados por DeepSeek
    def turno_actual(self):
        """Ejecuta el turno del jugador actual"""
        jugador = self.jugador_actual()
        
        # Mostrar estado del juego
        self.mostrar_estado()
        
        # Verificar si el jugador puede jugar
        if not self.puede_jugar(jugador):
            print(f"\n{jugador.nombre} no puede jugar con sus fichas actuales.")
            
            # Intentar robar del pozo
            if self.pozo.cantidad() > 0:
                ficha = self.levantar_ficha(jugador)
                print(f"{jugador.nombre} robó una ficha del pozo.")
                
                # Si ahora puede jugar, sigue su turno
                if self.puede_jugar(jugador):
                    print(f"{jugador.nombre} ahora puede jugar.")
                    self.turno_actual()  # Reintenta el mismo turno
                    return
                else:
                    print(f"{jugador.nombre} aún no puede jugar. Pasa turno.")
            else:
                print(f"{jugador.nombre} pasa turno (pozo vacío).")
            
            # Cambiar turno
            self.cambiar_turno()
            return
        
        # Mostrar fichas del jugador
        jugador.mostrar_fichas()
        
        # Mostrar extremos disponibles
        self.mostrar_extremos()
        
        # Pedir jugada
        print(f"\n--- Turno de {jugador.nombre} ---")
        print("Selecciona una ficha (número) o 0 para pasar turno:")
        
        try:
            seleccion_ficha = int(input("Ficha: "))
            
            if seleccion_ficha == 0:
                print(f"{jugador.nombre} pasa turno.")
                self.cambiar_turno()
                return
            
            if 1 <= seleccion_ficha <= len(jugador.fichas):
                ficha = jugador.fichas[seleccion_ficha - 1]
                
                # Pedir casilla
                print("¿En qué casilla quieres colocar la ficha? (número)")
                print("Las casillas disponibles son:")
                self.mostrar_casillas_libres()
                
                try:
                    num_casilla = int(input("Casilla: "))
                    
                    # Buscar la casilla
                    casilla = None
                    for c in self.tablero.casillas:
                        if c.numero == num_casilla:
                            casilla = c
                            break
                    
                    if casilla is None:
                        print("❌ Casilla inválida. La ficha vuelve a tu mano.")
                        self.turno_actual()  # Reintentar
                        return
                    
                    # Intentar colocar
                    if self.tablero.primera_jugada:
                        # Primera jugada: puede ir en cualquier casilla libre
                        if casilla.ficha is not None:
                            print("❌ Esa casilla ya está ocupada. La ficha vuelve a tu mano.")
                            self.turno_actual()
                            return
                        
                        # Verificar orientación
                        if ficha.orientacion != casilla.orientacion:
                            print("❌ La ficha no tiene la orientación correcta para esa casilla.")
                            print("   Puedes girarla con 'g' antes de colocarla.")
                            self.turno_actual()
                            return
                        
                        # Colocar
                        colocada = self.jugar_ficha(ficha, casilla)
                        
                    else:
                        # Jugadas siguientes: solo head o tail
                        # Verificar si es head o tail
                        es_head = casilla.numero == self.tablero.head_posible.casilla.numero
                        es_tail = casilla.numero == self.tablero.tail_posible.casilla.numero
                        
                        if not es_head and not es_tail:
                            print("❌ Esa casilla no es un extremo (head o tail). La ficha vuelve a tu mano.")
                            self.turno_actual()
                            return
                        
                        # Verificar que esté libre
                        if casilla.ficha is not None:
                            print("❌ Esa casilla ya está ocupada. La ficha vuelve a tu mano.")
                            self.turno_actual()
                            return
                        
                        # Verificar orientación
                        if ficha.orientacion != casilla.orientacion:
                            print("❌ La ficha no tiene la orientación correcta para esa casilla.")
                            print("   Puedes girarla con 'g' antes de colocarla.")
                            self.turno_actual()
                            return
                        
                        # Verificar que encaje
                        posible, _ = self.tablero.puede_colocar(ficha, casilla)
                        
                        if not posible:
                            print("❌ La ficha no encaja en ese extremo. La ficha vuelve a tu mano.")
                            self.turno_actual()
                            return
                        
                        # Colocar
                        colocada = self.jugar_ficha(ficha, casilla)
                    
                    # Si se colocó correctamente, el turno ya cambió dentro de jugar_ficha
                    if colocada:
                        print(f"✅ {jugador.nombre} colocó la ficha correctamente.")
                        
                        # Verificar si ganó
                        if self.jugador_gano():
                            self.terminada = True
                            self.ganador = jugador
                            return
                    else:
                        print("❌ Error al colocar la ficha. La ficha vuelve a tu mano.")
                        self.turno_actual()
                        
                except ValueError:
                    print("❌ Entrada inválida. La ficha vuelve a tu mano.")
                    self.turno_actual()
                    
            else:
                print("❌ Número de ficha inválido. La ficha vuelve a tu mano.")
                self.turno_actual()
                
        except ValueError:
            print("❌ Entrada inválida.")
            self.turno_actual()


    def mostrar_casillas_libres(self):
        """Muestra las casillas que están libres"""
        libres = [c for c in self.tablero.casillas if c.ficha is None]
        
        if self.tablero.primera_jugada:
            print("  (Primera jugada - cualquier casilla libre sirve)")
        
        for casilla in libres:
            es_head = not self.tablero.primera_jugada and casilla.numero == self.tablero.head_posible.casilla.numero
            es_tail = not self.tablero.primera_jugada and casilla.numero == self.tablero.tail_posible.casilla.numero
            
            etiqueta = ""
            if es_head:
                etiqueta = " [HEAD]"
            elif es_tail:
                etiqueta = " [TAIL]"
            
            print(f"  Casilla {casilla.numero} ({casilla.orientacion}){etiqueta}")