# main.py

from partida import Partida
import os

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def mostrar_extremos(partida):
    """Muestra los extremos disponibles"""
    if not partida.tablero.primera_jugada:
        print(f"\n🔢 EXTREMOS:")
        print(f"  HEAD: {partida.tablero.head_posible.texto()} (casilla {partida.tablero.head_posible.casilla.numero})")
        print(f"  TAIL: {partida.tablero.tail_posible.texto()} (casilla {partida.tablero.tail_posible.casilla.numero})")
    else:
        print("\n🎯 PRIMERA JUGADA - Coloca donde quieras")

def mostrar_tablero_resumido(partida):
    """Muestra un resumen del tablero"""
    fichas_jugadas = len(partida.tablero.fichas_jugadas)
    print(f"\n📊 TABLERO: {fichas_jugadas} fichas colocadas")
    
    # Mostrar primeras y últimas fichas
    if partida.tablero.fichas_jugadas:
        print("  (HEAD) ← ", end="")
        for i, (ficha, casilla) in enumerate(partida.tablero.fichas_jugadas):
            if i < 3 or i >= len(partida.tablero.fichas_jugadas) - 3:
                if i > 0 and i < len(partida.tablero.fichas_jugadas) - 3:
                    print("... ", end="")
                else:
                    print(f"{ficha.mostrar_valores()} ", end="")
        print("→ (TAIL)")

def turno_jugador(partida):
    """Ejecuta el turno de un jugador humano"""
    jugador = partida.jugador_actual()
    
    limpiar_pantalla()
    print("="*70)
    print(f"🎲 DOMINÓ DE FRACCIONES - Turno de {jugador.nombre}")
    print("="*70)
    
    # Mostrar estado
    print(f"\n📦 Pozo: {partida.pozo.cantidad()} fichas")
    mostrar_tablero_resumido(partida)
    mostrar_extremos(partida)
    
    # Mostrar fichas del jugador
    print(f"\n🎴 TUS FICHAS:")
    for i, ficha in enumerate(jugador.fichas):
        print(f"  {i+1}. {ficha.mostrar_valores()} ({ficha.orientacion})")
    
    # Verificar si puede jugar
    if not partida.puede_jugar(jugador):
        print(f"\n⛔ No puedes jugar con tus fichas actuales.")
        
        if partida.pozo.cantidad() > 0:
            print(f"📥 Robando una ficha del pozo...")
            ficha = partida.levantar_ficha(jugador)
            if ficha:
                print(f"   Robaste: {ficha.mostrar_valores()}")
                if partida.puede_jugar(jugador):
                    print(f"   ✅ ¡Ahora puedes jugar!")
                    input("Presiona Enter para continuar...")
                    return turno_jugador(partida)  # Reintentar
                else:
                    print(f"   ❌ Sigues sin poder jugar.")
        else:
            print(f"📭 Pozo vacío. Pasas turno.")
        
        partida.cambiar_turno()
        input("Presiona Enter para continuar...")
        return
    
    # Seleccionar ficha
    while True:
        try:
            print(f"\n📝 Elige una ficha (1-{len(jugador.fichas)}) o 0 para pasar turno:")
            seleccion = input("→ ")
            
            if seleccion == "0":
                print(f"\n⏭️ {jugador.nombre} pasa turno.")
                partida.cambiar_turno()
                input("Presiona Enter para continuar...")
                return
            
            idx = int(seleccion) - 1
            if 0 <= idx < len(jugador.fichas):
                ficha = jugador.fichas[idx]
                break
            else:
                print("❌ Número inválido. Intenta de nuevo.")
        except ValueError:
            print("❌ Entrada inválida. Intenta de nuevo.")
    
    # Mostrar opciones de la ficha
    print(f"\n📋 Ficha seleccionada: {ficha.mostrar_valores()}")
    print(f"   Orientación actual: {ficha.orientacion}")
    print(f"   Valores: O={ficha.textos['O']}, E={ficha.textos['E']}, N={ficha.textos['N']}, S={ficha.textos['S']}")
    
    # Opciones: girar o colocar
    while True:
        print(f"\n¿Qué quieres hacer?")
        print(f"  1. Girar 90°")
        print(f"  2. Colocar en casilla")
        print(f"  3. Volver a elegir ficha")
        
        try:
            opcion = input("→ ")
            
            if opcion == "1":
                ficha.girar_90()
                print(f"🔄 Ficha girada: {ficha.mostrar_valores()} ({ficha.orientacion})")
                continue
            
            elif opcion == "2":
                # Mostrar casillas disponibles
                print(f"\n📍 Casillas disponibles:")
                
                if partida.tablero.primera_jugada:
                    # Primera jugada: cualquier casilla libre
                    libres = [c for c in partida.tablero.casillas if c.ficha is None]
                    print("   (Primera jugada - cualquier casilla libre sirve)")
                    for c in libres:
                        print(f"  {c.numero}. {c.orientacion}")
                else:
                    # Mostrar solo HEAD y TAIL
                    head = partida.tablero.head_posible.casilla
                    tail = partida.tablero.tail_posible.casilla
                    print(f"  {head.numero}. HEAD (requiere {partida.tablero.head_posible.texto()}) - {head.orientacion}")
                    print(f"  {tail.numero}. TAIL (requiere {partida.tablero.tail_posible.texto()}) - {tail.orientacion}")
                
                print(f"\n📝 ¿En qué casilla quieres colocar?")
                num_casilla = input("→ ")
                
                try:
                    num = int(num_casilla)
                    casilla = None
                    for c in partida.tablero.casillas:
                        if c.numero == num:
                            casilla = c
                            break
                    
                    if casilla is None:
                        print("❌ Casilla no encontrada.")
                        continue
                    
                    if casilla.ficha is not None:
                        print("❌ Esa casilla ya está ocupada.")
                        continue
                    
                    # Verificar si es primera jugada o extremo
                    if not partida.tablero.primera_jugada:
                        head_num = partida.tablero.head_posible.casilla.numero
                        tail_num = partida.tablero.tail_posible.casilla.numero
                        if casilla.numero != head_num and casilla.numero != tail_num:
                            print("❌ Esa casilla no es un extremo (HEAD o TAIL).")
                            continue
                    
                    # Verificar orientación
                    if ficha.orientacion != casilla.orientacion:
                        print(f"❌ La ficha es {ficha.orientacion} pero la casilla es {casilla.orientacion}.")
                        print("   Puedes girar la ficha (opción 1) antes de intentar de nuevo.")
                        continue
                    
                    # Intentar colocar
                    exito = partida.jugar_ficha(ficha, casilla)
                    
                    if exito:
                        print(f"✅ ¡Ficha colocada con éxito en casilla {casilla.numero}!")
                        
                        # Verificar si ganó
                        if partida.jugador_gano():
                            print(f"\n🎉🎉🎉 ¡{jugador.nombre} GANÓ LA PARTIDA! 🎉🎉🎉")
                            partida.terminada = True
                            partida.ganador = jugador
                        
                        input("Presiona Enter para continuar...")
                        return
                    else:
                        print("❌ La ficha no encaja en esa casilla.")
                        continue
                        
                except ValueError:
                    print("❌ Número de casilla inválido.")
                    continue
            
            elif opcion == "3":
                print("↩️ Volviendo a elegir ficha...")
                return turno_jugador(partida)
            
            else:
                print("❌ Opción inválida.")
                
        except ValueError:
            print("❌ Entrada inválida.")

