#!/usr/bin/env python3
"""
Script para generar automáticamente el archivo del Bhagavad Gita
Se ejecuta automáticamente en Streamlit Cloud si no existe el JSON
"""

import os
import sys

def setup_bhagavad_gita():
    """Configura el archivo del Bhagavad Gita si no existe"""
    
    # Verificar si ya existe el archivo JSON
    json_files = [
        "bhagavad_gita_txt_corregido.json",
        "bhagavad_gita_txt.json", 
        "bhagavad_gita.json"
    ]
    
    for json_file in json_files:
        if os.path.exists(json_file):
            print(f"✅ Archivo del Gita encontrado: {json_file}")
            return True
    
    # Si no existe ningún JSON, intentar procesar el TXT
    if os.path.exists("Bhagavad-Gita-Anonimo.txt"):
        print("📖 Procesando Bhagavad-Gita-Anonimo.txt...")
        try:
            # Importar y ejecutar el procesador
            from procesado_bhagavad_gita_txt_corregido import main
            main()
            print("✅ Bhagavad Gita procesado correctamente")
            return True
        except Exception as e:
            print(f"❌ Error procesando el Gita: {e}")
            return False
    else:
        print("❌ No se encuentra el archivo Bhagavad-Gita-Anonimo.txt")
        return False

if __name__ == "__main__":
    setup_bhagavad_gita()
