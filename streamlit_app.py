# streamlit_app.py

import streamlit as st
from partida import Partida

# Inicializar el estado de la partida
if 'partida' not in st.session_state:
    st.session_state.partida = Partida("fichas.csv")
    st.session_state.mensajes = []

def agregar_mensaje(texto, tipo="info"):
    st.session_state.mensajes.append({"texto": texto, "tipo": tipo})

def reiniciar_partida():
    st.session_state.partida = Partida("fichas.csv")
    st.session_state.mensajes = []
    agregar_mensaje("🔄 Partida reiniciada", "success")

# Configurar página
st.set_page_config(page_title="Dominó de Fracciones", layout="wide")
st.title("🎲 Dominó de Fracciones")

# Sidebar con controles
with st.sidebar:
    st.header("📊 Estado")
    
    if 'partida' in st.session_state:
        partida = st.session_state.partida
        st.metric("Turno", partida.jugador_actual().nombre)
        st.metric("Fichas J1", partida.jugadores[0].cantidad_fichas())
        st.metric("Fichas J2", partida.jugadores[1].cantidad_fichas())
        st.metric("Pozo", partida.pozo.cantidad())
        st.metric("Fichas jugadas", len(partida.tablero.fichas_jugadas))
    
    st.button("🔄 Reiniciar partida", on_click=reiniciar_partida)

# Columna principal
col1, col2 = st.columns([2, 1])

with col1:
    # Mostrar mensajes
    if 'mensajes' in st.session_state and st.session_state.mensajes:
        for msg in st.session_state.mensajes[-20:]:
            if msg["tipo"] == "success":
                st.success(msg["texto"])
            elif msg["tipo"] == "error":
                st.error(msg["texto"])
            elif msg["tipo"] == "warning":
                st.warning(msg["texto"])
            else:
                st.info(msg["texto"])

