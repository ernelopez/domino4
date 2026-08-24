# pygame_app.py

import pygame
import sys
import os
from partida import Partida
from config import LARGO_FICHA, ANCHO_FICHA, MARGEN_TABLERO
import asyncio

# Constantes de pantalla (se recalcularán dinámicamente)
COLOR_FONDO = (40, 40, 40)
COLOR_BOTON = (70, 70, 70)
COLOR_BOTON_HOVER = (100, 100, 100)
COLOR_TEXTO_BOTON = (255, 255, 255)
COLOR_CASILLA_VACIA = (255, 182, 193)  # Rosa claro
COLOR_CASILLA_DESTACADA = (50, 200, 50)


class Boton:
    def __init__(self, x, y, ancho, alto, texto, color=COLOR_BOTON, color_hover=COLOR_BOTON_HOVER):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.color = color
        self.color_hover = color_hover
        self.activo = True
        self.fuente = None  # Se asignará después
    
    def dibujar(self, pantalla, fuente):
        color = self.color_hover if self.esta_sobre() and self.activo else self.color
        pygame.draw.rect(pantalla, color, self.rect, border_radius=8)
        pygame.draw.rect(pantalla, (150, 150, 150), self.rect, 2, border_radius=8)
        
        if self.activo:
            texto = fuente.render(self.texto, True, COLOR_TEXTO_BOTON)
        else:
            texto = fuente.render(self.texto, True, (100, 100, 100))
        pantalla.blit(texto, (self.rect.x + 10, self.rect.y + 8))
    
    def esta_sobre(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())
    
    def click(self):
        return self.activo and self.esta_sobre()


