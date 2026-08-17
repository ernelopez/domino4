# test_partida_completa.py

from partida import Partida
import time

def pausa():
    input("\nPresiona Enter para continuar...")

def mostrar_colocacion(ficha, casilla, exito, tablero):
    """Muestra detalles de la colocación de una ficha"""
    if exito:
        print(f"  ✅ Colocada con éxito")
        print(f"  📍 Casilla: {casilla.numero}")
        print(f"  🔄 Orientación: {ficha.orientacion}")
        
        # Mostrar qué valores tiene la ficha en cada posición
        print(f"  📊 Valores de la ficha:")
        print(f"     O: {ficha.textos['O']} ({ficha.valores['O']:.3f})")
        print(f"     E: {ficha.textos['E']} ({ficha.valores['E']:.3f})")
        if ficha.orientacion == "vertical":
            print(f"     N: {ficha.textos['N']} ({ficha.valores['N']:.3f})")
            print(f"     S: {ficha.textos['S']} ({ficha.valores['S']:.3f})")
        
        # Mostrar qué extremo se usó
        if not tablero.primera_jugada:
            if casilla.numero == tablero.head_posible.casilla.numero:
                print(f"  🎯 Extremo: HEAD (requería {tablero.head_posible.valor:.3f})")
            elif casilla.numero == tablero.tail_posible.casilla.numero:
                print(f"  🎯 Extremo: TAIL (requería {tablero.tail_posible.valor:.3f})")
    else:
        print(f"  ❌ Falló la colocación")
        # Mostrar por qué falló
        if not tablero.primera_jugada:
            if casilla.numero == tablero.head_posible.casilla.numero:
                print(f"     HEAD requiere: {tablero.head_posible.valor:.3f}")
                print(f"     La ficha tiene: {ficha.valores.values()}")
            elif casilla.numero == tablero.tail_posible.casilla.numero:
                print(f"     TAIL requiere: {tablero.tail_posible.valor:.3f}")
                print(f"     La ficha tiene: {ficha.valores.values()}")

