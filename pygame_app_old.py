# pygame_app.py

import pygame
import sys
from partida import Partida
from config import LARGO_FICHA, ANCHO_FICHA, MARGEN_TABLERO

# Constantes de pantalla
ANCHO_PANTALLA = 1200
ALTO_PANTALLA = 800
COLOR_FONDO = (40, 40, 40)
COLOR_FICHA = (240, 240, 240)
COLOR_TEXTO = (0, 0, 0)
COLOR_BORDE = (100, 100, 100)
COLOR_DESTACADO = (255, 200, 50)
COLOR_CASILLA_VACIA = (80, 80, 80)
COLOR_CASILLA_DESTACADA = (50, 200, 50)
COLOR_SELECCION = (100, 200, 255)
COLOR_ARRASTRE = (200, 255, 200)

class JuegoPygame:
    def __init__(self):
        pygame.init()
        
        # Configurar pantalla
        self.pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
        pygame.display.set_caption("Dominó de Fracciones")
        self.clock = pygame.time.Clock()
        self.fuente = pygame.font.Font(None, 24)
        self.fuente_grande = pygame.font.Font(None, 36)
        
        # Crear partida
        self.partida = Partida("fichas.csv")
        
        # Estado del juego
        self.ficha_seleccionada = None
        self.ficha_arrastrada = None
        self.offset_x = 0
        self.offset_y = 0
        self.casillas_destacadas = []
        self.mensaje = ""
        self.tiempo_mensaje = 0
        
        # Posiciones de las fichas de los jugadores
        self.actualizar_posiciones_fichas()
    
    def actualizar_posiciones_fichas(self):
        """Actualiza las posiciones de las fichas de cada jugador en la pantalla"""
        self.posiciones_fichas = {
            "jugador1": [],
            "jugador2": []
        }
        
        # Jugador 1: lateral izquierdo
        x = 30
        y = 150
        for i, ficha in enumerate(self.partida.jugadores[0].fichas):
            # Si la ficha es la que está siendo arrastrada, no la dibujamos en su posición original
            if ficha == self.ficha_arrastrada:
                continue
            self.posiciones_fichas["jugador1"].append({
                "ficha": ficha,
                "x": x,
                "y": y + i * (ANCHO_FICHA + 15),
                "ancho": LARGO_FICHA,
                "alto": ANCHO_FICHA
            })
        
        # Jugador 2: lateral derecho
        x = ANCHO_PANTALLA - 30 - LARGO_FICHA
        y = 150
        for i, ficha in enumerate(self.partida.jugadores[1].fichas):
            if ficha == self.ficha_arrastrada:
                continue
            self.posiciones_fichas["jugador2"].append({
                "ficha": ficha,
                "x": x,
                "y": y + i * (ANCHO_FICHA + 15),
                "ancho": LARGO_FICHA,
                "alto": ANCHO_FICHA
            })
    
    def dibujar_ficha(self, ficha, x, y, ancho, alto, seleccionada=False, resaltada=False, arrastrada=False):
        """Dibuja una ficha en la pantalla"""
        # Color de fondo
        if arrastrada:
            color = COLOR_ARRASTRE
        elif seleccionada:
            color = COLOR_SELECCION
        elif resaltada:
            color = COLOR_CASILLA_DESTACADA
        else:
            color = COLOR_FICHA
        
        # Dibujar rectángulo
        pygame.draw.rect(self.pantalla, color, (x, y, ancho, alto), border_radius=5)
        pygame.draw.rect(self.pantalla, COLOR_BORDE, (x, y, ancho, alto), 2, border_radius=5)
        
        # Dibujar línea central
        if ficha.orientacion == "horizontal":
            pygame.draw.line(self.pantalla, COLOR_BORDE, 
                           (x + ancho//2, y + 5), 
                           (x + ancho//2, y + alto - 5), 2)
        else:
            pygame.draw.line(self.pantalla, COLOR_BORDE, 
                           (x + 5, y + alto//2), 
                           (x + ancho - 5, y + alto//2), 2)
        
        # Mostrar valores
        if ficha.orientacion == "horizontal":
            texto1 = self.fuente.render(ficha.textos["O"], True, COLOR_TEXTO)
            texto2 = self.fuente.render(ficha.textos["E"], True, COLOR_TEXTO)
            self.pantalla.blit(texto1, (x + 10, y + alto//2 - 10))
            self.pantalla.blit(texto2, (x + ancho - 30, y + alto//2 - 10))
        else:
            texto1 = self.fuente.render(ficha.textos["N"], True, COLOR_TEXTO)
            texto2 = self.fuente.render(ficha.textos["S"], True, COLOR_TEXTO)
            self.pantalla.blit(texto1, (x + ancho//2 - 10, y + 10))
            self.pantalla.blit(texto2, (x + ancho//2 - 10, y + alto - 30))
    
    def dibujar_tablero(self):
        """Dibuja el tablero con las fichas colocadas"""
        for casilla in self.partida.tablero.casillas:
            if casilla.ficha is not None:
                # Obtener posición de la casilla en pantalla
                x = casilla.x + MARGEN_TABLERO
                y = casilla.y + MARGEN_TABLERO
                
                # Determinar dimensiones
                if casilla.orientacion == "horizontal":
                    ancho = LARGO_FICHA
                    alto = ANCHO_FICHA
                else:
                    ancho = ANCHO_FICHA
                    alto = LARGO_FICHA
                
                # Determinar si la casilla está destacada
                destacada = casilla in self.casillas_destacadas
                
                self.dibujar_ficha(
                    casilla.ficha,
                    x, y,
                    ancho, alto,
                    resaltada=destacada
                )
            else:
                # Dibujar casilla vacía (solo para referencia)
                x = casilla.x + MARGEN_TABLERO
                y = casilla.y + MARGEN_TABLERO
                if casilla.orientacion == "horizontal":
                    ancho = LARGO_FICHA
                    alto = ANCHO_FICHA
                else:
                    ancho = ANCHO_FICHA
                    alto = LARGO_FICHA
                
                color = COLOR_CASILLA_DESTACADA if casilla in self.casillas_destacadas else COLOR_CASILLA_VACIA
                pygame.draw.rect(self.pantalla, color, (x, y, ancho, alto), 1)
    
    def obtener_ficha_en_posicion(self, x, y):
        """Devuelve la ficha y el jugador que está en la posición (x, y)"""
        # Verificar fichas del jugador 1
        for pos in self.posiciones_fichas["jugador1"]:
            if (pos["x"] <= x <= pos["x"] + pos["ancho"] and
                pos["y"] <= y <= pos["y"] + pos["alto"]):
                return pos["ficha"], self.partida.jugadores[0]
        
        # Verificar fichas del jugador 2
        for pos in self.posiciones_fichas["jugador2"]:
            if (pos["x"] <= x <= pos["x"] + pos["ancho"] and
                pos["y"] <= y <= pos["y"] + pos["alto"]):
                return pos["ficha"], self.partida.jugadores[1]
        
        return None, None
    
    def obtener_casilla_en_posicion(self, x, y):
        """Devuelve la casilla que está en la posición (x, y)"""
        for casilla in self.partida.tablero.casillas:
            casilla_x = casilla.x + MARGEN_TABLERO
            casilla_y = casilla.y + MARGEN_TABLERO
            
            if casilla.orientacion == "horizontal":
                ancho = LARGO_FICHA
                alto = ANCHO_FICHA
            else:
                ancho = ANCHO_FICHA
                alto = LARGO_FICHA
            
            if (casilla_x <= x <= casilla_x + ancho and
                casilla_y <= y <= casilla_y + alto):
                return casilla
        
        return None
    
    def actualizar_casillas_destacadas(self, ficha, jugador):
        """
        Actualiza qué casillas se iluminan al pasar una ficha por encima.
        Solo considera: orientación de la casilla y que esté libre.
        NO valida los valores (eso se hace al soltar).
        """
        self.casillas_destacadas = []
        
        if ficha is None:
            return
        
        # Si es el turno del jugador
        if jugador == self.partida.jugador_actual():
            # Primera jugada: cualquier casilla libre con la orientación correcta
            if self.partida.tablero.primera_jugada:
                for casilla in self.partida.tablero.casillas:
                    if casilla.ficha is None and casilla.orientacion == ficha.orientacion:
                        self.casillas_destacadas.append(casilla)
            else:
                # Solo HEAD y TAIL, con la orientación correcta
                head = self.partida.tablero.head_posible.casilla
                tail = self.partida.tablero.tail_posible.casilla
                
                # HEAD: si está libre y la orientación coincide
                if head.ficha is None and head.orientacion == ficha.orientacion:
                    self.casillas_destacadas.append(head)
                
                # TAIL: si está libre y la orientación coincide
                if tail.ficha is None and tail.orientacion == ficha.orientacion:
                    self.casillas_destacadas.append(tail)
    
    def mostrar_mensaje(self, texto, tipo="info"):
        """Muestra un mensaje en la pantalla"""
        self.mensaje = texto
        self.tiempo_mensaje = pygame.time.get_ticks()
    
    def ejecutar(self):
        """Bucle principal del juego"""
        ejecutando = True
        
        while ejecutando:
            # Manejar eventos
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    ejecutando = False
                
                elif evento.type == pygame.MOUSEBUTTONDOWN:
                    if evento.button == 1:  # Click izquierdo
                        x, y = evento.pos
                        
                        # Verificar si se hizo clic en una ficha del jugador actual
                        ficha, jugador = self.obtener_ficha_en_posicion(x, y)
                        
                        if ficha is not None and jugador == self.partida.jugador_actual():
                            # Seleccionar la ficha
                            self.ficha_seleccionada = ficha
                            self.ficha_arrastrada = ficha
                            
                            # Calcular offset para el arrastre
                            # Buscar la posición de la ficha
                            for pos in self.posiciones_fichas["jugador1"] + self.posiciones_fichas["jugador2"]:
                                if pos["ficha"] == ficha:
                                    self.offset_x = x - pos["x"]
                                    self.offset_y = y - pos["y"]
                                    break
                            
                            # Actualizar casillas destacadas
                            self.actualizar_casillas_destacadas(ficha, jugador)
                            self.mostrar_mensaje(f"📌 Seleccionada: {ficha.mostrar_valores()}")
                
                #
                elif evento.type == pygame.MOUSEBUTTONUP:
                    if evento.button == 1 and self.ficha_arrastrada is not None:
                        x, y = evento.pos
                        
                        # Verificar si se soltó sobre una casilla
                        casilla = self.obtener_casilla_en_posicion(x, y)
                        
                        if casilla and casilla.ficha is None:
                            # VERIFICAR si es una jugada válida (solo al soltar)
                            if self.partida.tablero.primera_jugada:
                                # Primera jugada: solo validar orientación
                                if self.ficha_arrastrada.orientacion == casilla.orientacion:
                                    exito = self.partida.jugar_ficha(self.ficha_arrastrada, casilla)
                                    if exito:
                                        self.mostrar_mensaje(f"✅ {self.partida.jugador_actual().nombre} colocó {self.ficha_arrastrada.mostrar_valores()}")
                                        self.actualizar_posiciones_fichas()
                                    else:
                                        self.mostrar_mensaje("❌ No se pudo colocar la ficha")
                                else:
                                    self.mostrar_mensaje(f"❌ La ficha es {self.ficha_arrastrada.orientacion} pero la casilla es {casilla.orientacion}")
                            else:
                                # Segunda jugada en adelante: validar HEAD/TAIL
                                head = self.partida.tablero.head_posible.casilla
                                tail = self.partida.tablero.tail_posible.casilla
                                
                                if casilla.numero == head.numero or casilla.numero == tail.numero:
                                    # Es HEAD o TAIL, verificar si encaja
                                    posible, _ = self.partida.tablero.puede_colocar(self.ficha_arrastrada, casilla)
                                    if posible:
                                        exito = self.partida.jugar_ficha(self.ficha_arrastrada, casilla)
                                        if exito:
                                            self.mostrar_mensaje(f"✅ {self.partida.jugador_actual().nombre} colocó {self.ficha_arrastrada.mostrar_valores()}")
                                            self.actualizar_posiciones_fichas()
                                        else:
                                            self.mostrar_mensaje("❌ No se pudo colocar la ficha")
                                    else:
                                        self.mostrar_mensaje("❌ La ficha no encaja en ese extremo")
                                else:
                                    self.mostrar_mensaje("❌ Solo se puede colocar en HEAD o TAIL")
                        else:
                            if casilla and casilla.ficha is not None:
                                self.mostrar_mensaje("❌ Esa casilla ya está ocupada")
                            else:
                                self.mostrar_mensaje("❌ Soltar en una casilla")
                        
                        # Limpiar estado de arrastre
                        self.ficha_arrastrada = None
                        self.ficha_seleccionada = None
                        self.casillas_destacadas = []
                        self.actualizar_posiciones_fichas()
                
                elif evento.type == pygame.MOUSEMOTION:
                    if self.ficha_arrastrada is not None:
                        # Actualizar casillas destacadas mientras se arrastra
                        x, y = evento.pos
                        # Verificar sobre qué casilla está el mouse
                        casilla = self.obtener_casilla_en_posicion(x, y)
                        if casilla:
                            self.actualizar_casillas_destacadas(self.ficha_arrastrada, self.partida.jugador_actual())
                
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_g:
                        # Girar la ficha seleccionada
                        if self.ficha_seleccionada is not None:
                            self.ficha_seleccionada.girar_90()
                            self.mostrar_mensaje(f"🔄 Ficha girada: {self.ficha_seleccionada.mostrar_valores()}")
                            # Actualizar casillas destacadas
                            jugador = self.partida.jugador_actual()
                            self.actualizar_casillas_destacadas(self.ficha_seleccionada, jugador)
                            self.actualizar_posiciones_fichas()
                    elif evento.key == pygame.K_ESCAPE:
                        # Cancelar selección
                        self.ficha_seleccionada = None
                        self.ficha_arrastrada = None
                        self.casillas_destacadas = []
                        self.actualizar_posiciones_fichas()
                        self.mostrar_mensaje("❌ Selección cancelada")
            
            # Dibujar
            self.pantalla.fill(COLOR_FONDO)
            
            # Dibujar información de turno
            texto_turno = self.fuente_grande.render(
                f"Turno: {self.partida.jugador_actual().nombre}", 
                True, (255, 255, 255)
            )
            self.pantalla.blit(texto_turno, (ANCHO_PANTALLA//2 - 100, 20))
            
            # Dibujar mensaje
            if self.mensaje:
                texto_msg = self.fuente.render(self.mensaje, True, (255, 255, 255))
                self.pantalla.blit(texto_msg, (ANCHO_PANTALLA//2 - 200, 70))
            
            # Dibujar tablero
            self.dibujar_tablero()
            
            # Dibujar fichas de los jugadores (excepto la arrastrada)
            for jugador_id, posiciones in self.posiciones_fichas.items():
                for pos in posiciones:
                    es_seleccionada = pos["ficha"] == self.ficha_seleccionada and pos["ficha"] != self.ficha_arrastrada
                    self.dibujar_ficha(
                        pos["ficha"],
                        pos["x"], pos["y"],
                        pos["ancho"], pos["alto"],
                        seleccionada=es_seleccionada
                    )
            
            # Dibujar ficha arrastrada (si existe)
            if self.ficha_arrastrada is not None:
                x, y = pygame.mouse.get_pos()
                self.dibujar_ficha(
                    self.ficha_arrastrada,
                    x - self.offset_x,
                    y - self.offset_y,
                    LARGO_FICHA,
                    ANCHO_FICHA,
                    arrastrada=True
                )
            
            # Dibujar info de teclas
            texto_ayuda = self.fuente.render("G: Girar ficha | ESC: Cancelar | Arrastrar para colocar", True, (150, 150, 150))
            self.pantalla.blit(texto_ayuda, (20, ALTO_PANTALLA - 30))
            
            # Actualizar pantalla
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    juego = JuegoPygame()
    juego.ejecutar()