with col2:
    st.header("🎯 Acciones")
    
    if 'partida' in st.session_state:
        partida = st.session_state.partida
        
        # Verificar si la partida terminó
        if partida.terminada:
            if partida.ganador:
                st.success(f"🎉 GANADOR: {partida.ganador.nombre}")
            else:
                st.warning("🤝 Empate")
            
            st.json({
                "Jugador 1": partida.jugadores[0].cantidad_fichas(),
                "Jugador 2": partida.jugadores[1].cantidad_fichas(),
                "Pozo": partida.pozo.cantidad(),
                "Fichas jugadas": len(partida.tablero.fichas_jugadas)
            })
            st.stop()
        
        # Estado del turno actual
        jugador = partida.jugador_actual()
        ya_robo = partida.ya_robo_en_turno
        puede_robar = partida.puede_robar(jugador)
        
        # ============================================
        # CASO 1: Ya robó en este turno
        # ============================================

        if ya_robo:
            st.info("📌 Ya robaste una ficha en este turno.")
            
            # Mostrar SOLO la ficha que robó
            st.subheader(f"🎴 Ficha robada")
            
            ficha = partida.ficha_robada
            
            if ficha:
                st.write(f"📌 {ficha.mostrar_valores()} ({ficha.orientacion})")
                
                # Botón para girar la ficha robada
                if st.button("🔄 Girar 90°", key="girar_robada"):
                    ficha.girar_90()
                    agregar_mensaje(f"🔄 Ficha girada: {ficha.mostrar_valores()}", "info")
                    st.rerun()
                
                # Colocar la ficha robada
                st.subheader("📍 Colocar en casilla")
                
                if partida.tablero.primera_jugada:
                    casillas_libres = [c for c in partida.tablero.casillas if c.ficha is None]
                    opciones_casillas = [f"{c.numero} ({c.orientacion})" for c in casillas_libres]
                else:
                    head = partida.tablero.head_posible.casilla
                    tail = partida.tablero.tail_posible.casilla
                    casillas_libres = [head, tail]
                    opciones_casillas = [
                        f"{head.numero} HEAD (requiere {partida.tablero.head_posible.texto()})",
                        f"{tail.numero} TAIL (requiere {partida.tablero.tail_posible.texto()})"
                    ]
                
                if casillas_libres:
                    seleccion_casilla = st.selectbox("Elige casilla:", opciones_casillas, key="casilla_robada")
                    idx_casilla = opciones_casillas.index(seleccion_casilla)
                    casilla = casillas_libres[idx_casilla]
                    
                    if st.button("✅ Colocar ficha", type="primary", key="colocar_robada"):
                        if ficha.orientacion != casilla.orientacion:
                            agregar_mensaje(f"❌ La ficha es {ficha.orientacion} pero la casilla es {casilla.orientacion}", "error")
                        else:
                            exito = partida.jugar_ficha(ficha, casilla)
                            if exito:
                                agregar_mensaje(f"✅ Ficha colocada en casilla {casilla.numero}", "success")
                                if partida.jugador_gano():
                                    agregar_mensaje(f"🎉🎉🎉 ¡{jugador.nombre} GANÓ!", "success")
                            else:
                                agregar_mensaje("❌ La ficha no encaja en esa casilla", "error")
                        st.rerun()
            else:
                st.warning("No hay ficha robada (error)")
            
            # Pasar turno (disponible porque ya robó)
            if st.button("⏭️ Pasar turno", type="secondary", key="pasar_ya_robo"):
                partida.pasar_turno()
                agregar_mensaje(f"⏭️ {jugador.nombre} pasa turno", "warning")
                st.rerun()
        
        # ============================================
        # CASO 2: No robó aún
        # ============================================
        else:
            # Mostrar fichas del jugador
            st.subheader(f"🎴 Fichas de {jugador.nombre}")
            
            if jugador.fichas:
                opciones_fichas = [f"{i+1}. {ficha.mostrar_valores()} ({ficha.orientacion})" 
                                  for i, ficha in enumerate(jugador.fichas)]
                seleccion = st.selectbox("Elige una ficha:", opciones_fichas, key="ficha_no_robo")
                idx = opciones_fichas.index(seleccion)
                ficha = jugador.fichas[idx]
                
                if st.button("🔄 Girar 90°", key="girar_no_robo"):
                    ficha.girar_90()
                    agregar_mensaje(f"🔄 Ficha girada: {ficha.mostrar_valores()}", "info")
                    st.rerun()
                
                st.subheader("📍 Colocar en casilla")
                
                if partida.tablero.primera_jugada:
                    casillas_libres = [c for c in partida.tablero.casillas if c.ficha is None]
                    opciones_casillas = [f"{c.numero} ({c.orientacion})" for c in casillas_libres]
                else:
                    head = partida.tablero.head_posible.casilla
                    tail = partida.tablero.tail_posible.casilla
                    casillas_libres = [head, tail]
                    opciones_casillas = [
                        f"{head.numero} HEAD (requiere {partida.tablero.head_posible.texto()})",
                        f"{tail.numero} TAIL (requiere {partida.tablero.tail_posible.texto()})"
                    ]
                
                if casillas_libres:
                    seleccion_casilla = st.selectbox("Elige casilla:", opciones_casillas, key="casilla_no_robo")
                    idx_casilla = opciones_casillas.index(seleccion_casilla)
                    casilla = casillas_libres[idx_casilla]
                    
                    if st.button("✅ Colocar ficha", type="primary", key="colocar_no_robo"):
                        if ficha.orientacion != casilla.orientacion:
                            agregar_mensaje(f"❌ La ficha es {ficha.orientacion} pero la casilla es {casilla.orientacion}", "error")
                        else:
                            exito = partida.jugar_ficha(ficha, casilla)
                            if exito:
                                agregar_mensaje(f"✅ Ficha colocada en casilla {casilla.numero}", "success")
                                if partida.jugador_gano():
                                    agregar_mensaje(f"🎉🎉🎉 ¡{jugador.nombre} GANÓ!", "success")
                            else:
                                agregar_mensaje("❌ La ficha no encaja en esa casilla", "error")
                        st.rerun()
            else:
                st.warning("No tienes fichas")
            
            # Botón para robar (SIEMPRE disponible si el pozo tiene fichas)
            if puede_robar:
                if st.button("📥 Robar del pozo", type="primary", key="robar_no_robo"):
                    ficha = partida.robar_ficha()
                    if ficha:
                        agregar_mensaje(f"📥 {jugador.nombre} robó: {ficha.mostrar_valores()}", "info")
                        st.rerun()
            else:
                if partida.pozo.cantidad() == 0:
                    st.info("📭 Pozo vacío")
            
            # NO hay botón "Pasar turno" aquí (no se puede pasar sin robar)
        
        # ============================================
        # Mostrar extremos (siempre al final)
        # ============================================
        st.divider()
        st.subheader("🔢 Extremos")
        
        if not partida.tablero.primera_jugada:
            col_tail, col_head = st.columns(2)
            with col_tail:
                st.metric("⬅️ TAIL", partida.tablero.tail_posible.texto())
            with col_head:
                st.metric("HEAD ➡️", partida.tablero.head_posible.texto())
        else:
            st.info("🎯 Primera jugada - coloca donde quieras")