# pygame_app.py

import pygame
import sys
import os
from partida import Partida
from config import LARGO_FICHA, ANCHO_FICHA, MARGEN_TABLERO

# Constantes de pantalla
ANCHO_PANTALLA = 1400
ALTO_PANTALLA = 900
COLOR_FONDO = (40, 40, 40)
COLOR_BOTON = (70, 70, 70)
COLOR_BOTON_HOVER = (100, 100, 100)
COLOR_TEXTO_BOTON = (255, 255, 255)
COLOR_CASILLA_VACIA = (80, 80, 80)
COLOR_CASILLA_DESTACADA = (50, 200, 50)


class Boton:
    def __init__(self, x, y, ancho, alto, texto, color=COLOR_BOTON, color_hover=COLOR_BOTON_HOVER):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.color = color
        self.color_hover = color_hover
        self.activo = True
        self.fuente = pygame.font.Font(None, 28)
    
    def dibujar(self, pantalla):
        color = self.color_hover if self.esta_sobre() and self.activo else self.color
        pygame.draw.rect(pantalla, color, self.rect, border_radius=8)
        pygame.draw.rect(pantalla, (150, 150, 150), self.rect, 2, border_radius=8)
        
        if self.activo:
            texto = self.fuente.render(self.texto, True, COLOR_TEXTO_BOTON)
        else:
            texto = self.fuente.render(self.texto, True, (100, 100, 100))
        pantalla.blit(texto, (self.rect.x + 10, self.rect.y + 8))
    
    def esta_sobre(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())
    
    def click(self):
        return self.activo and self.esta_sobre()


