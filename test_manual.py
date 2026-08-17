# test_manual.py

from partida import Partida

def pausa():
    """Pausa la ejecución hasta que el usuario presione Enter"""
    input("\nPresiona Enter para continuar...")

def test_colocacion_fichas():
    """Prueba controlada de colocación de fichas"""
    print("="*70)
    print("🎯 PRUEBA MANUAL - COLOCACIÓN DE FICHAS 🎯")
    print("="*70)
    
    # Crear partida
    partida = Partida("fichas.csv")
    jugador1 = partida.jugadores[0]
    jugador2 = partida.jugadores[1]
    
    print("\n📋 Fichas iniciales del Jugador 1:")
    jugador1.mostrar_fichas()
    
    pausa()
    
    # PRUEBA 1: Primera jugada
    print("\n" + "="*70)
    print("PRUEBA 1: Primera jugada (cualquier casilla libre)")
    print("="*70)
    
    ficha = jugador1.fichas[0]
    casilla = partida.tablero.casillas[5]  # Casilla 5 (horizontal)
    
    print(f"Ficha a colocar: {ficha.mostrar_valores()}")
    print(f"Casilla: {casilla.numero} ({casilla.orientacion})")
    
    exito = partida.jugar_ficha(ficha, casilla)
    print(f"¿Colocada con éxito? {exito}")
    print(f"Turno actual: {partida.jugador_actual().nombre}")
    
    if exito:
        print(f"HEAD: {partida.tablero.head_posible.valor}")
        print(f"TAIL: {partida.tablero.tail_posible.valor}")
    
    pausa()
    
    # PRUEBA 2: Segunda jugada (debe ir en HEAD o TAIL)
    print("\n" + "="*70)
    print("PRUEBA 2: Segunda jugada (debe ser HEAD o TAIL)")
    print("="*70)
    
    jugador_actual = partida.jugador_actual()
    print(f"\nTurno de: {jugador_actual.nombre}")
    jugador_actual.mostrar_fichas()
    
    # Mostrar extremos
    print(f"\nExtremos disponibles:")
    print(f"HEAD: casilla {partida.tablero.head_posible.casilla.numero} valor {partida.tablero.head_posible.valor}")
    print(f"TAIL: casilla {partida.tablero.tail_posible.casilla.numero} valor {partida.tablero.tail_posible.valor}")
    
    # Buscar una ficha que encaje en HEAD
    ficha_head = None
    for f in jugador_actual.fichas:
        if partida.tablero.head_posible.valor in f.valores.values():
            ficha_head = f
            break
    
    if ficha_head:
        print(f"\n✅ Encontrada ficha que encaja en HEAD: {ficha_head.mostrar_valores()}")
        casilla_head = partida.tablero.head_posible.casilla
        
        print(f"Colocando en HEAD (casilla {casilla_head.numero})...")
        exito = partida.jugar_ficha(ficha_head, casilla_head)
        print(f"¿Colocada con éxito? {exito}")
        print(f"Turno actual: {partida.jugador_actual().nombre}")
        
        if exito:
            print(f"Nuevo HEAD: {partida.tablero.head_posible.valor}")
            print(f"TAIL: {partida.tablero.tail_posible.valor}")
    else:
        print("❌ No hay ficha que encaje en HEAD")
    
    pausa()
    
    # PRUEBA 3: Intentar colocar en casilla que no es extremo
    print("\n" + "="*70)
    print("PRUEBA 3: Intentar colocar en casilla que NO es extremo")
    print("="*70)
    
    jugador_actual = partida.jugador_actual()
    print(f"\nTurno de: {jugador_actual.nombre}")
    
    if jugador_actual.fichas:
        ficha = jugador_actual.fichas[0]
        print(f"Ficha seleccionada: {ficha.mostrar_valores()}")
        
        # Buscar una casilla libre que NO sea HEAD ni TAIL
        casilla_no_extremo = None
        for c in partida.tablero.casillas:
            if c.ficha is None:
                if (c.numero != partida.tablero.head_posible.casilla.numero and 
                    c.numero != partida.tablero.tail_posible.casilla.numero):
                    casilla_no_extremo = c
                    break
        
        if casilla_no_extremo:
            print(f"Intentando colocar en casilla {casilla_no_extremo.numero} (NO es extremo)...")
            exito = partida.jugar_ficha(ficha, casilla_no_extremo)
            print(f"¿Se colocó? {exito} (DEBERÍA SER False)")
            print(f"Turno actual: {partida.jugador_actual().nombre} (DEBERÍA SEGUIR SIENDO EL MISMO)")
        else:
            print("❌ No hay casilla no-extremo disponible")
    
    pausa()
    
    # PRUEBA 4: Intentar colocar ficha que no encaja en extremo
    print("\n" + "="*70)
    print("PRUEBA 4: Intentar colocar ficha que NO encaja en extremo")
    print("="*70)
    
    jugador_actual = partida.jugador_actual()
    print(f"\nTurno de: {jugador_actual.nombre}")
    
    # Buscar una ficha que NO encaje en ningún extremo
    ficha_no_encaja = None
    for f in jugador_actual.fichas:
        if (partida.tablero.head_posible.valor not in f.valores.values() and 
            partida.tablero.tail_posible.valor not in f.valores.values()):
            ficha_no_encaja = f
            break
    
    if ficha_no_encaja:
        print(f"Ficha que NO encaja: {ficha_no_encaja.mostrar_valores()}")
        print(f"HEAD requiere: {partida.tablero.head_posible.valor}")
        print(f"TAIL requiere: {partida.tablero.tail_posible.valor}")
        
        # Intentar colocarla en HEAD
        casilla_head = partida.tablero.head_posible.casilla
        print(f"Intentando colocar en HEAD (casilla {casilla_head.numero})...")
        exito = partida.jugar_ficha(ficha_no_encaja, casilla_head)
        print(f"¿Se colocó? {exito} (DEBERÍA SER False)")
        print(f"Turno actual: {partida.jugador_actual().nombre} (DEBERÍA SEGUIR SIENDO EL MISMO)")
    else:
        print("✅ Todas las fichas encajan en algún extremo")
    
    pausa()
    
    # PRUEBA 5: Colocación válida en TAIL
    print("\n" + "="*70)
    print("PRUEBA 5: Colocación válida en TAIL")
    print("="*70)
    
    jugador_actual = partida.jugador_actual()
    print(f"\nTurno de: {jugador_actual.nombre}")
    jugador_actual.mostrar_fichas()
    
    # Buscar ficha que encaje en TAIL
    ficha_tail = None
    for f in jugador_actual.fichas:
        if partida.tablero.tail_posible.valor in f.valores.values():
            ficha_tail = f
            break
    
    if ficha_tail:
        print(f"✅ Ficha que encaja en TAIL: {ficha_tail.mostrar_valores()}")
        casilla_tail = partida.tablero.tail_posible.casilla
        print(f"Colocando en TAIL (casilla {casilla_tail.numero})...")
        
        exito = partida.jugar_ficha(ficha_tail, casilla_tail)
        print(f"¿Colocada con éxito? {exito} (DEBERÍA SER True)")
        print(f"Turno actual: {partida.jugador_actual().nombre} (DEBERÍA CAMBIAR)")
        
        if exito:
            print(f"HEAD: {partida.tablero.head_posible.valor}")
            print(f"Nuevo TAIL: {partida.tablero.tail_posible.valor}")
    else:
        print("❌ No hay ficha que encaje en TAIL")
    
    print("\n" + "="*70)
    print("✅ PRUEBAS MANUALES COMPLETADAS")
    print("="*70)

if __name__ == "__main__":
    test_colocacion_fichas()