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

# Colores de jugadores
COLOR_JUGADOR1 = (200, 100, 100)  # Rojo suave
COLOR_JUGADOR2 = (100, 150, 220)  # Azul suave
COLOR_TEXTO = (255, 255, 255)

ANCHO_PANTALLA = 1200
ALTO_PANTALLA = 750

archivofuente = 'junegull.ttf'
#archivofuente = 'Ubuntu-Title.ttf'


class Boton:
    def __init__(self, x, y, ancho, alto, texto, imagen=None, color=COLOR_BOTON, color_hover=COLOR_BOTON_HOVER):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.imagen = imagen  # <--- Imagen del botón
        self.color = color
        self.color_hover = color_hover
        self.activo = True
        self.fuente = None
    
    def dibujar(self, pantalla, fuente):
        # Si hay imagen, dibujarla
        if self.imagen is not None:
            img = pygame.transform.scale(self.imagen, (self.rect.width, self.rect.height))
            pantalla.blit(img, (self.rect.x, self.rect.y))
        else:
            # Fallback: dibujar rectángulo
            color = self.color_hover if self.esta_sobre() and self.activo else self.color
            pygame.draw.rect(pantalla, color, self.rect, border_radius=8)
            pygame.draw.rect(pantalla, (150, 150, 150), self.rect, 2, border_radius=8)
        
        # Texto del botón (si tiene)
        if self.texto:
            if self.activo:
                texto_surface = fuente.render(self.texto, True, COLOR_TEXTO_BOTON)
            else:
                texto_surface = fuente.render(self.texto, True, (100, 100, 100))
            
            # Centrar el texto en el rectángulo del botón
            texto_rect = texto_surface.get_rect(center=self.rect.center)
            
            # Si es el botón de reinicio, ajustar verticalmente
            if "Reiniciar" in self.texto or "Ayuda" in self.texto:
                texto_rect.y -= 5
                texto_rect.x -= 5  # <--- Ajustá este valor (2, 3, 4, 5) hasta que quede bien
            
            pantalla.blit(texto_surface, texto_rect)
    
    def esta_sobre(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())
    
    def click(self):
        return self.activo and self.esta_sobre()