class JuegoPygame:
    def __init__(self):
        pygame.init()
        
        # Configurar pantalla
        self.pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
        pygame.display.set_caption("Dominó de Fracciones")
        self.clock = pygame.time.Clock()
        self.fuente = pygame.font.Font(None, 24)
        self.fuente_grande = pygame.font.Font(None, 36)
        self.fuente_fraccion = pygame.font.Font(None, 20)
        
        # Cargar imágenes
        self.cargar_imagenes()
        
        # Crear partida (con 4 fichas por jugador para pruebas rápidas)
        self.partida = Partida("fichas_prueba.csv", fichas_por_jugador=4)
        
        # Calcular offset para centrar el tablero
        self.calcular_offset_tablero()
        
        # Estado del juego
        self.ficha_seleccionada = None
        self.ficha_arrastrada = None
        self.ficha_robada_actual = None
        self.offset_x = 0
        self.offset_y = 0
        self.casillas_destacadas = []
        self.mensaje = ""
        self.tiempo_mensaje = 0
        
        # Posiciones de las fichas
        self.actualizar_posiciones_fichas()
        
        # Crear botones
        self.crear_botones()
    
    def cargar_imagenes(self):
        """Carga las imágenes de los assets"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            assets_dir = os.path.join(script_dir, "assets")
            
            ruta_frente = os.path.join(assets_dir, "ficha.png")
            ruta_dorso = os.path.join(assets_dir, "dorso.png")
            
            self.img_frente = pygame.image.load(ruta_frente)
            self.img_dorso = pygame.image.load(ruta_dorso)
            
            self.img_frente = pygame.transform.scale(self.img_frente, (LARGO_FICHA, ANCHO_FICHA))
            self.img_dorso = pygame.transform.scale(self.img_dorso, (LARGO_FICHA, ANCHO_FICHA))
            
            print("✅ Imágenes cargadas correctamente")
        except Exception as e:
            print(f"⚠️ Error cargando imágenes: {e}")
            self.img_frente = None
            self.img_dorso = None
    
    def calcular_offset_tablero(self):
        """Calcula el offset para centrar el tablero en la pantalla"""
        min_x = float('inf')
        max_x = float('-inf')
        min_y = float('inf')
        max_y = float('-inf')
        
        for casilla in self.partida.tablero.casillas:
            if casilla.x < min_x:
                min_x = casilla.x
            if casilla.x > max_x:
                max_x = casilla.x
            if casilla.y < min_y:
                min_y = casilla.y
            if casilla.y > max_y:
                max_y = casilla.y
        
        max_x += LARGO_FICHA
        max_y += LARGO_FICHA
        
        centro_tablero_x = (min_x + max_x) // 2
        centro_tablero_y = (min_y + max_y) // 2
        
        self.offset_tablero_x = ANCHO_PANTALLA // 2 - centro_tablero_x
        self.offset_tablero_y = ALTO_PANTALLA // 2 - centro_tablero_y
    
    def crear_botones(self):
        """Crea los botones de la interfaz"""
        self.botones = []
        
        self.boton_robar = Boton(20, ALTO_PANTALLA - 70, 150, 40, "📥 Robar del pozo")
        self.botones.append(self.boton_robar)
        
        self.boton_pasar = Boton(190, ALTO_PANTALLA - 70, 150, 40, "⏭️ Pasar turno")
        self.botones.append(self.boton_pasar)
        
        self.boton_girar = Boton(360, ALTO_PANTALLA - 70, 130, 40, "🔄 Girar")
        self.botones.append(self.boton_girar)
    
    def actualizar_botones(self):
        """Actualiza qué botones están activos según el estado del juego"""
        partida = self.partida
        jugador = partida.jugador_actual()
        ya_robo = partida.ya_robo_en_turno
        puede_robar = partida.puede_robar(jugador)
        
        self.boton_robar.activo = not ya_robo and puede_robar and not partida.terminada
        self.boton_pasar.activo = ya_robo and not partida.terminada
        self.boton_girar.activo = self.ficha_seleccionada is not None and not partida.terminada
    
    def actualizar_posiciones_fichas(self):
        """Actualiza las posiciones de las fichas de cada jugador en la pantalla"""
        self.posiciones_fichas = {
            "jugador1": [],
            "jugador2": []
        }
        
        # Jugador 1: lateral izquierdo
        x = 30
        y = 150
        max_por_columna = 15
        ancho_ficha = LARGO_FICHA
        alto_ficha = ANCHO_FICHA
        separacion = 10
        
        for i, ficha in enumerate(self.partida.jugadores[0].fichas):
            if ficha == self.ficha_arrastrada:
                continue
            
            fila = i % max_por_columna
            columna = i // max_por_columna
            
            self.posiciones_fichas["jugador1"].append({
                "ficha": ficha,
                "x": x + columna * (ancho_ficha + separacion + 20),
                "y": y + fila * (alto_ficha + separacion),
                "ancho": ancho_ficha,
                "alto": alto_ficha
            })
        
        # Jugador 2: lateral derecho
        x = ANCHO_PANTALLA - 30 - LARGO_FICHA
        y = 150
        
        for i, ficha in enumerate(self.partida.jugadores[1].fichas):
            if ficha == self.ficha_arrastrada:
                continue
            
            fila = i % max_por_columna
            columna = i // max_por_columna
            
            self.posiciones_fichas["jugador2"].append({
                "ficha": ficha,
                "x": x - columna * (ancho_ficha + separacion + 20),
                "y": y + fila * (alto_ficha + separacion),
                "ancho": ancho_ficha,
                "alto": alto_ficha
            })
    
    def dibujar_valores_ficha(self, ficha, x, y, ancho, alto):
        """Dibuja los valores de la ficha encima de la imagen de fondo"""
        s = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        s.fill((255, 255, 255, 180))
        self.pantalla.blit(s, (x, y))
        
        if ficha.orientacion == "horizontal":
            pygame.draw.line(self.pantalla, (80, 80, 80), 
                           (x + ancho//2, y + 5), 
                           (x + ancho//2, y + alto - 5), 2)
        else:
            pygame.draw.line(self.pantalla, (80, 80, 80), 
                           (x + 5, y + alto//2), 
                           (x + ancho - 5, y + alto//2), 2)
        
        if ficha.orientacion == "horizontal":
            texto1 = self.fuente_fraccion.render(ficha.textos["O"].replace("/", "|"), True, (0, 0, 0))
            texto2 = self.fuente_fraccion.render(ficha.textos["E"].replace("/", "|"), True, (0, 0, 0))
            self.pantalla.blit(texto1, (x + 10, y + alto//2 - 10))
            self.pantalla.blit(texto2, (x + ancho - 30, y + alto//2 - 10))
        else:
            texto1 = self.fuente_fraccion.render(ficha.textos["N"].replace("/", "|"), True, (0, 0, 0))
            texto2 = self.fuente_fraccion.render(ficha.textos["S"].replace("/", "|"), True, (0, 0, 0))
            self.pantalla.blit(texto1, (x + ancho//2 - 10, y + 10))
            self.pantalla.blit(texto2, (x + ancho//2 - 10, y + alto - 30))
    
    def dibujar_ficha(self, ficha, x, y, ancho, alto, seleccionada=False, resaltada=False, arrastrada=False, dorso=False):
        """Dibuja una ficha en la pantalla"""
        if dorso and self.img_dorso is not None:
            img = pygame.transform.scale(self.img_dorso, (ancho, alto))
            self.pantalla.blit(img, (x, y))
            return
        
        if self.img_frente is not None and not dorso:
            img = pygame.transform.scale(self.img_frente, (ancho, alto))
            self.pantalla.blit(img, (x, y))
            
            if seleccionada or arrastrada:
                color = (100, 200, 255) if seleccionada else (200, 255, 200)
                pygame.draw.rect(self.pantalla, color, (x, y, ancho, alto), 4, border_radius=5)
            
            if resaltada:
                pygame.draw.rect(self.pantalla, (50, 255, 50), (x, y, ancho, alto), 4, border_radius=5)
            
            self.dibujar_valores_ficha(ficha, x, y, ancho, alto)
            return
        
        # Fallback: dibujar rectángulo
        color = (200, 200, 255) if seleccionada else (200, 200, 100) if arrastrada else (240, 240, 240)
        pygame.draw.rect(self.pantalla, color, (x, y, ancho, alto), border_radius=5)
        pygame.draw.rect(self.pantalla, (100, 100, 100), (x, y, ancho, alto), 2, border_radius=5)
        
        if ficha.orientacion == "horizontal":
            pygame.draw.line(self.pantalla, (100, 100, 100), 
                           (x + ancho//2, y + 5), 
                           (x + ancho//2, y + alto - 5), 2)
        else:
            pygame.draw.line(self.pantalla, (100, 100, 100), 
                           (x + 5, y + alto//2), 
                           (x + ancho - 5, y + alto//2), 2)
        
        if ficha.orientacion == "horizontal":
            texto1 = self.fuente_fraccion.render(ficha.textos["O"].replace("/", "|"), True, (0, 0, 0))
            texto2 = self.fuente_fraccion.render(ficha.textos["E"].replace("/", "|"), True, (0, 0, 0))
            self.pantalla.blit(texto1, (x + 10, y + alto//2 - 10))
            self.pantalla.blit(texto2, (x + ancho - 30, y + alto//2 - 10))
        else:
            texto1 = self.fuente_fraccion.render(ficha.textos["N"].replace("/", "|"), True, (0, 0, 0))
            texto2 = self.fuente_fraccion.render(ficha.textos["S"].replace("/", "|"), True, (0, 0, 0))
            self.pantalla.blit(texto1, (x + ancho//2 - 10, y + 10))
            self.pantalla.blit(texto2, (x + ancho//2 - 10, y + alto - 30))
    
    def dibujar_pozo(self):
        """Dibuja las fichas del pozo boca abajo en el centro del tablero"""
        fichas_pozo = self.partida.pozo.fichas
        if not fichas_pozo:
            return
        
        centro_x = ANCHO_PANTALLA // 2
        centro_y = ALTO_PANTALLA // 2
        
        por_fila = 6
        separacion = 3
        ancho = ANCHO_FICHA
        alto = LARGO_FICHA
        
        total_ancho = por_fila * (ancho + separacion)
        total_alto = (len(fichas_pozo) // por_fila + 1) * (alto + separacion)
        
        inicio_x = centro_x - total_ancho // 2
        inicio_y = centro_y - total_alto // 2
        
        max_mostrar = 30
        for i, ficha in enumerate(fichas_pozo[:max_mostrar]):
            fila = i // por_fila
            columna = i % por_fila
            
            x = inicio_x + columna * (ancho + separacion)
            y = inicio_y + fila * (alto + separacion)
            
            self.dibujar_ficha(ficha, x, y, ancho, alto, dorso=True)
        
        texto = self.fuente.render(f"Pozo: {len(fichas_pozo)} fichas", True, (200, 200, 200))
        self.pantalla.blit(texto, (centro_x - 60, inicio_y - 30))
    
    def dibujar_tablero(self):
        """Dibuja el tablero centrado en la pantalla"""
        for casilla in self.partida.tablero.casillas:
            x = casilla.x + self.offset_tablero_x
            y = casilla.y + self.offset_tablero_y
            
            if casilla.ficha is not None:
                if casilla.orientacion == "horizontal":
                    ancho = LARGO_FICHA
                    alto = ANCHO_FICHA
                else:
                    ancho = ANCHO_FICHA
                    alto = LARGO_FICHA
                
                destacada = casilla in self.casillas_destacadas
                
                self.dibujar_ficha(
                    casilla.ficha,
                    x, y,
                    ancho, alto,
                    resaltada=destacada,
                    dorso=False
                )
            else:
                if casilla.orientacion == "horizontal":
                    ancho = LARGO_FICHA
                    alto = ANCHO_FICHA
                else:
                    ancho = ANCHO_FICHA
                    alto = LARGO_FICHA
                
                color = COLOR_CASILLA_DESTACADA if casilla in self.casillas_destacadas else (50, 50, 50)
                pygame.draw.rect(self.pantalla, color, (x, y, ancho, alto), 1)
    
    def obtener_ficha_en_posicion(self, x, y):
        """Devuelve la ficha y el jugador que está en la posición (x, y)"""
        partida = self.partida
        jugador_actual = partida.jugador_actual()
        
        if partida.ya_robo_en_turno and self.ficha_robada_actual is not None:
            for pos in self.posiciones_fichas["jugador1"] + self.posiciones_fichas["jugador2"]:
                if pos["ficha"] == self.ficha_robada_actual:
                    if (pos["x"] <= x <= pos["x"] + pos["ancho"] and
                        pos["y"] <= y <= pos["y"] + pos["alto"]):
                        return self.ficha_robada_actual, jugador_actual
            return None, None
        
        for pos in self.posiciones_fichas["jugador1"]:
            if (pos["x"] <= x <= pos["x"] + pos["ancho"] and
                pos["y"] <= y <= pos["y"] + pos["alto"]):
                return pos["ficha"], self.partida.jugadores[0]
        
        for pos in self.posiciones_fichas["jugador2"]:
            if (pos["x"] <= x <= pos["x"] + pos["ancho"] and
                pos["y"] <= y <= pos["y"] + pos["alto"]):
                return pos["ficha"], self.partida.jugadores[1]
        
        return None, None
    
    def obtener_casilla_en_posicion(self, x, y):
        """Devuelve la casilla que está en la posición (x, y)"""
        x_ajustada = x - self.offset_tablero_x
        y_ajustada = y - self.offset_tablero_y
        
        for casilla in self.partida.tablero.casillas:
            casilla_x = casilla.x
            casilla_y = casilla.y
            
            if casilla.orientacion == "horizontal":
                ancho = LARGO_FICHA
                alto = ANCHO_FICHA
            else:
                ancho = ANCHO_FICHA
                alto = LARGO_FICHA
            
            if (casilla_x <= x_ajustada <= casilla_x + ancho and
                casilla_y <= y_ajustada <= casilla_y + alto):
                return casilla
        
        return None
    
    def actualizar_casillas_destacadas(self, ficha, jugador):
        """Actualiza qué casillas se iluminan al pasar una ficha por encima"""
        self.casillas_destacadas = []
        
        if ficha is None:
            return
        
        x, y = pygame.mouse.get_pos()
        casilla_bajo_mouse = self.obtener_casilla_en_posicion(x, y)
        
        if casilla_bajo_mouse is None:
            return
        
        if jugador == self.partida.jugador_actual():
            if self.partida.tablero.primera_jugada:
                if (casilla_bajo_mouse.ficha is None and 
                    casilla_bajo_mouse.orientacion == ficha.orientacion):
                    self.casillas_destacadas.append(casilla_bajo_mouse)
            else:
                head = self.partida.tablero.head_posible.casilla
                tail = self.partida.tablero.tail_posible.casilla
                
                if casilla_bajo_mouse.numero == head.numero:
                    if head.ficha is None and head.orientacion == ficha.orientacion:
                        self.casillas_destacadas.append(head)
                elif casilla_bajo_mouse.numero == tail.numero:
                    if tail.ficha is None and tail.orientacion == ficha.orientacion:
                        self.casillas_destacadas.append(tail)
    
    def mostrar_mensaje(self, texto, tipo="info"):
        """Muestra un mensaje en la pantalla"""
        self.mensaje = texto
        self.tiempo_mensaje = pygame.time.get_ticks()
    
    def verificar_y_mostrar_fin_partida(self):
        """Verifica si la partida terminó y muestra el mensaje correspondiente"""
        if self.partida.terminada:
            if self.partida.ganador:
                self.mostrar_mensaje(f"🎉 ¡{self.partida.ganador.nombre} GANÓ!", "success")
            else:
                self.mostrar_mensaje("🤝 EMPATE", "warning")
            self.actualizar_botones()
            return True
        
        # Si no está terminada, verificar
        self.partida.verificar_fin_partida()
        if self.partida.terminada:
            if self.partida.ganador:
                self.mostrar_mensaje(f"🎉 ¡{self.partida.ganador.nombre} GANÓ!", "success")
            else:
                self.mostrar_mensaje("🤝 EMPATE", "warning")
            self.actualizar_botones()
            return True
        
        return False
    
    def ejecutar(self):
        """Bucle principal del juego"""
        ejecutando = True
        
        while ejecutando:
            # Manejar eventos
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    ejecutando = False
                
                elif evento.type == pygame.MOUSEBUTTONDOWN:
                    if evento.button == 1:
                        x, y = evento.pos
                        
                        # Verificar clic en botones
                        for boton in self.botones:
                            if boton.click():
                                if boton == self.boton_robar:
                                    if not self.partida.ya_robo_en_turno and not self.partida.terminada:
                                        ficha = self.partida.robar_ficha()
                                        if ficha:
                                            self.ficha_robada_actual = ficha
                                            self.ficha_seleccionada = ficha
                                            self.mostrar_mensaje(f"📥 {self.partida.jugador_actual().nombre} robó: {ficha.mostrar_valores()}")
                                            self.actualizar_posiciones_fichas()
                                            self.actualizar_botones()
                                            #self.verificar_y_mostrar_fin_partida()
                                        else:
                                            self.mostrar_mensaje("❌ No hay fichas en el pozo")
                                    continue
                                
                                elif boton == self.boton_pasar:
                                    if self.partida.ya_robo_en_turno and not self.partida.terminada:
                                        self.partida.pasar_turno()
                                        self.mostrar_mensaje(f"⏭️ {self.partida.jugador_actual().nombre} pasa turno")
                                        self.ficha_seleccionada = None
                                        self.ficha_arrastrada = None
                                        self.ficha_robada_actual = None
                                        self.casillas_destacadas = []
                                        self.actualizar_posiciones_fichas()
                                        self.actualizar_botones()
                                        self.verificar_y_mostrar_fin_partida()
                                    continue
                                
                                elif boton == self.boton_girar:
                                    if self.ficha_seleccionada is not None and not self.partida.terminada:
                                        self.ficha_seleccionada.girar_90()
                                        self.mostrar_mensaje(f"🔄 Ficha girada: {self.ficha_seleccionada.mostrar_valores()}")
                                        self.actualizar_posiciones_fichas()
                                    continue
                        
                        # ============================================
                        # SELECCIONAR FICHA CON CLICK
                        # ============================================
                        ficha, jugador = self.obtener_ficha_en_posicion(x, y)
                        
                        if ficha is not None and jugador == self.partida.jugador_actual() and not self.partida.terminada:
                            self.ficha_seleccionada = ficha
                            self.ficha_arrastrada = ficha
                            
                            for pos in self.posiciones_fichas["jugador1"] + self.posiciones_fichas["jugador2"]:
                                if pos["ficha"] == ficha:
                                    self.offset_x = x - pos["x"]
                                    self.offset_y = y - pos["y"]
                                    break
                            
                            self.mostrar_mensaje(f"📌 Seleccionada: {ficha.mostrar_valores()}")
                            self.actualizar_botones()
                
                elif evento.type == pygame.MOUSEBUTTONUP:
                    if evento.button == 1 and self.ficha_arrastrada is not None and not self.partida.terminada:
                        x, y = evento.pos
                        casilla = self.obtener_casilla_en_posicion(x, y)
                        
                        if casilla and casilla.ficha is None:
                            if self.partida.tablero.primera_jugada:
                                if self.ficha_arrastrada.orientacion == casilla.orientacion:
                                    exito = self.partida.jugar_ficha(self.ficha_arrastrada, casilla)
                                    if exito:
                                        self.mostrar_mensaje(f"✅ {self.partida.jugador_actual().nombre} colocó {self.ficha_arrastrada.mostrar_valores()}")
                                        self.ficha_robada_actual = None
                                        self.actualizar_posiciones_fichas()
                                        self.actualizar_botones()
                                        self.verificar_y_mostrar_fin_partida()
                                    else:
                                        self.mostrar_mensaje("❌ No se pudo colocar la ficha")
                                else:
                                    self.mostrar_mensaje(f"❌ La ficha es {self.ficha_arrastrada.orientacion} pero la casilla es {casilla.orientacion}")
                            else:
                                head = self.partida.tablero.head_posible.casilla
                                tail = self.partida.tablero.tail_posible.casilla
                                
                                if casilla.numero == head.numero or casilla.numero == tail.numero:
                                    posible, _ = self.partida.tablero.puede_colocar(self.ficha_arrastrada, casilla)
                                    if posible:
                                        exito = self.partida.jugar_ficha(self.ficha_arrastrada, casilla)
                                        if exito:
                                            self.mostrar_mensaje(f"✅ {self.partida.jugador_actual().nombre} colocó {self.ficha_arrastrada.mostrar_valores()}")
                                            self.ficha_robada_actual = None
                                            self.actualizar_posiciones_fichas()
                                            self.actualizar_botones()
                                            self.verificar_y_mostrar_fin_partida()
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
                        
                        self.ficha_arrastrada = None
                        self.ficha_seleccionada = None
                        self.casillas_destacadas = []
                        self.actualizar_posiciones_fichas()
                        self.actualizar_botones()
                
                elif evento.type == pygame.MOUSEMOTION:
                    if self.ficha_arrastrada is not None and not self.partida.terminada:
                        self.actualizar_casillas_destacadas(
                            self.ficha_arrastrada, 
                            self.partida.jugador_actual()
                        )
                
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_g:
                        if self.ficha_seleccionada is not None and not self.partida.terminada:
                            self.ficha_seleccionada.girar_90()
                            self.mostrar_mensaje(f"🔄 Ficha girada: {self.ficha_seleccionada.mostrar_valores()}")
                            self.actualizar_posiciones_fichas()
                            self.actualizar_botones()
                    elif evento.key == pygame.K_ESCAPE:
                        self.ficha_seleccionada = None
                        self.ficha_arrastrada = None
                        self.ficha_robada_actual = None
                        self.casillas_destacadas = []
                        self.actualizar_posiciones_fichas()
                        self.actualizar_botones()
                        self.mostrar_mensaje("❌ Selección cancelada")
            
            # ============================================
            # NO HAY VERIFICACIÓN DE FIN DE PARTIDA AQUÍ
            # (solo se verifica después de acciones)
            # ============================================
            
            # Dibujar
            self.pantalla.fill(COLOR_FONDO)
            
            texto_turno = self.fuente_grande.render(
                f"Turno: {self.partida.jugador_actual().nombre}" if not self.partida.terminada else "PARTIDA TERMINADA",
                True, (255, 255, 255)
            )
            self.pantalla.blit(texto_turno, (ANCHO_PANTALLA//2 - 100, 20))
            
            if self.mensaje:
                texto_msg = self.fuente.render(self.mensaje, True, (255, 255, 255))
                self.pantalla.blit(texto_msg, (ANCHO_PANTALLA//2 - 200, 70))
            
            self.dibujar_pozo()
            self.dibujar_tablero()
            
            for jugador_id, posiciones in self.posiciones_fichas.items():
                for pos in posiciones:
                    es_seleccionada = pos["ficha"] == self.ficha_seleccionada and pos["ficha"] != self.ficha_arrastrada
                    self.dibujar_ficha(
                        pos["ficha"],
                        pos["x"], pos["y"],
                        pos["ancho"], pos["alto"],
                        seleccionada=es_seleccionada
                    )
            
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
            
            for boton in self.botones:
                boton.dibujar(self.pantalla)
            
            texto_ayuda = self.fuente.render("G: Girar ficha | ESC: Cancelar | Arrastrar para colocar", True, (150, 150, 150))
            self.pantalla.blit(texto_ayuda, (20, ALTO_PANTALLA - 30))
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    juego = JuegoPygame()
    juego.ejecutar()