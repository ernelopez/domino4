# streamlit_app.py

import streamlit as st
import subprocess
import sys

def ejecutar_main():
    """Ejecuta main.py y captura su salida"""
    try:
        result = subprocess.run(
            [sys.executable, "main.py"],
            capture_output=True,
            text=True,
            timeout=30  # Límite por seguridad
        )
        return result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return "⏰ Tiempo de ejecución agotado", ""

def main():
    st.set_page_config(page_title="Test Dominó", layout="wide")
    
    st.title("🎲 Test de Dominó de Fracciones")
    st.markdown("Ejecuta el juego automáticamente y muestra la salida")
    
    if st.button("▶️ Ejecutar main.py"):
        with st.spinner("Ejecutando..."):
            stdout, stderr = ejecutar_main()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📤 Salida estándar")
            if stdout:
                st.code(stdout, language="text")
            else:
                st.info("No hay salida estándar")
        
        with col2:
            st.subheader("⚠️ Errores")
            if stderr:
                st.code(stderr, language="text", line_numbers=True)
            else:
                st.success("✅ Sin errores")
        
        # Opción de descargar
        if stdout:
            st.download_button(
                label="📥 Descargar salida",
                data=stdout,
                file_name="salida_domino.txt",
                mime="text/plain"
            )

if __name__ == "__main__":
    main()