def main():
    print("="*70)
    print("🎲 DOMINÓ DE FRACCIONES 🎲")
    print("="*70)
    
    # Crear partida
    partida = Partida("fichas.csv")
    
    print(f"\n👥 Jugadores:")
    print(f"  {partida.jugadores[0].nombre}: {partida.jugadores[0].cantidad_fichas()} fichas")
    print(f"  {partida.jugadores[1].nombre}: {partida.jugadores[1].cantidad_fichas()} fichas")
    print(f"  Pozo: {partida.pozo.cantidad()} fichas")
    
    input("\nPresiona Enter para comenzar...")
    
    # Bucle principal
    while not partida.terminada:
        turno_jugador(partida)
    
    # Mostrar resultado final
    limpiar_pantalla()
    print("="*70)
    print("🏁 PARTIDA TERMINADA 🏁")
    print("="*70)
    
    if partida.ganador:
        print(f"\n🎉 GANADOR: {partida.ganador.nombre} 🎉")
        print(f"   Fichas restantes: {partida.ganador.cantidad_fichas()}")
    else:
        print("\n🤝 EMPATE")
    
    print(f"\n📊 Estadísticas finales:")
    print(f"  Fichas Jugador 1: {partida.jugadores[0].cantidad_fichas()}")
    print(f"  Fichas Jugador 2: {partida.jugadores[1].cantidad_fichas()}")
    print(f"  Fichas en pozo: {partida.pozo.cantidad()}")
    print(f"  Fichas jugadas: {len(partida.tablero.fichas_jugadas)}")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()