def simular_partida():
    """Simula una partida completa con turnos alternados"""
    print("="*70)
    print("🎲 SIMULACIÓN DE PARTIDA COMPLETA 🎲")
    print("="*70)
    
    # Crear partida
    partida = Partida("fichas.csv")
    
    print(f"\n📋 Fichas iniciales:")
    print(f"Jugador 1: {partida.jugadores[0].cantidad_fichas()} fichas")
    print(f"Jugador 2: {partida.jugadores[1].cantidad_fichas()} fichas")
    print(f"Pozo: {partida.pozo.cantidad()} fichas")
    
    pausa()
    
    turno_numero = 0
    
    while not partida.terminada and turno_numero < 30:  # Límite de seguridad
        turno_numero += 1
        jugador = partida.jugador_actual()
        
        print("\n" + "="*70)
        print(f"🔄 TURNO {turno_numero} - {jugador.nombre}")
        print("="*70)
        
        # Mostrar estado
        print(f"\n📊 Estado:")
        print(f"  Fichas Jugador 1: {partida.jugadores[0].cantidad_fichas()}")
        print(f"  Fichas Jugador 2: {partida.jugadores[1].cantidad_fichas()}")
        print(f"  Fichas en pozo: {partida.pozo.cantidad()}")
        print(f"  Fichas jugadas: {len(partida.tablero.fichas_jugadas)}")
        
        if not partida.tablero.primera_jugada:
            print(f"\n🔢 Extremos:")
            print(f"  HEAD: {partida.tablero.head_posible.valor} (casilla {partida.tablero.head_posible.casilla.numero})")
            print(f"  TAIL: {partida.tablero.tail_posible.valor} (casilla {partida.tablero.tail_posible.casilla.numero})")
        
        # Mostrar fichas del jugador actual
        print(f"\n🎴 Fichas de {jugador.nombre}:")
        jugador.mostrar_fichas()
        
        # Verificar si puede jugar
        puede = partida.puede_jugar(jugador)
        print(f"\n¿Puede jugar? {puede}")
        
        if not puede:
            print(f"\n⏭️ {jugador.nombre} NO PUEDE JUGAR")
            
            # Intentar robar del pozo
            if partida.pozo.cantidad() > 0:
                ficha = partida.levantar_ficha(jugador)
                if ficha is not None:
                    print(f"  Robó una ficha del pozo")
                    print(f"  Nueva ficha: {ficha.mostrar_valores()}")
                    
                    # Verificar si ahora puede jugar
                    if partida.puede_jugar(jugador):
                        print(f"  ✅ Ahora puede jugar")
                        continue  # Reintentar el mismo turno
                    else:
                        print(f"  ❌ Sigue sin poder jugar")
                else:
                    print(f"  ❌ No hay fichas en el pozo")
            else:
                print(f"  ❌ Pozo vacío")
            
            # Cambiar turno
            partida.cambiar_turno()
            print(f"\n➡️ Turno cambiado a: {partida.jugador_actual().nombre}")
            pausa()
            continue
        
        # Buscar una jugada válida
        jugada_encontrada = False
        
        # Intentar colocar en HEAD primero
        for ficha in jugador.fichas:
            if partida.tablero.primera_jugada:
                # Primera jugada: usar cualquier casilla horizontal
                for casilla in partida.tablero.casillas:
                    if casilla.ficha is None and casilla.orientacion == ficha.orientacion:
                        print(f"\n🎯 Primera jugada:")
                        print(f"  Ficha: {ficha.mostrar_valores()}")
                        print(f"  Casilla: {casilla.numero} ({casilla.orientacion})")
                        
                        # Intentar colocar
                        exito = partida.jugar_ficha(ficha, casilla)
                        mostrar_colocacion(ficha, casilla, exito, partida.tablero)
                        
                        if exito:
                            jugada_encontrada = True
                            break
                if jugada_encontrada:
                    break
            else:
                # Buscar ficha que encaje en HEAD
                if partida.tablero.head_posible.valor in ficha.valores.values():
                    casilla = partida.tablero.head_posible.casilla
                    if casilla.ficha is None:
                        print(f"\n🎯 Colocando en HEAD:")
                        print(f"  Ficha: {ficha.mostrar_valores()}")
                        print(f"  HEAD requiere: {partida.tablero.head_posible.valor}")
                        print(f"  Casilla: {casilla.numero} ({casilla.orientacion})")
                        
                        # Intentar colocar
                        exito = partida.jugar_ficha(ficha, casilla)
                        mostrar_colocacion(ficha, casilla, exito, partida.tablero)
                        
                        if exito:
                            jugada_encontrada = True
                            break
                
                # Si no encaja en HEAD, probar en TAIL
                if not jugada_encontrada and partida.tablero.tail_posible.valor in ficha.valores.values():
                    casilla = partida.tablero.tail_posible.casilla
                    if casilla.ficha is None:
                        print(f"\n🎯 Colocando en TAIL:")
                        print(f"  Ficha: {ficha.mostrar_valores()}")
                        print(f"  TAIL requiere: {partida.tablero.tail_posible.valor}")
                        print(f"  Casilla: {casilla.numero} ({casilla.orientacion})")
                        
                        # Intentar colocar
                        exito = partida.jugar_ficha(ficha, casilla)
                        mostrar_colocacion(ficha, casilla, exito, partida.tablero)
                        
                        if exito:
                            jugada_encontrada = True
                            break
        
        if not jugada_encontrada:
            print(f"\n⚠️ No se encontró jugada válida")
            
            # Intentar robar
            if partida.pozo.cantidad() > 0:
                ficha = partida.levantar_ficha(jugador)
                if ficha is not None:
                    print(f"  Robó una ficha del pozo")
                    print(f"  Nueva ficha: {ficha.mostrar_valores()}")
                    
                    # Verificar si ahora puede jugar
                    if partida.puede_jugar(jugador):
                        print(f"  ✅ Ahora puede jugar")
                        continue  # Reintentar el mismo turno
                    else:
                        print(f"  ❌ Sigue sin poder jugar")
                else:
                    print(f"  ❌ No hay fichas en el pozo")
            else:
                print(f"  ❌ Pozo vacío")
            
            # Si no puede jugar, pasar turno
            partida.cambiar_turno()
            print(f"\n➡️ Turno cambiado a: {partida.jugador_actual().nombre}")
        
        # Mostrar resultado de la jugada si se colocó
        if jugada_encontrada:
            print(f"\n📊 Después de la jugada:")
            print(f"  Fichas restantes de {jugador.nombre}: {jugador.cantidad_fichas()}")
            
            if not partida.tablero.primera_jugada:
                print(f"  Nuevo HEAD: {partida.tablero.head_posible.valor}")
                print(f"  Nuevo TAIL: {partida.tablero.tail_posible.valor}")
            
            # Verificar si ganó
            if partida.jugador_gano():
                print(f"\n🎉 ¡{jugador.nombre} GANÓ LA PARTIDA!")
                partida.terminada = True
                partida.ganador = jugador
                break
        
        pausa()
    
    # Mostrar resultado final
    print("\n" + "="*70)
    print("🏁 FIN DE LA PARTIDA 🏁")
    print("="*70)
    
    if partida.ganador:
        print(f"\n🎉 GANADOR: {partida.ganador.nombre}")
        print(f"   Fichas restantes: {partida.ganador.cantidad_fichas()}")
    else:
        print("\n🤝 LA PARTIDA TERMINÓ SIN GANADOR")
        print("   (Pozo vacío o ambos jugadores bloqueados)")
    
    print(f"\n📊 Estadísticas finales:")
    print(f"  Turnos jugados: {turno_numero}")
    print(f"  Fichas Jugador 1: {partida.jugadores[0].cantidad_fichas()}")
    print(f"  Fichas Jugador 2: {partida.jugadores[1].cantidad_fichas()}")
    print(f"  Fichas en pozo: {partida.pozo.cantidad()}")
    print(f"  Fichas jugadas: {len(partida.tablero.fichas_jugadas)}")
    
    # Mostrar fichas restantes de cada jugador
    for jugador in partida.jugadores:
        if jugador.cantidad_fichas() > 0:
            print(f"\n🎴 Fichas restantes de {jugador.nombre}:")
            jugador.mostrar_fichas()
    
    print("\n" + "="*70)

if __name__ == "__main__":
    simular_partida()