"""
Carga y procesamiento del archivo JSON del Bhagavad Gita.
"""

import json
import os
import streamlit as st
import logging

logger = logging.getLogger(__name__)

def cargar_bhagavad_gita(path="bhagavad_gita.json"):
    paths_prioritarios = [
        "bhagavad_gita_txt_corregido.json",
        "bhagavad_gita_txt.json",
        "bhagavad_gita_mejorado.json",
        "bhagavad_gita_epub.json",
        "bhagavad_gita.json"
    ]

    archivo_usado = None
    for p in paths_prioritarios:
        if os.path.exists(p):
            archivo_usado = p
            break

    if not archivo_usado and os.path.exists("Bhagavad-Gita-Anonimo.txt"):
        st.info("🔄 Procesando el Bhagavad Gita por primera vez...")
        try:
            from procesado_bhagavad_gita_txt_corregido import procesar_bhagavad_gita_txt
            resultado = procesar_bhagavad_gita_txt("Bhagavad-Gita-Anonimo.txt", "bhagavad_gita_txt_corregido.json")
            if resultado and os.path.exists("bhagavad_gita_txt_corregido.json"):
                archivo_usado = "bhagavad_gita_txt_corregido.json"
                st.success("✅ Bhagavad Gita procesado correctamente")
                st.rerun()
            else:
                st.error("❌ No se pudo crear el archivo JSON del Bhagavad Gita")
        except Exception as e:
            st.error(f"❌ Error procesando el Bhagavad Gita: {e}")

    if not archivo_usado:
        st.error("❌ Error: No se encontró ningún archivo del Bhagavad Gita")
        st.stop()

    try:
        with open(archivo_usado, "r", encoding="utf-8") as f:
            bhagavad_gita = json.load(f)
        logger.info(f"Bhagavad Gita cargado desde {archivo_usado}")
        return bhagavad_gita
    except json.JSONDecodeError as e:
        st.error(f"Error al decodificar JSON en {archivo_usado}: {e}")
        st.stop()