class JuegoPygame:
    def __init__(self):
        pygame.init()
        
        # Obtener tamaño de la pantalla
        info = pygame.display.Info()
        self.ancho_pantalla = info.current_w
        self.alto_pantalla = info.current_h
        
        # Crear pantalla completa
        #self.pantalla = pygame.display.set_mode((self.ancho_pantalla, self.alto_pantalla), pygame.FULLSCREEN)
        self.pantalla = pygame.display.set_mode((self.ancho_pantalla, self.alto_pantalla))
        pygame.display.set_caption("Dominó de Fracciones - ESC para salir")
        self.clock = pygame.time.Clock()
        
        # Recalcular tamaños según resolución
        self.recalcular_tamanos()
        
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
        self.ficha_clickeada = None  # <--- NUEVO
        self.pos_click_x = 0         # <--- NUEVO
        self.pos_click_y = 0         # <--- NUEVO
        self.offset_x = 0
        self.offset_y = 0
        self.casillas_destacadas = []
        self.mensaje = ""
        self.tiempo_mensaje = 0
        
        self.mensaje = ""
        self.tiempo_mensaje = 0
        self.mensaje_color = (255, 255, 255)

        # Posiciones de las fichas en la mano
        self.posiciones_fichas = {
            "jugador1": [],
            "jugador2": []
        }
        self.actualizar_posiciones_fichas()
        
        # Crear botones
        self.crear_botones()
    
    def recalcular_tamanos(self):
        """Recalcula todos los tamaños según la resolución actual"""
        BASE_ANCHO = 1200
        BASE_ALTO = 750
        
        self.escala_x = self.ancho_pantalla / BASE_ANCHO
        self.escala_y = self.alto_pantalla / BASE_ALTO
        self.escala = min(self.escala_x, self.escala_y)
        
        self.largo_ficha = int(LARGO_FICHA * self.escala)
        self.ancho_ficha = int(ANCHO_FICHA * self.escala)
        self.margen_tablero = int(MARGEN_TABLERO * self.escala)
        
        self.tamano_fuente = max(12, int(24 * self.escala))
        self.tamano_fuente_grande = max(16, int(36 * self.escala))
        self.tamano_fuente_fraccion = max(10, int(20 * self.escala))
        
        self.fuente = pygame.font.Font(None, self.tamano_fuente)
        self.fuente_grande = pygame.font.Font(None, self.tamano_fuente_grande)
        self.fuente_fraccion = pygame.font.Font(None, self.tamano_fuente_fraccion)
        
        print(f"📐 Escalado: {self.escala:.2f}x")
        print(f"   Ficha: {self.largo_ficha}x{self.ancho_ficha}")
        print(f"   Fuente: {self.tamano_fuente}px")
    
    def cargar_imagenes(self):
        """Carga las imágenes de los assets"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            assets_dir = os.path.join(script_dir, "assets")
            
            ruta_frente = os.path.join(assets_dir, "ficha.png")
            ruta_frente_v = os.path.join(assets_dir, "ficha_vertical.png")
            ruta_dorso = os.path.join(assets_dir, "dorso.png")
            
            self.img_frente = pygame.image.load(ruta_frente)
            self.img_frente_v = pygame.image.load(ruta_frente_v)
            self.img_dorso = pygame.image.load(ruta_dorso)
            
            self.img_frente = pygame.transform.scale(self.img_frente, (self.largo_ficha, self.ancho_ficha))
            self.img_frente_v = pygame.transform.scale(self.img_frente_v, (self.ancho_ficha, self.largo_ficha))
            self.img_dorso = pygame.transform.scale(self.img_dorso, (self.largo_ficha, self.ancho_ficha))
            
            print("✅ Imágenes cargadas correctamente")
        except Exception as e:
            print(f"⚠️ Error cargando imágenes: {e}")
            self.img_frente = None
            self.img_frente_v = None
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
        
        self.offset_tablero_x = self.ancho_pantalla // 2 - int(centro_tablero_x * self.escala)
        self.offset_tablero_y = self.alto_pantalla // 2 - int(centro_tablero_y * self.escala)
    
    def crear_botones(self):
        """Crea los botones de la interfaz"""
        self.botones = []
        
        alto_boton = int(40 * self.escala)
        ancho_boton = int(150 * self.escala)
        separacion = int(20 * self.escala)
        margen = int(20 * self.escala)
        y_boton = self.alto_pantalla - alto_boton - margen
        
        self.boton_robar = Boton(margen, y_boton, ancho_boton, alto_boton, "📥 Robar del pozo")
        self.botones.append(self.boton_robar)
        
        self.boton_pasar = Boton(margen + ancho_boton + separacion, y_boton, ancho_boton, alto_boton, "⏭️ Pasar turno")
        self.botones.append(self.boton_pasar)
        
        self.boton_girar = Boton(margen + 2 * (ancho_boton + separacion), y_boton, ancho_boton, alto_boton, "🔄 Girar")
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
        
        margen = int(30 * self.escala)
        y_inicial = int(80 * self.escala)
        max_por_columna = 20
        separacion = int(8 * self.escala)
        separacion_columnas = int(15 * self.escala)
        
        # ESPACIO FIJO
        espacio_fijo_alto = self.ancho_ficha + separacion
        espacio_fijo_ancho = self.largo_ficha + separacion + separacion_columnas
        
        def calcular_posicion_ficha(ficha, i, x_base, direccion):
            """Calcula la posición de una ficha, centrándola si es vertical"""
            if ficha == self.ficha_arrastrada:
                return None
            
            if ficha.orientacion == "horizontal":
                ancho = self.largo_ficha
                alto = self.ancho_ficha
            else:
                ancho = self.ancho_ficha
                alto = self.largo_ficha
            
            fila = i % max_por_columna
            columna = i // max_por_columna
            
            if direccion == "izquierda":
                x = x_base + columna * espacio_fijo_ancho
            else:
                x = x_base - columna * espacio_fijo_ancho
            
            y = y_inicial + fila * espacio_fijo_alto
            
            # Centrar si es vertical
            if ficha.orientacion == "vertical":
                x = x + (self.largo_ficha - self.ancho_ficha) // 2
            
            return {
                "ficha": ficha,
                "x": x,
                "y": y,
                "ancho": ancho,
                "alto": alto
            }
        
        # Jugador 1
        for i, ficha in enumerate(self.partida.jugadores[0].fichas):
            pos = calcular_posicion_ficha(ficha, i, margen, "izquierda")
            if pos:
                self.posiciones_fichas["jugador1"].append(pos)
        
        # Jugador 2
        x_derecha = self.ancho_pantalla - margen - self.largo_ficha
        for i, ficha in enumerate(self.partida.jugadores[1].fichas):
            pos = calcular_posicion_ficha(ficha, i, x_derecha, "derecha")
            if pos:
                self.posiciones_fichas["jugador2"].append(pos)

    
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
            self.pantalla.blit(texto1, (x + int(10 * self.escala), y + alto//2 - self.tamano_fuente_fraccion//2))
            self.pantalla.blit(texto2, (x + ancho - int(30 * self.escala), y + alto//2 - self.tamano_fuente_fraccion//2))
        else:
            texto1 = self.fuente_fraccion.render(ficha.textos["N"].replace("/", "|"), True, (0, 0, 0))
            texto2 = self.fuente_fraccion.render(ficha.textos["S"].replace("/", "|"), True, (0, 0, 0))
            self.pantalla.blit(texto1, (x + ancho//2 - self.tamano_fuente_fraccion//2, y + int(10 * self.escala)))
            self.pantalla.blit(texto2, (x + ancho//2 - self.tamano_fuente_fraccion//2, y + alto - int(30 * self.escala)))
    
    # ============================================================
    # FUNCIONES DE DIBUJO DE FICHAS SEGÚN CONTEXTO
    # ============================================================
    
    def dibujar_ficha_tablero(self, ficha, x, y, ancho, alto, resaltada=False):
        """
        Dibuja una ficha en el tablero.
        Recibe la posición y el tamaño ya calculados.
        """
        if self.img_frente is not None:
            img = pygame.transform.scale(self.img_frente, (ancho, alto))
            self.pantalla.blit(img, (x, y))
            
            if resaltada:
                pygame.draw.rect(self.pantalla, (50, 255, 50), (x, y, ancho, alto), 
                               max(2, int(4 * self.escala)), border_radius=5)
            
            self.dibujar_valores_ficha(ficha, x, y, ancho, alto)
            return
        
        # Fallback sin imágenes
        color = (240, 240, 240)
        pygame.draw.rect(self.pantalla, color, (x, y, ancho, alto), border_radius=5)
        pygame.draw.rect(self.pantalla, (100, 100, 100), (x, y, ancho, alto), 2, border_radius=5)
        
        if ficha.orientacion == "horizontal":
            pygame.draw.line(self.pantalla, (100, 100, 100), 
                           (x + ancho//2, y + 5), (x + ancho//2, y + alto - 5), 2)
        else:
            pygame.draw.line(self.pantalla, (100, 100, 100), 
                           (x + 5, y + alto//2), (x + ancho - 5, y + alto//2), 2)
        
        if ficha.orientacion == "horizontal":
            texto1 = self.fuente_fraccion.render(ficha.textos["O"].replace("/", "|"), True, (0, 0, 0))
            texto2 = self.fuente_fraccion.render(ficha.textos["E"].replace("/", "|"), True, (0, 0, 0))
            self.pantalla.blit(texto1, (x + int(10 * self.escala), y + alto//2 - self.tamano_fuente_fraccion//2))
            self.pantalla.blit(texto2, (x + ancho - int(30 * self.escala), y + alto//2 - self.tamano_fuente_fraccion//2))
        else:
            texto1 = self.fuente_fraccion.render(ficha.textos["N"].replace("/", "|"), True, (0, 0, 0))
            texto2 = self.fuente_fraccion.render(ficha.textos["S"].replace("/", "|"), True, (0, 0, 0))
            self.pantalla.blit(texto1, (x + ancho//2 - self.tamano_fuente_fraccion//2, y + int(10 * self.escala)))
            self.pantalla.blit(texto2, (x + ancho//2 - self.tamano_fuente_fraccion//2, y + alto - int(30 * self.escala)))
    
    def dibujar_ficha_dorso(self, x, y, ancho, alto):
        """Dibuja una ficha boca abajo (dorso)"""
        if self.img_dorso is not None:
            img = pygame.transform.scale(self.img_dorso, (ancho, alto))
            self.pantalla.blit(img, (x, y))
            return
        
        # Fallback sin imagen
        pygame.draw.rect(self.pantalla, (100, 100, 100), (x, y, ancho, alto), border_radius=5)
        pygame.draw.rect(self.pantalla, (50, 50, 50), (x, y, ancho, alto), 2, border_radius=5)
    

    def dibujar_ficha_mano(self, ficha, x, y, seleccionada=False):
        if ficha.orientacion == "horizontal":
            ancho = self.largo_ficha
            alto = self.ancho_ficha
            # Posición sin desplazar
            dx = 0
            dy = 0
        else:
            ancho = self.ancho_ficha
            alto = self.largo_ficha
            # Desplazar para centrar la ficha vertical en el espacio de la horizontal
            # La ficha horizontal ocupaba LARGO_FICHA x ANCHO_FICHA
            # La ficha vertical ocupa ANCHO_FICHA x LARGO_FICHA
            # Para centrarla, hay que desplazarla:
            #   - En X: (LARGO_FICHA - ANCHO_FICHA) / 2
            #   - En Y: (ANCHO_FICHA - LARGO_FICHA) / 2 (negativo, sube)
            dx = 0
            dy = (self.ancho_ficha - self.largo_ficha) // 2
        
        if self.img_frente is not None:
            if ficha.orientacion == "vertical" :
                img = self.img_frente_v
            else :
                img = self.img_frente

            self.pantalla.blit(img, (x + dx, y + dy))
            
            if seleccionada:
                pygame.draw.rect(self.pantalla, (100, 200, 255), (x + dx, y + dy, ancho, alto), 
                               max(2, int(4 * self.escala)), border_radius=5)
            
            self.dibujar_valores_ficha(ficha, x + dx, y + dy, ancho, alto)
            return

    def dibujar_ficha_arrastrada(self, ficha, x, y):
        """
        Dibuja la ficha que se está arrastrando, siguiendo al mouse.
        """
        if ficha.orientacion == "horizontal":
            ancho = self.largo_ficha
            alto = self.ancho_ficha
            dx = 0
            dy = 0
        else:
            ancho = self.ancho_ficha
            alto = self.largo_ficha
            # Centrar la ficha vertical en el espacio que ocuparía una horizontal
            dx = (self.largo_ficha - self.ancho_ficha) // 2
            dy = (self.ancho_ficha - self.largo_ficha) // 2
        
        if self.img_frente is not None:
            if ficha.orientacion == "vertical":
                img = self.img_frente_v
            else:
                img = self.img_frente

            self.pantalla.blit(img, (x + dx, y + dy))
            
            # Borde verde para arrastre
            pygame.draw.rect(self.pantalla, (200, 255, 200), (x + dx, y + dy, ancho, alto), 
                           max(2, int(4 * self.escala)), border_radius=5)
            
            self.dibujar_valores_ficha(ficha, x + dx, y + dy, ancho, alto)
            return
        
        # Fallback sin imágenes
        color = (200, 255, 200)
        pygame.draw.rect(self.pantalla, color, (x, y, ancho, alto), border_radius=5)
        pygame.draw.rect(self.pantalla, (100, 100, 100), (x, y, ancho, alto), 2, border_radius=5)
        
        if ficha.orientacion == "horizontal":
            pygame.draw.line(self.pantalla, (100, 100, 100), 
                           (x + ancho//2, y + 5), (x + ancho//2, y + alto - 5), 2)
        else:
            pygame.draw.line(self.pantalla, (100, 100, 100), 
                           (x + 5, y + alto//2), (x + ancho - 5, y + alto//2), 2)
        
        if ficha.orientacion == "horizontal":
            texto1 = self.fuente_fraccion.render(ficha.textos["O"].replace("/", "|"), True, (0, 0, 0))
            texto2 = self.fuente_fraccion.render(ficha.textos["E"].replace("/", "|"), True, (0, 0, 0))
            self.pantalla.blit(texto1, (x + int(10 * self.escala), y + alto//2 - self.tamano_fuente_fraccion//2))
            self.pantalla.blit(texto2, (x + ancho - int(30 * self.escala), y + alto//2 - self.tamano_fuente_fraccion//2))
        else:
            texto1 = self.fuente_fraccion.render(ficha.textos["N"].replace("/", "|"), True, (0, 0, 0))
            texto2 = self.fuente_fraccion.render(ficha.textos["S"].replace("/", "|"), True, (0, 0, 0))
            self.pantalla.blit(texto1, (x + ancho//2 - self.tamano_fuente_fraccion//2, y + int(10 * self.escala)))
            self.pantalla.blit(texto2, (x + ancho//2 - self.tamano_fuente_fraccion//2, y + alto - int(30 * self.escala)))
    '''
    def dibujar_ficha_arrastrada(self, ficha, x, y):
        """
        Dibuja la ficha que se está arrastrando, siguiendo al mouse.
        """
        if ficha.orientacion == "horizontal":
            ancho = self.largo_ficha
            alto = self.ancho_ficha
        else:
            ancho = self.ancho_ficha
            alto = self.largo_ficha
        
        if self.img_frente is not None:
            if ficha.orientacion == "vertical":
                img = self.img_frente_v
            else :
                img = self.img_frente

            self.pantalla.blit(img, (x, y))
            
            # Borde verde para arrastre
            pygame.draw.rect(self.pantalla, (200, 255, 200), (x, y, ancho, alto), 
                           max(2, int(4 * self.escala)), border_radius=5)
            
            self.dibujar_valores_ficha(ficha, x, y, ancho, alto)
            return
        
        # Fallback sin imágenes
        color = (200, 255, 200)
        pygame.draw.rect(self.pantalla, color, (x, y, ancho, alto), border_radius=5)
        pygame.draw.rect(self.pantalla, (100, 100, 100), (x, y, ancho, alto), 2, border_radius=5)
        
        if ficha.orientacion == "horizontal":
            pygame.draw.line(self.pantalla, (100, 100, 100), 
                           (x + ancho//2, y + 5), (x + ancho//2, y + alto - 5), 2)
        else:
            pygame.draw.line(self.pantalla, (100, 100, 100), 
                           (x + 5, y + alto//2), (x + ancho - 5, y + alto//2), 2)
        
        if ficha.orientacion == "horizontal":
            texto1 = self.fuente_fraccion.render(ficha.textos["O"].replace("/", "|"), True, (0, 0, 0))
            texto2 = self.fuente_fraccion.render(ficha.textos["E"].replace("/", "|"), True, (0, 0, 0))
            self.pantalla.blit(texto1, (x + int(10 * self.escala), y + alto//2 - self.tamano_fuente_fraccion//2))
            self.pantalla.blit(texto2, (x + ancho - int(30 * self.escala), y + alto//2 - self.tamano_fuente_fraccion//2))
        else:
            texto1 = self.fuente_fraccion.render(ficha.textos["N"].replace("/", "|"), True, (0, 0, 0))
            texto2 = self.fuente_fraccion.render(ficha.textos["S"].replace("/", "|"), True, (0, 0, 0))
            self.pantalla.blit(texto1, (x + ancho//2 - self.tamano_fuente_fraccion//2, y + int(10 * self.escala)))
            self.pantalla.blit(texto2, (x + ancho//2 - self.tamano_fuente_fraccion//2, y + alto - int(30 * self.escala)))
    '''

    # ============================================================
    # DIBUJO DE TABLERO, POZO Y OTROS
    # ============================================================
    
    def dibujar_pozo(self):
        """Dibuja las fichas del pozo boca abajo en el centro del tablero"""
        fichas_pozo = self.partida.pozo.fichas
        if not fichas_pozo:
            return
        
        centro_x = self.ancho_pantalla // 2
        centro_y = self.alto_pantalla // 2
        
        por_fila = 6
        separacion = int(3 * self.escala)
        ancho = self.ancho_ficha
        alto = self.largo_ficha
        
        total_ancho = por_fila * (ancho + separacion)
        total_alto = (len(fichas_pozo) // por_fila + 1) * (alto + separacion)
        
        inicio_x = centro_x - total_ancho // 2
        inicio_y = centro_y - total_alto // 2
        
        max_mostrar = 30
        for i in range(min(len(fichas_pozo), max_mostrar)):
            fila = i // por_fila
            columna = i % por_fila
            
            x = inicio_x + columna * (ancho + separacion)
            y = inicio_y + fila * (alto + separacion)
            
            self.dibujar_ficha_dorso(x, y, ancho, alto)
        
        texto = self.fuente.render(f"Pozo: {len(fichas_pozo)} fichas", True, (200, 200, 200))
        self.pantalla.blit(texto, (centro_x - int(60 * self.escala), inicio_y - int(30 * self.escala)))
    
    def dibujar_tablero(self):
        """Dibuja el tablero centrado en la pantalla"""
        for casilla in self.partida.tablero.casillas:
            x = int(casilla.x * self.escala) + self.offset_tablero_x
            y = int(casilla.y * self.escala) + self.offset_tablero_y
            
            if casilla.ficha is not None:
                if casilla.orientacion == "horizontal":
                    ancho = self.largo_ficha
                    alto = self.ancho_ficha
                else:
                    ancho = self.ancho_ficha
                    alto = self.largo_ficha
                
                destacada = casilla in self.casillas_destacadas
                
                self.dibujar_ficha_tablero(
                    casilla.ficha,
                    x, y,
                    ancho, alto,
                    resaltada=destacada
                )
            else:
                if casilla.orientacion == "horizontal":
                    ancho = self.largo_ficha
                    alto = self.ancho_ficha
                else:
                    ancho = self.ancho_ficha
                    alto = self.largo_ficha
                
                # Casilla vacía
                if casilla in self.casillas_destacadas:
                    color = COLOR_CASILLA_DESTACADA  # Verde brillante
                    grosor = 0
                    pygame.draw.rect(self.pantalla, color, (x, y, ancho, alto))
                else:
                    color = COLOR_CASILLA_VACIA  # Rosa
                    grosor = 2  # <--- Aumentado de 1 a 2
                    pygame.draw.rect(self.pantalla, color, (x, y, ancho, alto), grosor)

                #color = COLOR_CASILLA_DESTACADA if casilla in self.casillas_destacadas else (50, 50, 50)
                pygame.draw.rect(self.pantalla, color, (x, y, ancho, alto), grosor)
    
    # ============================================================
    # FUNCIONES DE DETECCIÓN
    # ============================================================
    
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
        x_ajustada = (x - self.offset_tablero_x) / self.escala
        y_ajustada = (y - self.offset_tablero_y) / self.escala
        
        for casilla in self.partida.tablero.casillas:
            if (casilla.x <= x_ajustada <= casilla.x + LARGO_FICHA and
                casilla.y <= y_ajustada <= casilla.y + ANCHO_FICHA):
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
        
        self.partida.verificar_fin_partida()
        if self.partida.terminada:
            if self.partida.ganador:
                self.mostrar_mensaje(f"🎉 ¡{self.partida.ganador.nombre} GANÓ!", "success")
            else:
                self.mostrar_mensaje("🤝 EMPATE", "warning")
            self.actualizar_botones()
            return True
        
        return False
    
    def dibujar_mensajes(self):
        """Dibuja los mensajes en el centro del tablero"""
        if not self.mensaje:
            return
        
        # Posición centrada
        centro_x = self.ancho_pantalla // 2
        centro_y = int(80 * self.escala)
        
        # Fondo semitransparente
        texto = self.fuente_grande.render(self.mensaje, True, (255, 255, 255))
        ancho_texto = texto.get_width()
        alto_texto = texto.get_height()
        
        # Fondo
        s = pygame.Surface((ancho_texto + 40, alto_texto + 20), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        self.pantalla.blit(s, (centro_x - ancho_texto//2 - 20, centro_y - alto_texto//2 - 10))
        
        # Texto
        self.pantalla.blit(texto, (centro_x - ancho_texto//2, centro_y - alto_texto//2))

    def dibujar_ayuda(self):
        """Dibuja las instrucciones en la esquina inferior derecha"""
        x = self.ancho_pantalla - int(300 * self.escala)
        y = self.alto_pantalla - int(100 * self.escala)
        
        lineas = [
            "G: Girar ficha",
            "F: Pantalla completa",
            "ESC: Salir"
        ]
        
        for i, linea in enumerate(lineas):
            texto = self.fuente.render(linea, True, (150, 150, 150))
            self.pantalla.blit(texto, (x, y + i * int(25 * self.escala)))

    async def ejecutar(self):
        """Bucle principal del juego"""
        ejecutando = True
        
        while ejecutando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    ejecutando = False
                
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        ejecutando = False
                    elif evento.key == pygame.K_g:
                        if self.ficha_seleccionada is not None and not self.partida.terminada:
                            self.ficha_seleccionada.girar_90()
                            self.mostrar_mensaje(f"🔄 Ficha girada: {self.ficha_seleccionada.mostrar_valores()}")
                            self.actualizar_posiciones_fichas()
                            self.actualizar_botones()
                
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
                        
                        # Seleccionar ficha con click (sin arrastre todavía)
                        ficha, jugador = self.obtener_ficha_en_posicion(x, y)
                        
                        if ficha is not None and jugador == self.partida.jugador_actual() and not self.partida.terminada:
                            # Guardar la ficha clickeada y la posición
                            self.ficha_clickeada = ficha
                            self.pos_click_x = x
                            self.pos_click_y = y
                            
                            # NO iniciar arrastre todavía
                            self.ficha_arrastrada = None
                            self.ficha_seleccionada = ficha
                
                elif evento.type == pygame.MOUSEMOTION:
                    # Si hay una ficha clickeada y se movió el mouse, iniciar arrastre
                    if hasattr(self, 'ficha_clickeada') and self.ficha_clickeada is not None and not self.partida.terminada:
                        # Calcular distancia desde el clic
                        dx = evento.pos[0] - self.pos_click_x
                        dy = evento.pos[1] - self.pos_click_y
                        
                        # Si se movió más de 10 píxeles, iniciar arrastre
                        if (dx*dx + dy*dy) > 100:  # 10 píxeles al cuadrado
                            self.ficha_arrastrada = self.ficha_clickeada
                            self.ficha_clickeada = None  # Ya no es un clic
                            
                            # Calcular offset
                            for pos in self.posiciones_fichas["jugador1"] + self.posiciones_fichas["jugador2"]:
                                if pos["ficha"] == self.ficha_arrastrada:
                                    self.offset_x = self.pos_click_x - pos["x"]
                                    self.offset_y = self.pos_click_y - pos["y"]
                                    break
                            
                            self.actualizar_posiciones_fichas()
                            self.actualizar_casillas_destacadas(self.ficha_arrastrada, self.partida.jugador_actual())
                            self.mostrar_mensaje(f"📌 Arrastrando: {self.ficha_arrastrada.mostrar_valores()}")
                    
                    # Si ya hay arrastre, actualizar casillas destacadas
                    if self.ficha_arrastrada is not None and not self.partida.terminada:
                        self.actualizar_casillas_destacadas(
                            self.ficha_arrastrada, 
                            self.partida.jugador_actual()
                        )
                
                elif evento.type == pygame.MOUSEBUTTONUP:
                    if evento.button == 1:
                        # Si hay ficha clickeada y no se movió (no hubo arrastre)
                        if hasattr(self, 'ficha_clickeada') and self.ficha_clickeada is not None and not self.partida.terminada:
                            # Es un clic → girar la ficha
                            self.ficha_clickeada.girar_90()
                            self.offset_x = 0
                            self.offset_y = 0
                            self.mostrar_mensaje(f"🔄 Ficha girada: {self.ficha_clickeada.mostrar_valores()}")
                            self.actualizar_posiciones_fichas()
                            self.actualizar_botones()
                            self.ficha_clickeada = None
                            self.ficha_seleccionada = None
                        
                        # Si hay arrastre, procesar la colocación
                        elif self.ficha_arrastrada is not None and not self.partida.terminada:
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
                        
                        # Limpiar estado de clic
                        self.ficha_clickeada = None
            
            # Dibujar
            self.pantalla.fill(COLOR_FONDO)
            
            # Mensajes (turno y jugadas) dentro del tablero
            self.dibujar_mensajes()
            
            self.dibujar_pozo()
            self.dibujar_tablero()
            
            for jugador_id, posiciones in self.posiciones_fichas.items():
                for pos in posiciones:
                    es_seleccionada = pos["ficha"] == self.ficha_seleccionada and pos["ficha"] != self.ficha_arrastrada
                    self.dibujar_ficha_mano(
                        pos["ficha"],
                        pos["x"], pos["y"],
                        seleccionada=es_seleccionada
                    )
            
            if self.ficha_arrastrada is not None:
                x, y = pygame.mouse.get_pos()
                self.dibujar_ficha_arrastrada(
                    self.ficha_arrastrada,
                    x - self.offset_x,
                    y - self.offset_y
                )
            
            for boton in self.botones:
                boton.dibujar(self.pantalla, self.fuente)
            
            self.dibujar_ayuda()
            
            pygame.display.flip()
            await asyncio.sleep(1 / 60)
        
        pygame.quit()
        return
'''
    async def ejecutar(self):
        """Bucle principal del juego"""
        ejecutando = True
        
        while ejecutando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    ejecutando = False
                
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        ejecutando = False
                    elif evento.key == pygame.K_g:
                        if self.ficha_seleccionada is not None and not self.partida.terminada:
                            self.ficha_seleccionada.girar_90()
                            self.mostrar_mensaje(f"🔄 Ficha girada: {self.ficha_seleccionada.mostrar_valores()}")
                            self.actualizar_posiciones_fichas()
                            self.actualizar_botones()
                    elif evento.key == pygame.K_f: #TECLA F TOCADO PARA PyGBAG, VER SI CAMBIAR
                        pygame.display.toggle_fullscreen()
                
                elif evento.type == pygame.MOUSEBUTTONDOWN:
                    if evento.button == 1:
                        x, y = evento.pos
                        
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
                        
                        ficha, jugador = self.obtener_ficha_en_posicion(x, y)
                        
                        if ficha is not None and jugador == self.partida.jugador_actual() and not self.partida.terminada:
                            self.ficha_seleccionada = ficha
                            self.ficha_arrastrada = ficha
                            
                            for pos in self.posiciones_fichas["jugador1"] + self.posiciones_fichas["jugador2"]:
                                if pos["ficha"] == ficha:
                                    self.offset_x = x - pos["x"]
                                    self.offset_y = y - pos["y"]
                                    break
                            self.actualizar_posiciones_fichas()
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
            
            # Dibujar
            self.pantalla.fill(COLOR_FONDO)
            
            # Mensajes (turno y jugadas) dentro del tablero
            self.dibujar_mensajes()
            
            self.dibujar_pozo()
            self.dibujar_tablero()
            
            for jugador_id, posiciones in self.posiciones_fichas.items():
                for pos in posiciones:
                    es_seleccionada = pos["ficha"] == self.ficha_seleccionada and pos["ficha"] != self.ficha_arrastrada
                    self.dibujar_ficha_mano(
                        pos["ficha"],
                        pos["x"], pos["y"],
                        seleccionada=es_seleccionada
                    )
            
            if self.ficha_arrastrada is not None:
                x, y = pygame.mouse.get_pos()
                self.dibujar_ficha_arrastrada(
                    self.ficha_arrastrada,
                    x - self.offset_x,
                    y - self.offset_y
                )
            
            for boton in self.botones:
                boton.dibujar(self.pantalla, self.fuente)
            
            self.dibujar_ayuda()
            
            pygame.display.flip()
            await asyncio.sleep(1 / 60)  # <--- CEDER CONTROL AL NAVEGADOR
            #self.clock.tick(60)
        
        pygame.quit()
        sys.exit()'''


async def main():
    juego = JuegoPygame()
    await juego.ejecutar()

if __name__ == "__main__":
    juego = JuegoPygame()
    asyncio.run(juego.ejecutar())