class JuegoPygame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        if hasattr(sys, 'pygodide'):
            # WEB: usar el tamaño definido en config
            self.ancho_pantalla = ANCHO_PANTALLA
            self.alto_pantalla = ALTO_PANTALLA
            self.pantalla = pygame.display.set_mode((self.ancho_pantalla, self.alto_pantalla))
        else:
            info = pygame.display.Info()
            self.ancho_pantalla = info.current_w
            self.alto_pantalla = info.current_h
            self.pantalla = pygame.display.set_mode((self.ancho_pantalla, self.alto_pantalla), pygame.FULLSCREEN)

        pygame.display.set_caption("Dominó de equivalencias")
        self.clock = pygame.time.Clock()

        
        self.recalcular_tamanos()

        # Cargar imágenes
        self.cargar_imagenes()
        
        # Crear partida (con 4 fichas por jugador para pruebas rápidas)
        self.partida = Partida("fichas.csv", fichas_por_jugador=6)
        
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

        self.mostrar_confirmacion_reinicio = False
        self.mensaje_confirmacion = ""
        self.mostrar_ayuda = False

        # Posiciones de las fichas en la mano
        self.posiciones_fichas = {
            "jugador1": [],
            "jugador2": []
        }
        self.actualizar_posiciones_fichas()
        
        # Crear botones
        self.crear_botones()
    
    def obtener_tamaño_canvas(self):
        """Obtiene el tamaño real del canvas en el navegador"""
        if hasattr(sys, 'pygodide'):
            try:
                import js
                canvas = js.document.getElementById('canvas')
                self.ancho_pantalla = canvas.clientWidth
                self.alto_pantalla = canvas.clientHeight
            except:
                pass

    def recalcular_tamanos(self):
        BASE_ANCHO = ANCHO_PANTALLA
        BASE_ALTO = ALTO_PANTALLA
        self.escala_x = self.ancho_pantalla / BASE_ANCHO
        self.escala_y = self.alto_pantalla / BASE_ALTO
        self.escala = min(self.escala_x, self.escala_y)


        self.largo_ficha = int(LARGO_FICHA * self.escala)
        self.ancho_ficha = int(ANCHO_FICHA * self.escala)
        self.margen_tablero = int(MARGEN_TABLERO * self.escala)
        
        self.tamano_fuente = max(12, int(24 * self.escala))
        self.tamano_fuente_grande = max(16, int(36 * self.escala))
        #self.tamano_fuente_fraccion = max(10, int(20 * self.escala))
        self.tamano_fuente_fraccion = max(10, int(20 * self.escala))
        
        print(f"📐 Escalado: {self.escala:.2f}x")
        print(f"   Ficha: {self.largo_ficha}x{self.ancho_ficha}")
        print(f"   Fuente: {self.tamano_fuente}px")

        # Cargar tipografía desde archivo
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            ruta_fuente = os.path.join(script_dir, "fonts", archivofuente)
            
            self.fuente = pygame.font.Font(ruta_fuente, self.tamano_fuente)
            self.fuente_grande = pygame.font.Font(ruta_fuente, self.tamano_fuente_grande)
            self.fuente_fraccion = pygame.font.Font(ruta_fuente, self.tamano_fuente_fraccion)
            print("✅ Tipografía cargada correctamente")
        except Exception as e:
            print(f"⚠️ Error cargando tipografía: {e}")
            # Fallback a fuente por defecto
            self.fuente = pygame.font.Font(None, self.tamano_fuente)
            self.fuente_grande = pygame.font.Font(None, self.tamano_fuente_grande)
            self.fuente_fraccion = pygame.font.Font(None, self.tamano_fuente_fraccion)
    
    def cargar_imagenes(self):
        """Carga las imágenes de los assets"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            assets_dir = os.path.join(script_dir, "assets")
            sonidos_dir = os.path.join(script_dir, "sonidos")
            
            # Fichas
            ruta_frente = os.path.join(assets_dir, "ficha.png")
            ruta_frente_v = os.path.join(assets_dir, "ficha_v.png")
            ruta_dorso = os.path.join(assets_dir, "dorso.png")
            ruta_dorso_v = os.path.join(assets_dir, "dorso_v.png")
            
            self.img_frente = pygame.image.load(ruta_frente)
            self.img_frente_v = pygame.image.load(ruta_frente_v)
            self.img_dorso = pygame.image.load(ruta_dorso)
            self.img_dorso_v = pygame.image.load(ruta_dorso_v)
            
            self.img_frente = pygame.transform.scale(self.img_frente, (self.largo_ficha, self.ancho_ficha))
            self.img_frente_v = pygame.transform.scale(self.img_frente_v, (self.ancho_ficha, self.largo_ficha))
            self.img_dorso = pygame.transform.scale(self.img_dorso, (self.largo_ficha, self.ancho_ficha))
            self.img_dorso_v = pygame.transform.scale(self.img_dorso_v, (self.ancho_ficha, self.largo_ficha))
            
            # Botones
            ruta_boton_robar = os.path.join(assets_dir, "boton_robar.png")
            ruta_boton_pasar = os.path.join(assets_dir, "boton_pasar.png")
            ruta_boton_reset = os.path.join(assets_dir, "boton_reset.png")
            ruta_boton_ayuda = os.path.join(assets_dir, "boton_ayuda.png")
            
            self.img_boton_robar = pygame.image.load(ruta_boton_robar)
            self.img_boton_pasar = pygame.image.load(ruta_boton_pasar)
            self.img_boton_reset = pygame.image.load(ruta_boton_reset)
            self.img_boton_ayuda = pygame.image.load(ruta_boton_ayuda)

            print("✅ Imágenes cargadas correctamente")

            # Cargar sonidos
            self.sonido_win = pygame.mixer.Sound(os.path.join(sonidos_dir, "win.mp3"))
            self.sonido_girar = pygame.mixer.Sound(os.path.join(sonidos_dir, "girar.mp3"))
            self.sonido_clic = pygame.mixer.Sound(os.path.join(sonidos_dir, "clic.mp3"))
            self.sonido_coin = pygame.mixer.Sound(os.path.join(sonidos_dir, "coin.mp3"))
            
            print("✅ Sonidos cargados correctamente")

        except Exception as e:
            print(f"⚠️ Error cargando imágenes: {e}")
            self.img_frente = None
            self.img_frente_v = None
            self.img_dorso = None
            self.img_boton_robar = None
            self.img_boton_pasar = None
            self.img_boton_reset = None
            self.img_boton_ayuda = None
            print(f"⚠️ Error cargando sonidos: {e}")
            # Si falla, crear sonidos vacíos para no romper el juego
            self.sonido_win = None
            self.sonido_girar = None
            self.sonido_clic = None
            self.sonido_coin = None

    def calcular_offset_tablero(self):
        """Calcula el offset para centrar el tablero en la pantalla"""
        # Offset fijo para centrar visualmente
        # Si el tablero está corrido 50 píxeles a la izquierda, sumamos 50 al offset
        # Ajustá este valor hasta que quede centrado
        
        # Calculamos el offset base con el centro geométrico
        min_x = float('inf')
        max_x = float('-inf')
        min_y = float('inf')
        max_y = float('-inf')
        
        for casilla in self.partida.tablero.casillas:
            if casilla.x < min_x:
                min_x = casilla.x
            if casilla.x + LARGO_FICHA > max_x:
                max_x = casilla.x + LARGO_FICHA
            if casilla.y < min_y:
                min_y = casilla.y
            if casilla.y + ANCHO_FICHA > max_y:
                max_y = casilla.y + ANCHO_FICHA
        
        centro_x = (min_x + max_x) / 2
        centro_y = (min_y + max_y) / 2
        
        # Offset base
        offset_x = self.ancho_pantalla // 2 - int(centro_x * self.escala)
        offset_y = self.alto_pantalla // 2 - int(centro_y * self.escala)
        
        # Ajuste de media ficha horizontal (escalado)
        media_ficha = int((ANCHO_FICHA / 2) * self.escala)
        self.offset_tablero_x = offset_x + media_ficha
        self.offset_tablero_y = offset_y
        
        '''
        centro_x = (min_x + max_x) // 2
        centro_y = (min_y + max_y) // 2
        
        # Offset base
        base_offset_x = self.ancho_pantalla // 2 - int(centro_x * self.escala)
        base_offset_y = self.alto_pantalla // 2 - int(centro_y * self.escala)
        
        # Ajuste manual (cambiá estos valores hasta que quede centrado)
        ajuste_x = int(40 * self.escala)   # <--- Probá con 20, 40, 60, -20, -40
        ajuste_y = 0
        
        self.offset_tablero_x = base_offset_x + ajuste_x
        self.offset_tablero_y = base_offset_y + ajuste_y
        
        print(f"base_offset_x={base_offset_x}, ajuste_x={ajuste_x}, offset_x={self.offset_tablero_x}")
        '''
    
    def crear_botones(self):
        """Crea los botones de la interfaz"""
        self.botones = []
        
        alto_boton = int(50 * self.escala)
        ancho_boton = int(200 * self.escala)
        separacion = int(20 * self.escala)
        
        centro_x = self.ancho_pantalla // 2
        y_boton = self.alto_pantalla // 2 + int(220 * self.escala) #Altura del botón
        
        # Botón Robar con imagen
        self.boton_robar = Boton(
            centro_x - ancho_boton - separacion//2, 
            y_boton, 
            ancho_boton, 
            alto_boton, 
            "Robar del pozo",  # <--- Texto (opcional, puede ser "")
            self.img_boton_robar  # <--- Imagen
        )
        self.botones.append(self.boton_robar)
        
        # Botón Pasar con imagen
        self.boton_pasar = Boton(
            centro_x + separacion//2, 
            y_boton, 
            ancho_boton, 
            alto_boton, 
            "Pasar turno",  # <--- Texto (opcional, puede ser "")
            self.img_boton_pasar  # <--- Imagen
        )
        self.botones.append(self.boton_pasar)

        x_reiniciar = int(30 * self.escala)
        y_reiniciar = self.alto_pantalla - int(75 * self.escala)
        ancho_reiniciar = int(150 * self.escala)
        alto_reiniciar = int(50 * self.escala)
        
        self.boton_reiniciar = Boton(
            x_reiniciar,
            y_reiniciar,
            ancho_reiniciar,
            alto_reiniciar,
            "Reiniciar",
            self.img_boton_reset
        )
        self.botones.append(self.boton_reiniciar)

        x_ayuda = self.ancho_pantalla - int(150 * self.escala) - int(30 * self.escala)
        y_ayuda = self.alto_pantalla - int(75 * self.escala)
        ancho_ayuda = int(150 * self.escala)
        alto_ayuda = int(50 * self.escala)
        
        self.boton_ayuda = Boton(
            x_ayuda,
            y_ayuda,
            ancho_ayuda,
            alto_ayuda,
            "Ayuda",
            self.img_boton_ayuda
        )
        self.botones.append(self.boton_ayuda)
    
    def actualizar_botones(self):
        """Actualiza qué botones están activos según el estado del juego"""
        partida = self.partida
        jugador = partida.jugador_actual()
        ya_robo = partida.ya_robo_en_turno
        puede_robar = partida.puede_robar(jugador)
        
        self.boton_robar.activo = not ya_robo and puede_robar and not partida.terminada
        self.boton_pasar.activo = ya_robo and not partida.terminada
        self.boton_reiniciar.activo = True
        self.boton_ayuda.activo = True
        #self.boton_girar.activo = self.ficha_seleccionada is not None and not partida.terminada
    
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
        """Dibuja los valores de la ficha en dos líneas centradas como bloque"""
        # Fondo semitransparente para legibilidad
        s = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        s.fill((255, 255, 255, 180))
        self.pantalla.blit(s, (x, y))
        
        # Línea central de la ficha
        if ficha.orientacion == "horizontal":
            pygame.draw.line(self.pantalla, (80, 80, 80), 
                           (x + ancho//2, y + 5), 
                           (x + ancho//2, y + alto - 5), 2)
        else:
            pygame.draw.line(self.pantalla, (80, 80, 80), 
                           (x + 5, y + alto//2), 
                           (x + ancho - 5, y + alto//2), 2)
        
        # Función para dibujar fracción
        def dibujar_fraccion(texto, x_centro, y_centro):
            """Dibuja una fracción con línea horizontal"""
            if "/" in texto:
                num, den = texto.split("/")
            else:
                num = texto
                den = ""
            
            # Renderizar textos
            texto_num = self.fuente_fraccion.render(num, True, (0, 0, 0)) if num else None
            texto_den = self.fuente_fraccion.render(den, True, (0, 0, 0)) if den else None
            
            # Alto de los textos
            alto_num = texto_num.get_height() if texto_num else 0
            alto_den = texto_den.get_height() if texto_den else 0
            
            # Espacio entre líneas
            separacion_entre_lineas = 2
            
            # Ancho máximo del bloque (para la línea)
            ancho_num = texto_num.get_width() if texto_num else 0
            ancho_den = texto_den.get_width() if texto_den else 0
            ancho_max = max(ancho_num, ancho_den)
            
            # Ajustar ancho de la línea (con margen)
            ancho_linea = int(ancho_max * 1)
            alto_linea = 2  # <--- Altura de la línea (probá con 2, 3, 4)
            
            # Alto total del bloque
            alto_total = alto_num + alto_den + separacion_entre_lineas + alto_linea
            
            # Calcular posición Y para centrar el bloque
            y_inicio = y_centro - alto_total // 2
            
            # Dibujar numerador (arriba)
            if texto_num:
                self.pantalla.blit(texto_num, 
                    (x_centro - texto_num.get_width() // 2, 
                     y_inicio))
            
            # Dibujar línea horizontal
            y_linea = y_inicio + alto_num + separacion_entre_lineas // 2
            pygame.draw.rect(self.pantalla, (0, 0, 0), 
                            (x_centro - ancho_linea // 2, y_linea, ancho_linea, alto_linea))
            
            # Dibujar denominador (abajo)
            if texto_den:
                y_den = y_linea + alto_linea + separacion_entre_lineas // 2
                self.pantalla.blit(texto_den, 
                    (x_centro - texto_den.get_width() // 2, 
                     y_den))
        
        # Dibujar valores según orientación
        if ficha.orientacion == "horizontal":
            dibujar_fraccion(ficha.textos["O"], x + ancho//4, y + alto//2)
            dibujar_fraccion(ficha.textos["E"], x + 3 * ancho//4, y + alto//2)
        else:
            dibujar_fraccion(ficha.textos["N"], x + ancho//2, y + alto//4)
            dibujar_fraccion(ficha.textos["S"], x + ancho//2, y + 3 * alto//4)

    
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
    

    def dibujar_ficha_dorso(self, x, y, ancho, alto, orientacion="horizontal"):
        """Dibuja una ficha boca abajo (dorso)"""
        if orientacion == "vertical" and self.img_dorso_v is not None:
            #img = pygame.transform.scale(self.img_dorso_v, (ancho, alto))
            #self.pantalla.blit(img, (x, y))
            self.pantalla.blit(self.img_dorso_v, (x, y))
        elif self.img_dorso is not None:
            #img = pygame.transform.scale(self.img_dorso, (ancho, alto))
            #self.pantalla.blit(img, (x, y))
            self.pantalla.blit(self.img_dorso, (x, y))
        else:
            # Fallback sin imagen
            pygame.draw.rect(self.pantalla, (100, 100, 100), (x, y, ancho, alto), border_radius=5)
            pygame.draw.rect(self.pantalla, (50, 50, 50), (x, y, ancho, alto), 2, border_radius=5)


    def dibujar_ficha_mano(self, ficha, x, y, seleccionada=False, es_turno=True):
        """
        Dibuja una ficha en la mano de un jugador.
        Si no es el turno del jugador, muestra el dorso.
        """
        if es_turno:
            # Mostrar frente (código existente)
            if ficha.orientacion == "horizontal":
                ancho = self.largo_ficha
                alto = self.ancho_ficha
                dx = 0
                dy = 0
            else:
                ancho = self.ancho_ficha
                alto = self.largo_ficha
                dx = 0
                dy = (self.ancho_ficha - self.largo_ficha) // 2
            
            if self.img_frente is not None:
                img = self.img_frente_v if ficha.orientacion == "vertical" else self.img_frente
                self.pantalla.blit(img, (x + dx, y + dy))
                
                if seleccionada:
                    pygame.draw.rect(self.pantalla, (100, 200, 255), (x + dx, y + dy, ancho, alto), 
                                   max(2, int(4 * self.escala)), border_radius=5)
                
                self.dibujar_valores_ficha(ficha, x + dx, y + dy, ancho, alto)
                return
        else:
            # Mostrar dorso
            if ficha.orientacion == "horizontal":
                ancho = self.largo_ficha
                alto = self.ancho_ficha
            else:
                ancho = self.ancho_ficha
                alto = self.largo_ficha
            
            if self.img_dorso is not None:
                img = self.img_dorso_v if ficha.orientacion == "vertical" else self.img_dorso
                self.pantalla.blit(img, (x, y))
                return


    '''
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
    '''

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
            
            ficha = fichas_pozo[i]
            self.dibujar_ficha_dorso(x, y, ancho, alto, 'vertical')
        
        texto = self.fuente.render(f"Pozo: {len(fichas_pozo)} fichas", True, (200, 200, 200))
        self.pantalla.blit(texto, (centro_x - texto.get_width() // 2, inicio_y - int(30 * self.escala)))
    

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
            if casilla.orientacion == "horizontal":
                # Horizontal: ancho = LARGO_FICHA, alto = ANCHO_FICHA
                ancho = LARGO_FICHA
                alto = ANCHO_FICHA
            else:
                # Vertical: ancho = ANCHO_FICHA, alto = LARGO_FICHA
                ancho = ANCHO_FICHA
                alto = LARGO_FICHA
            
            if (casilla.x <= x_ajustada <= casilla.x + ancho and
                casilla.y <= y_ajustada <= casilla.y + alto):
                return casilla
        
        return None

    def actualizar_casillas_destacadas(self, ficha, jugador):
        self.casillas_destacadas = []
        if ficha is None:
            return
        
        x, y = pygame.mouse.get_pos()
        casilla_bajo_mouse = self.obtener_casilla_en_posicion(x, y)
        
        if casilla_bajo_mouse is None:
            return
        
        if casilla_bajo_mouse.ficha is not None:
            return
        
        if jugador == self.partida.jugador_actual():
            if self.partida.tablero.primera_jugada:
                if casilla_bajo_mouse.orientacion == ficha.orientacion:
                    self.casillas_destacadas.append(casilla_bajo_mouse)
            else:
                head = self.partida.tablero.head_posible.casilla
                tail = self.partida.tablero.tail_posible.casilla
                if casilla_bajo_mouse.numero == head.numero or casilla_bajo_mouse.numero == tail.numero:
                    if casilla_bajo_mouse.orientacion == ficha.orientacion:
                        self.casillas_destacadas.append(casilla_bajo_mouse)

    def verificar_y_mostrar_fin_partida(self):
        """Verifica si la partida terminó y muestra el mensaje correspondiente"""
        if self.partida.terminada:
            if self.partida.ganador:
                # Determinar color del ganador
                if self.partida.ganador == self.partida.jugadores[0]:
                    color = COLOR_JUGADOR1  # Rojo suave para Jugador 1
                else:
                    color = COLOR_JUGADOR2  # Azul suave para Jugador 2
                if self.sonido_win:
                    self.sonido_win.play()
                self.mostrar_mensaje(f"¡{self.partida.ganador.nombre} GANÓ!", "success", color)
            else:
                self.mostrar_mensaje("EMPATE", "warning")
            self.actualizar_botones()
            return True
        
        self.partida.verificar_fin_partida()
        if self.partida.terminada:
            if self.partida.ganador:
                if self.partida.ganador == self.partida.jugadores[0]:
                    color = COLOR_JUGADOR1
                else:
                    color = COLOR_JUGADOR2
                self.mostrar_mensaje(f"¡{self.partida.ganador.nombre} GANÓ!", "success", color)
            else:
                self.mostrar_mensaje("EMPATE", "warning")
            self.actualizar_botones()
            return True
        
        return False


    def mostrar_mensaje(self, texto, tipo="info", color=None):
        """Muestra un mensaje en la pantalla"""
        self.mensaje = texto
        self.tiempo_mensaje = pygame.time.get_ticks()
        if color:
            self.mensaje_color = color
        else:
            self.mensaje_color = COLOR_TEXTO  # blanco por defecto

    def dibujar_mensajes(self):
        """Dibuja el título, turno y mensajes"""
        centro_x = self.ancho_pantalla // 2
        
        # TÍTULO (arriba del pozo)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        ruta_fuente = os.path.join(script_dir, "fonts", archivofuente)
        fuente_titulo = pygame.font.Font(ruta_fuente, int(48 * self.escala))
        titulo = fuente_titulo.render("Dominó de equivalencias", True, (255, 255, 200))
        y_titulo = int(150 * self.escala)
        
        ancho_t = titulo.get_width()
        alto_t = titulo.get_height()
        self.pantalla.blit(titulo, (centro_x - ancho_t//2, y_titulo - alto_t//2))
        
        # Turno o mensaje de fin de partida
        if self.partida.terminada:
            # Mostrar mensaje de ganador o empate
            if self.partida.ganador:
                if self.partida.ganador == self.partida.jugadores[0]:
                    color = COLOR_JUGADOR1
                else:
                    color = COLOR_JUGADOR2
                texto = f"¡{self.partida.ganador.nombre} GANÓ!"
            else:
                color = COLOR_TEXTO
                texto = "EMPATE"
        else:
            # Mostrar turno normal
            jugador_actual = self.partida.jugador_actual()
            if jugador_actual == self.partida.jugadores[0]:
                color = COLOR_JUGADOR1
            else:
                color = COLOR_JUGADOR2
            texto = f"Turno: {jugador_actual.nombre}"
        
        texto_turno = self.fuente_grande.render(texto, True, color)
        y_turno = y_titulo + int(400 * self.escala)
        ancho_turno = texto_turno.get_width()
        alto_turno = texto_turno.get_height()
        self.pantalla.blit(texto_turno, (centro_x - ancho_turno//2, y_turno - alto_turno//2))

    '''
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
        """Dibuja el título, turno y mensajes"""
        centro_x = self.ancho_pantalla // 2
        
        # TÍTULO (arriba del pozo)
        # Usar la misma tipografía personalizada
        script_dir = os.path.dirname(os.path.abspath(__file__))
        ruta_fuente = os.path.join(script_dir, "fonts", archivofuente)  # <--- Tu archivo .ttf
        fuente_titulo = pygame.font.Font(ruta_fuente, int(48 * self.escala))  # <--- Más grande
        titulo = fuente_titulo.render("Dominó de equivalencias", True, (255, 255, 200))
        y_titulo = int(150 * self.escala)
        
        # Fondo para el título
        ancho_t = titulo.get_width()
        alto_t = titulo.get_height()
        self.pantalla.blit(titulo, (centro_x - ancho_t//2, y_titulo - alto_t//2))
        
        # Turno (debajo del título)

        jugador_actual = self.partida.jugador_actual()
        if jugador_actual == self.partida.jugadores[0]:
            color_turno = COLOR_JUGADOR1  # Rojo suave para Jugador 1
        else:
            color_turno = COLOR_JUGADOR2  # Azul suave para Jugador 2

        texto_turno = self.fuente_grande.render(
            f"Turno: {jugador_actual.nombre}" if not self.partida.terminada else "PARTIDA TERMINADA",
            True, color_turno
        )
        y_turno = y_titulo + int(400 * self.escala)
        ancho_turno = texto_turno.get_width()
        alto_turno = texto_turno.get_height()
        self.pantalla.blit(texto_turno, (centro_x - ancho_turno//2, y_turno - alto_turno//2))
    '''    
    
    def dibujar_ayuda(self):
        """Dibuja las instrucciones en la esquina inferior derecha"""
        x = self.ancho_pantalla - int(300 * self.escala)
        y = self.alto_pantalla - int(100 * self.escala)
        
        lineas = ["ESC: Salir"]
        
        for i, linea in enumerate(lineas):
            texto = self.fuente.render(linea, True, (150, 150, 150))
            self.pantalla.blit(texto, (x, y + i * int(25 * self.escala)))

    def reiniciar_partida(self):
        """Reinicia la partida"""
        # Crear una nueva partida
        self.partida = Partida("fichas.csv", fichas_por_jugador=6)
        
        # Resetear estado del juego
        self.ficha_seleccionada = None
        self.ficha_arrastrada = None
        self.ficha_robada_actual = None
        self.ficha_clickeada = None
        self.casillas_destacadas = []
        self.mensaje = ""
        self.tiempo_mensaje = 0
        self.offset_x = 0
        self.offset_y = 0
        
        # Recalcular offset del tablero
        self.calcular_offset_tablero()
        
        # Actualizar posiciones de las fichas
        self.actualizar_posiciones_fichas()
        
        # Actualizar botones
        self.actualizar_botones()
        
        self.mostrar_mensaje("Partida reiniciada")


    def dibujar_confirmacion_reinicio(self):
        """Dibuja el cartel de confirmación de reinicio"""
        if not self.mostrar_confirmacion_reinicio:
            return
        
        # Fondo oscuro semitransparente
        s = pygame.Surface((self.ancho_pantalla, self.alto_pantalla), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        self.pantalla.blit(s, (0, 0))
        
        # Cartel
        ancho_cartel = int(400 * self.escala)
        alto_cartel = int(150 * self.escala)
        x_cartel = (self.ancho_pantalla - ancho_cartel) // 2
        y_cartel = (self.alto_pantalla - alto_cartel) // 2
        
        pygame.draw.rect(self.pantalla, (50, 50, 50), (x_cartel, y_cartel, ancho_cartel, alto_cartel), border_radius=10)
        pygame.draw.rect(self.pantalla, (150, 150, 150), (x_cartel, y_cartel, ancho_cartel, alto_cartel), 2, border_radius=10)
        
        # Texto del mensaje
        texto = self.fuente_grande.render(self.mensaje_confirmacion, True, (255, 255, 255))
        self.pantalla.blit(texto, (self.ancho_pantalla // 2 - texto.get_width() // 2, 
                                  y_cartel + int(30 * self.escala)))
        
        # Instrucciones
        instrucciones = self.fuente.render("Presiona S para Sí, N para No", True, (200, 200, 200))
        self.pantalla.blit(instrucciones, (self.ancho_pantalla // 2 - instrucciones.get_width() // 2, 
                                          y_cartel + int(90 * self.escala)))

    def dibujar_ayuda_cartel(self):
        """Dibuja el cartel de ayuda con instrucciones"""
        if not self.mostrar_ayuda:
            return
        
        # Fondo oscuro semitransparente
        s = pygame.Surface((self.ancho_pantalla, self.alto_pantalla), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        self.pantalla.blit(s, (0, 0))
        
        # Cartel
        ancho_cartel = int(500 * self.escala)
        alto_cartel = int(400 * self.escala)
        x_cartel = (self.ancho_pantalla - ancho_cartel) // 2
        y_cartel = (self.alto_pantalla - alto_cartel) // 2
        
        pygame.draw.rect(self.pantalla, (50, 50, 50), (x_cartel, y_cartel, ancho_cartel, alto_cartel), border_radius=10)
        pygame.draw.rect(self.pantalla, (150, 150, 150), (x_cartel, y_cartel, ancho_cartel, alto_cartel), 2, border_radius=10)
        
        # Título
        titulo = self.fuente_grande.render("🎲 Instrucciones", True, (255, 255, 255))
        self.pantalla.blit(titulo, (self.ancho_pantalla // 2 - titulo.get_width() // 2, y_cartel + int(20 * self.escala)))
        
        # Línea separadora
        pygame.draw.line(self.pantalla, (150, 150, 150), 
                        (x_cartel + int(20 * self.escala), y_cartel + int(65 * self.escala)),
                        (x_cartel + ancho_cartel - int(20 * self.escala), y_cartel + int(65 * self.escala)), 1)
        
        # Instrucciones
        instrucciones = [
            "Objetivo: Colocar todas tus fichas",
            "Gira una ficha: hacé clic en ella o apretá G",
            "Robá del pozo con el botón celeste",
            "Pasá el turno cuando no puedas jugar",
        ]
        
        y_texto = y_cartel + int(85 * self.escala)
        for linea in instrucciones:
            texto = self.fuente.render(linea, True, (220, 220, 220))
            self.pantalla.blit(texto, (x_cartel + int(25 * self.escala), y_texto))
            y_texto += int(35 * self.escala)
        
        # Separador
        y_texto += int(10 * self.escala)
        pygame.draw.line(self.pantalla, (100, 100, 100), 
                        (x_cartel + int(20 * self.escala), y_texto),
                        (x_cartel + ancho_cartel - int(20 * self.escala), y_texto), 1)
        y_texto += int(20 * self.escala)
        
        # Desarrollador
        desarrollador = self.fuente.render("Desarrollado por: Ernesto López", True, (180, 180, 180))
        self.pantalla.blit(desarrollador, (self.ancho_pantalla // 2 - desarrollador.get_width() // 2, y_texto))
        y_texto += int(35 * self.escala)  # <--- AGREGAR ESTA LÍNEA

        linea_extra = self.fuente.render("Escuelas en Foco, BA", True, (180, 180, 180))
        self.pantalla.blit(linea_extra, (self.ancho_pantalla // 2 - linea_extra.get_width() // 2, y_texto))
        # Cerrar con ESC
        cerrar = self.fuente.render("Presioná ESC para cerrar", True, (150, 150, 150))
        self.pantalla.blit(cerrar, (self.ancho_pantalla // 2 - cerrar.get_width() // 2, y_cartel + alto_cartel - int(35 * self.escala)))

    async def ejecutar(self):
        """Bucle principal del juego"""
        ejecutando = True
        
        while ejecutando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    ejecutando = False
                
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        if self.mostrar_confirmacion_reinicio:
                            self.mostrar_confirmacion_reinicio = False
                            self.mensaje_confirmacion = ""
                        elif self.mostrar_ayuda:
                            self.mostrar_ayuda = False
                        else:
                            ejecutando = False
                        #ejecutando = False

                    elif evento.key == pygame.K_s:
                        if self.mostrar_confirmacion_reinicio:
                            # Reiniciar partida
                            self.reiniciar_partida()
                            self.mostrar_confirmacion_reinicio = False
                            self.mensaje_confirmacion = ""
                    
                    elif evento.key == pygame.K_n:
                        if self.mostrar_confirmacion_reinicio:
                            # Cancelar reinicio
                            self.mostrar_confirmacion_reinicio = False
                            self.mensaje_confirmacion = ""

                    elif evento.key == pygame.K_g:
                        if self.ficha_seleccionada is not None and not self.partida.terminada:
                            self.ficha_seleccionada.girar_90()
                            if self.sonido_girar:
                                self.sonido_girar.play()
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
                                            if self.sonido_clic:
                                                self.sonido_clic.play()
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
                                        if self.sonido_clic:
                                            self.sonido_clic.play()
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

                                elif boton == self.boton_reiniciar:
                                    # Mostrar cartel de confirmación
                                    self.mostrar_confirmacion_reinicio = True
                                    self.mensaje_confirmacion = "¿Reiniciar partida? (S/N)"
                                    continue

                                elif boton == self.boton_ayuda:
                                    self.mostrar_ayuda = not self.mostrar_ayuda
                                    continue
                                
                                #elif boton == self.boton_girar:
                                #    if self.ficha_seleccionada is not None and not self.partida.terminada:
                                #        self.ficha_seleccionada.girar_90()
                                #        self.mostrar_mensaje(f"🔄 Ficha girada: {self.ficha_seleccionada.mostrar_valores()}")
                                #        self.actualizar_posiciones_fichas()
                                #    continue
                        
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
                            if self.sonido_girar:
                                self.sonido_girar.play()
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
                                            if self.sonido_coin:
                                                self.sonido_coin.play()
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
                                                if self.sonido_coin:
                                                    self.sonido_coin.play()
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

            # Dibujar etiquetas de jugadores

            # Jugador 1 (izquierda)
            texto_j1 = self.fuente.render("Jugador 1", True, COLOR_JUGADOR1)
            x_j1 = int(30 * self.escala)
            y_j1 = int(50 * self.escala)
            self.pantalla.blit(texto_j1, (x_j1, y_j1))

            # Jugador 2 (derecha)
            texto_j2 = self.fuente.render("Jugador 2", True, COLOR_JUGADOR2)
            x_j2 = self.ancho_pantalla - int(30 * self.escala) - texto_j2.get_width()
            y_j2 = int(50 * self.escala)
            self.pantalla.blit(texto_j2, (x_j2, y_j2))
            
            #NUEVO: DAR VUELTA CARTAS DEL JUGADOR QUE NO ESTÁ JUGANDO
            jugador_actual = self.partida.jugador_actual()

            for jugador_id, posiciones in self.posiciones_fichas.items():
                # Determinar si es el turno de este jugador
                if jugador_id == "jugador1":
                    es_turno = (jugador_actual == self.partida.jugadores[0])
                else:  # jugador2
                    es_turno = (jugador_actual == self.partida.jugadores[1])
                
                for pos in posiciones:
                    es_seleccionada = pos["ficha"] == self.ficha_seleccionada and pos["ficha"] != self.ficha_arrastrada
                    self.dibujar_ficha_mano(
                        pos["ficha"],
                        pos["x"], pos["y"],
                        seleccionada=es_seleccionada,
                        es_turno=es_turno
                    )
            '''
            for jugador_id, posiciones in self.posiciones_fichas.items():
                for pos in posiciones:
                    es_seleccionada = pos["ficha"] == self.ficha_seleccionada and pos["ficha"] != self.ficha_arrastrada
                    self.dibujar_ficha_mano(
                        pos["ficha"],
                        pos["x"], pos["y"],
                        seleccionada=es_seleccionada
                    )
            '''

            if self.ficha_arrastrada is not None:
                x, y = pygame.mouse.get_pos()
                self.dibujar_ficha_arrastrada(
                    self.ficha_arrastrada,
                    x - self.offset_x,
                    y - self.offset_y
                )
            
            for boton in self.botones:
                boton.dibujar(self.pantalla, self.fuente)
            
            self.dibujar_ayuda_cartel()
            self.dibujar_confirmacion_reinicio()
            pygame.display.flip()
            await asyncio.sleep(1 / 60)
        
        pygame.quit()
        return

async def main():
    juego = JuegoPygame()
    await juego.ejecutar()

if __name__ == "__main__":
    #juego = JuegoPygame()
    #asyncio.run(juego.ejecutar())
    asyncio.run(main())