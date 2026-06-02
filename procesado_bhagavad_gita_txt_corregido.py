#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script mejorado para procesar el Bhagavad Gita desde archivo TXT
Maneja correctamente versos compuestos como "3-4", "13-19", etc.
"""

import re
import json
import os

def procesar_bhagavad_gita_txt(txt_path, output_path):
    """Procesa el archivo TXT del Bhagavad Gita y lo convierte a JSON estructurado"""
    
    print("🕉️  PROCESANDO BHAGAVAD GITA DESDE TXT")
    print("="*50)
    
    try:
        # Verificar que el archivo existe
        if not os.path.exists(txt_path):
            print(f"❌ Error: Archivo {txt_path} no encontrado")
            return False
        
        # Leer archivo
        with open(txt_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        print(f"📄 Archivo leído: {len(contenido)} caracteres")
        
        # Extraer capítulos y versos
        capitulos = extraer_capitulos_versos(contenido)
        
        if not capitulos:
            print("❌ Error: No se pudieron extraer capítulos")
            return False
        
        # Crear estructura final
        bhagavad_gita = {
            "titulo": "Bhagavad Gita",
            "traductor": "José Barrio Gutiérrez", 
            "fuente": txt_path,
            "total_capitulos": len(capitulos),
            "capitulos": capitulos
        }
        
        # Calcular estadísticas
        total_versos = sum(len(cap['versos']) for cap in capitulos.values())
        
        print(f"\n📊 ESTADÍSTICAS DE EXTRACCIÓN:")
        print(f"   📖 Capítulos procesados: {len(capitulos)}")
        print(f"   📝 Total de versos: {total_versos}")
        
        # Análisis por capítulo
        for cap_num in sorted(capitulos.keys(), key=int):
            cap = capitulos[cap_num]
            versos_krishna = sum(1 for v in cap['versos'].values() 
                               if 'El Bienaventurado Señor' in v.get('locutor', ''))
            print(f"   📖 Cap {cap_num}: {len(cap['versos'])} versos ({versos_krishna} de Krishna)")
        
        # Guardar resultado
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(bhagavad_gita, f, ensure_ascii=False, indent=2)
        
        file_size = os.path.getsize(output_path) / 1024
        print(f"\n✅ PROCESAMIENTO COMPLETADO")
        print(f"   📄 Archivo guardado: {output_path}")
        print(f"   💾 Tamaño: {file_size:.1f} KB")
        print(f"   🎯 Listo para usar con Krishna AI")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al procesar archivo: {e}")
        return False

def extraer_capitulos_versos(contenido):
    """Extrae capítulos y versos del contenido del archivo TXT"""
    print("🔍 Extrayendo capítulos, versos y locutores...")
    
    capitulos = {}
    lineas = contenido.split('\n')
    
    # Patrones para detectar capítulos y locutores
    patron_capitulo = r'Capítulo\s+([IVX]+|[\d]+)'
    patron_locutor = r'^([A-Za-zñáéíóúÑÁÉÍÓÚ\s]+)\s+dijo:'
    
    # Variables de estado
    capitulo_actual = None
    titulo_actual = ""
    locutor_actual = ""
    esperando_titulo = False
    
    for i, linea in enumerate(lineas):
        linea = linea.strip()
        
        # Buscar capítulos
        match_capitulo = re.search(patron_capitulo, linea, re.IGNORECASE)
        if match_capitulo:
            cap_num_str = match_capitulo.group(1)
            
            # Convertir números romanos a arábigos
            cap_num = convertir_romano_a_arabigo(cap_num_str)
            if cap_num is None:
                try:
                    cap_num = int(cap_num_str)
                except ValueError:
                    continue
            
            capitulo_actual = str(cap_num)
            esperando_titulo = True
            locutor_actual = ""
            
            # Extraer título del capítulo de la misma línea
            resto_linea = linea[match_capitulo.end():].strip()
            if resto_linea:
                titulo_actual = resto_linea
                esperando_titulo = False
            
            if capitulo_actual not in capitulos:
                capitulos[capitulo_actual] = {
                    'titulo': titulo_actual,
                    'versos': {}
                }
                print(f"📖 Encontrado: Capítulo {capitulo_actual}")
            
            continue
        
        # Capturar título del capítulo si estamos esperando
        if esperando_titulo and linea and not linea.isdigit():
            titulo_actual = linea
            if capitulo_actual:
                capitulos[capitulo_actual]['titulo'] = titulo_actual
            esperando_titulo = False
            continue
        
        # Buscar locutores (quien habla)
        match_locutor = re.search(patron_locutor, linea, re.IGNORECASE)
        if match_locutor:
            locutor_actual = match_locutor.group(1).strip()
            print(f"   🗣️  {locutor_actual} habla en capítulo {capitulo_actual}")
            continue
        
        # Buscar versos (números seguidos de punto, incluyendo rangos)
        if capitulo_actual and re.match(r'^\d+[\-\d]*\.', linea):
            partes = linea.split('.', 1)
            if len(partes) == 2:
                verso_num_str = partes[0].strip()
                verso_texto = partes[1].strip()
                
                # MANEJO DE VERSOS COMPUESTOS (ej: "3-4", "13-19")
                if '-' in verso_num_str:
                    rango = verso_num_str.split('-')
                    if len(rango) == 2:
                        try:
                            inicio = int(rango[0])
                            fin = int(rango[1])
                            
                            print(f"   📝 Verso compuesto {verso_num_str}: expandiendo versos {inicio}-{fin}")
                            expandir_verso_compuesto(capitulos, capitulo_actual, inicio, fin, verso_texto, locutor_actual)
                            
                        except ValueError:
                            # Si falla la conversión, tratar como verso simple
                            capitulos[capitulo_actual]['versos'][verso_num_str] = {
                                'texto': verso_texto,
                                'significado': '',
                                'locutor': locutor_actual
                            }
                else:
                    # Verso simple
                    capitulos[capitulo_actual]['versos'][verso_num_str] = {
                        'texto': verso_texto,
                        'significado': '',
                        'locutor': locutor_actual
                    }
                    print(f"   📄 Verso {verso_num_str}: {verso_texto[:50]}...")
        
        # Continuar texto de verso anterior
        elif capitulo_actual and linea and not linea.startswith('Capítulo') and not re.match(patron_locutor, linea):
            if capitulos[capitulo_actual]['versos']:
                ultimo_verso = list(capitulos[capitulo_actual]['versos'].keys())[-1]
                texto_actual = capitulos[capitulo_actual]['versos'][ultimo_verso]['texto']
                capitulos[capitulo_actual]['versos'][ultimo_verso]['texto'] = texto_actual + ' ' + linea
    
    return capitulos

def expandir_verso_compuesto(capitulos, capitulo_actual, inicio, fin, texto_completo, locutor):
    """Expande un verso compuesto (ej: 13-19) en versos individuales"""
    
    num_versos = fin - inicio + 1
    
    # Intentar dividir por frases (punto y coma, dos puntos)
    frases = re.split(r'[;:]\s*', texto_completo)
    frases = [f.strip() for f in frases if f.strip()]
    
    if len(frases) < num_versos:
        # Si no hay suficientes frases, dividir por comas
        frases = re.split(r'[,]\s*', texto_completo)
        frases = [f.strip() for f in frases if f.strip()]
    
    if len(frases) >= num_versos:
        # Distribuir frases entre versos
        frases_por_verso = len(frases) // num_versos
        resto_frases = len(frases) % num_versos
        
        idx_frase = 0
        for j in range(num_versos):
            verso_individual = str(inicio + j)
            
            # Calcular frases para este verso
            frases_este_verso = frases_por_verso
            if j < resto_frases:
                frases_este_verso += 1
            
            # Tomar las frases correspondientes
            if frases_este_verso > 0:
                texto_verso = '; '.join(frases[idx_frase:idx_frase + frases_este_verso])
            else:
                texto_verso = ""
            
            capitulos[capitulo_actual]['versos'][verso_individual] = {
                'texto': texto_verso.strip(),
                'significado': '',
                'locutor': locutor
            }
            
            idx_frase += frases_este_verso
            print(f"      📄 Verso {verso_individual}: {texto_verso[:50]}...")
    else:
        # Si no hay suficientes frases, dividir equitativamente por palabras
        palabras = texto_completo.split()
        palabras_por_verso = len(palabras) // num_versos
        resto_palabras = len(palabras) % num_versos
        
        idx_palabra = 0
        for j in range(num_versos):
            verso_individual = str(inicio + j)
            
            # Calcular palabras para este verso
            palabras_este_verso = palabras_por_verso
            if j < resto_palabras:
                palabras_este_verso += 1
            
            # Tomar las palabras correspondientes
            if palabras_este_verso > 0:
                texto_verso = ' '.join(palabras[idx_palabra:idx_palabra + palabras_este_verso])
            else:
                texto_verso = ""
            
            capitulos[capitulo_actual]['versos'][verso_individual] = {
                'texto': texto_verso.strip(),
                'significado': '',
                'locutor': locutor
            }
            
            idx_palabra += palabras_este_verso
            print(f"      📄 Verso {verso_individual}: {texto_verso[:50]}...")

def convertir_romano_a_arabigo(romano):
    if not romano:
        return None
    valores = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    try:
        total = 0
        i = 0
        romano = romano.upper()
        
        while i < len(romano):
            if i + 1 < len(romano) and valores[romano[i]] < valores[romano[i + 1]]:
                total += valores[romano[i + 1]] - valores[romano[i]]
                i += 2
            else:
                total += valores[romano[i]]
                i += 1
        
        return total
    except (KeyError, IndexError):
        return None

if __name__ == "__main__":
    txt_path = "Bhagavad-Gita-Anonimo.txt"
    output_path = "bhagavad_gita_txt_corregido.json"
    
    if procesar_bhagavad_gita_txt(txt_path, output_path):
        print("\n🎉 ¡Procesamiento exitoso!")
        print("✅ El archivo está listo para usar con Krishna AI")
        print(f"📁 Generado: {output_path}")
    else:
        print("\n❌ Error en el procesamiento")
        print("🔧 Verifica el archivo TXT y vuelve a intentarlo")
