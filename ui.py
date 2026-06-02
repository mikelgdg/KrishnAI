"""
Componentes de UI para Krishna AI.
"""

import os
import streamlit as st
import logging

logger = logging.getLogger(__name__)

def load_css():
    css_file = ".streamlit/_style.css"
    if os.path.exists(css_file):
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def render_sidebar(bhagavad_gita, api_rotator):
    with st.sidebar:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(".streamlit/krishna.png", use_container_width=False)

        st.markdown('###')

        st.markdown("### Nombre")
        nombre_usuario = st.text_input(
            "",
            value=st.session_state.get('nombre_usuario', 'Mikel'),
            help="Krishna se dirigirá a ti por este nombre",
            label_visibility="collapsed",
            key="nombre_input"
        )

        if nombre_usuario and nombre_usuario != st.session_state.get('ultimo_nombre_procesado', ''):
            from gender_detector import obtener_tratamiento_genero
            tratamiento_temp = obtener_tratamiento_genero(nombre_usuario, None, api_rotator)
            genero_detectado = "Femenino" if tratamiento_temp["querido"] == "querida" else "Masculino"
            st.session_state.genero_detectado = genero_detectado
            st.session_state.ultimo_nombre_procesado = nombre_usuario
        elif 'genero_detectado' not in st.session_state:
            st.session_state.genero_detectado = "Masculino"

        if nombre_usuario:
            st.session_state.nombre_usuario = nombre_usuario
        else:
            st.session_state.nombre_usuario = "Mikel"

        st.session_state.genero_usuario = st.session_state.get('genero_detectado', 'Masculino')

        st.markdown("### Creatividad")
        temperature = st.slider(
            "",
            min_value=0.0,
            max_value=0.8,
            value=0.1,
            step=0.05,
            help="Controla la creatividad. Valores bajos mantienen mayor fidelidad al texto original.",
            label_visibility="collapsed"
        )

        if st.button("🔄 Nueva conversación", help="Limpia el historial para empezar una nueva conversación con Krishna", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        st.markdown("#\n" * 7)

        with st.expander("ℹ️ Información", expanded=False):
            nombre_mostrar = st.session_state.get('nombre_usuario', 'Mikel')
            st.markdown(f"""
            **Krishna AI** te permite dialogar directamente con Krishna del Bhagavad Gita.
            
            Eres **{nombre_mostrar}** en Kurukshetra, y Krishna responderá con las enseñanzas exactas del Gita.
            
            **Uso:**
            - Haz preguntas profundas sobre dharma, karma, moksha
            - Krishna recuerda los últimos intercambios
            - Todas las respuestas incluyen referencias exactas
            
            **Datos del Gita:**
            - Capítulos: {len(bhagavad_gita['capitulos'])}
            - Versos: {sum(len(cap['versos']) for cap in bhagavad_gita['capitulos'].values())}
            - Traductor: {bhagavad_gita['traductor']}
            
            **API:** {api_rotator.get_status_summary()['available_keys']}/{api_rotator.get_status_summary()['total_keys']} claves disponibles
            """)

    return temperature
