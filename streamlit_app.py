# streamlit_app.py

import streamlit as st
from partida import Partida
import time

# Inicializar el estado de la partida
if 'partida' not in st.session_state:
    st.session_state.partida = Partida("fichas.csv")
    st.session_state.mensajes = []
    st.session_state.esperando_accion = False

def agregar_mensaje(texto, tipo="info"):
    st.session_state.mensajes.append({"texto": texto, "tipo": tipo})

def reiniciar_partida():
    st.session_state.partida = Partida("fichas.csv")
    st.session_state.mensajes = []
    st.session_state.esperando_accion = False
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
        for msg in st.session_state.mensajes[-20:]:  # Últimos 20 mensajes
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
        
        if not partida.terminada:
            jugador = partida.jugador_actual()
            
            # Verificar si el jugador puede jugar
            puede_jugar = partida.puede_jugar(jugador)
            
            # Si NO puede jugar, mostrar opción de robar (pero pasar siempre disponible)
            if not puede_jugar:
                st.warning(f"⛔ {jugador.nombre} no puede jugar con sus fichas actuales.")
                
                if partida.pozo.cantidad() > 0:
                    if st.button("📥 Robar del pozo", type="primary"):
                        ficha = partida.levantar_ficha(jugador)
                        if ficha:
                            agregar_mensaje(f"📥 {jugador.nombre} robó: {ficha.mostrar_valores()}", "info")
                            # Verificar si ahora puede jugar
                            if partida.puede_jugar(jugador):
                                agregar_mensaje(f"✅ ¡Ahora puedes jugar!", "success")
                            else:
                                agregar_mensaje(f"❌ Sigues sin poder jugar.", "warning")
                            st.rerun()
                else:
                    st.error("📭 Pozo vacío.")
            
            # Botón para pasar turno SIEMPRE disponible
            if st.button("⏭️ Pasar turno", type="secondary"):
                agregar_mensaje(f"⏭️ {jugador.nombre} pasa turno", "warning")
                partida.cambiar_turno()
                st.rerun()
            
            # Si NO puede jugar, no mostrar el resto (fichas, colocar, etc.)
            if not puede_jugar:
                # Mostrar extremos
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
                
                st.stop()
            
            # Si PUEDE jugar, mostrar sus fichas y acciones
            st.subheader(f"🎴 Fichas de {jugador.nombre}")
            
            if jugador.fichas:
                # Selector de ficha
                opciones_fichas = [f"{i+1}. {ficha.mostrar_valores()} ({ficha.orientacion})" 
                                  for i, ficha in enumerate(jugador.fichas)]
                seleccion = st.selectbox("Elige una ficha:", opciones_fichas)
                idx = opciones_fichas.index(seleccion)
                ficha = jugador.fichas[idx]
                
                # Botón para girar
                if st.button("🔄 Girar 90°"):
                    ficha.girar_90()
                    agregar_mensaje(f"🔄 Ficha girada: {ficha.mostrar_valores()}", "info")
                    st.rerun()
                
                # Colocar ficha
                st.subheader("📍 Colocar en casilla")
                
                if partida.tablero.primera_jugada:
                    # Primera jugada: cualquier casilla libre
                    casillas_libres = [c for c in partida.tablero.casillas if c.ficha is None]
                    opciones_casillas = [f"{c.numero} ({c.orientacion})" for c in casillas_libres]
                else:
                    # Solo HEAD y TAIL
                    head = partida.tablero.head_posible.casilla
                    tail = partida.tablero.tail_posible.casilla
                    casillas_libres = [head, tail]
                    opciones_casillas = [
                        f"{head.numero} HEAD (requiere {partida.tablero.head_posible.texto()})",
                        f"{tail.numero} TAIL (requiere {partida.tablero.tail_posible.texto()})"
                    ]
                
                if casillas_libres:
                    seleccion_casilla = st.selectbox("Elige casilla:", opciones_casillas)
                    idx_casilla = opciones_casillas.index(seleccion_casilla)
                    casilla = casillas_libres[idx_casilla]
                    
                    if st.button("✅ Colocar ficha", type="primary"):
                        # Verificar orientación
                        if ficha.orientacion != casilla.orientacion:
                            agregar_mensaje(f"❌ La ficha es {ficha.orientacion} pero la casilla es {casilla.orientacion}", "error")
                        else:
                            exito = partida.jugar_ficha(ficha, casilla)
                            if exito:
                                agregar_mensaje(f"✅ Ficha colocada en casilla {casilla.numero}", "success")
                                if partida.jugador_gano():
                                    agregar_mensaje(f"🎉🎉🎉 ¡{jugador.nombre} GANÓ!", "success")
                                    partida.terminada = True
                                    partida.ganador = jugador
                            else:
                                agregar_mensaje("❌ La ficha no encaja en esa casilla", "error")
                        st.rerun()
            else:
                st.warning("No tienes fichas")
            
            # Mostrar extremos DEBAJO de todo
            st.divider()
            st.subheader("🔢 Extremos")
            
            if not partida.tablero.primera_jugada:
                # TAIL a la izquierda, HEAD a la derecha
                col_tail, col_head = st.columns(2)
                with col_tail:
                    st.metric("⬅️ TAIL", partida.tablero.tail_posible.texto())
                with col_head:
                    st.metric("HEAD ➡️", partida.tablero.head_posible.texto())
            else:
                st.info("🎯 Primera jugada - coloca donde quieras")
        
        else:
            # Partida terminada
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