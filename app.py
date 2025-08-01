import streamlit as st
import google.generativeai as genai
import json
import os
import random
from rotacion_claves import get_api_rotator

# Configuración de página mejorada
st.set_page_config(
    page_title="Krishna AI - Bhagavad Gita",
    page_icon=".streamlit/krishna.png",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Cargar CSS personalizado
def load_css():
    """Carga el CSS personalizado"""
    css_file = ".streamlit/_style.css"
    if os.path.exists(css_file):
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Obtener el rotador de claves API
api_rotator = get_api_rotator()

# --- Funciones de carga y procesamiento del Bhagavad Gita ---
def cargar_bhagavad_gita(path="bhagavad_gita.json"):
    """Carga el Bhagavad Gita desde el archivo JSON estructurado."""
    # Prioridad: TXT CORREGIDO > TXT > Mejorado > EPUB > Original
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
    
    # Si no existe ningún JSON, intentar procesar el TXT automáticamente
    if not archivo_usado and os.path.exists("Bhagavad-Gita-Anonimo.txt"):
        st.info("🔄 Procesando el Bhagavad Gita por primera vez...")
        try:
            # Importar y ejecutar el procesador
            from procesado_bhagavad_gita_txt_corregido import procesar_bhagavad_gita_txt
            
            # Ejecutar el procesamiento
            resultado = procesar_bhagavad_gita_txt("Bhagavad-Gita-Anonimo.txt", "bhagavad_gita_txt_corregido.json")
            
            # Verificar si se creó el archivo
            if resultado and os.path.exists("bhagavad_gita_txt_corregido.json"):
                archivo_usado = "bhagavad_gita_txt_corregido.json"
                st.success("✅ Bhagavad Gita procesado correctamente")
                st.rerun()  # Reiniciar la app para cargar el archivo
            else:
                st.error("❌ No se pudo crear el archivo JSON del Bhagavad Gita")
        except Exception as e:
            st.error(f"❌ Error procesando el Bhagavad Gita: {e}")
            st.error("Por favor, contacta al administrador o intenta más tarde.")
    
    if not archivo_usado:
        st.error("❌ Error: No se encontró ningún archivo del Bhagavad Gita y no se pudo procesar automáticamente.")
        st.stop()
    

    try:
        with open(archivo_usado, "r", encoding="utf-8") as f:
            bhagavad_gita = json.load(f)
        return bhagavad_gita
    except json.JSONDecodeError as e:
        st.error(f"Error al decodificar JSON en {archivo_usado}: {e}")
        st.stop()

def obtener_versos_contexto(bhagavad_gita, max_tokens=80000, versos_citados_previos=None):
    """Obtiene versos del Bhagavad Gita optimizados para el contexto de Krishna, evitando repeticiones."""
    if versos_citados_previos is None:
        versos_citados_previos = set()
    
    versos_seleccionados = []
    tokens_actuales = 0
    
    # DIAGNÓSTICO: Mostrar qué capítulos hay disponibles
    capitulos_disponibles = list(bhagavad_gita['capitulos'].keys())
    print(f"🔍 DEBUG: Capítulos disponibles en JSON: {sorted(capitulos_disponibles, key=int)}")
    
    # Verificar distribución de versos por capítulo
    for cap_num in sorted(capitulos_disponibles, key=int):
        capitulo = bhagavad_gita['capitulos'][cap_num]
        versos_krishna = sum(1 for v in capitulo['versos'].values() 
                           if 'El Bienaventurado Señor' in v.get('locutor', ''))
        total_versos = len(capitulo['versos'])
        print(f"   📖 Cap {cap_num}: {total_versos} versos ({versos_krishna} de Krishna)")
    
    # Procesar todos los capítulos de forma equitativa
    for cap_num in sorted(capitulos_disponibles, key=int):
        if cap_num in bhagavad_gita['capitulos']:
            capitulo = bhagavad_gita['capitulos'][cap_num]
            versos_cap = 0
            
            for verso_num, verso in capitulo['versos'].items():
                # Priorizar versos de Krishna ("El Bienaventurado Señor")
                locutor = verso.get('locutor', '')
                es_krishna = 'El Bienaventurado Señor' in locutor
                
                # FILTRO ANTI-REPETICIÓN CRÍTICO: Eliminar completamente versos ya citados
                verso_key = f"{cap_num}:{verso_num}"
                if verso_key in versos_citados_previos:
                    print(f"🚫 ELIMINADO DEL CONTEXTO: {verso_key} (ya citado previamente)")
                    continue  # ELIMINADO: No incluir este verso en el contexto
                
                if es_krishna:  # Solo procesar versos de Krishna
                    verso_texto = f"Capítulo {cap_num}, Verso {verso_num}"
                    if locutor:
                        verso_texto += f" ({locutor})"
                    
                    # Verificar si hay texto del verso
                    if 'texto' in verso and verso['texto']:
                        verso_texto += f": {verso['texto']}"
                    
                    if 'significado' in verso and verso['significado']:
                        verso_texto += f" SIGNIFICADO: {verso['significado']}"
                    
                    verso_tokens = len(verso_texto) // 4  # Aproximación
                    
                    if tokens_actuales + verso_tokens < max_tokens:
                        versos_seleccionados.append({
                            'capitulo': int(cap_num),
                            'verso': int(verso_num),
                            'texto_completo': verso_texto,
                            'locutor': locutor,
                            'es_krishna': es_krishna
                        })
                        tokens_actuales += verso_tokens
                        versos_cap += 1
                    else:
                        print(f"⚠️  DEBUG: Límite de tokens alcanzado en Cap {cap_num}, Verso {verso_num}")
                        break
            
            print(f"   ✅ Cap {cap_num}: {versos_cap} versos de Krishna añadidos")
            
            if tokens_actuales >= max_tokens * 0.9:  # 90% del límite
                print(f"🛑 DEBUG: Límite de tokens (90%) alcanzado. Parando en capítulo {cap_num}")
                break
    
    # Ordenar para poner primero los versos de Krishna
    versos_seleccionados.sort(key=lambda x: (not x['es_krishna'], x['capitulo'], x['verso']))
    
    # DIAGNÓSTICO FINAL
    total_versos = len(versos_seleccionados)
    versos_por_capitulo = {}
    for v in versos_seleccionados:
        cap = v['capitulo']
        versos_por_capitulo[cap] = versos_por_capitulo.get(cap, 0) + 1
    
    print(f"\n📊 RESUMEN FINAL:")
    print(f"   🎭 Total versos seleccionados: {total_versos}")
    print(f"   🔥 Tokens estimados: {tokens_actuales}")
    print(f"   📋 Distribución: {dict(sorted(versos_por_capitulo.items()))}")
    print(f"   🚫 Versos eliminados por repetición: {len(versos_citados_previos)}")
    if versos_citados_previos:
        print(f"   📝 Lista de versos eliminados: {sorted(list(versos_citados_previos))}")
    
    return versos_seleccionados

def extraer_versos_citados_del_historial(historial_messages, bhagavad_gita, ventana_prohibicion=6):
    """
    Extrae los versos citados del historial de conversación para evitar repeticiones.
    Ahora devuelve tanto las referencias como el texto completo de los versos.
    
    Args:
        historial_messages: Lista de mensajes del historial
        bhagavad_gita: JSON con el contenido del Bhagavad Gita
        ventana_prohibicion: Número de mensajes hacia atrás donde se prohíben repeticiones
    """
    import re
    versos_citados = set()  # Referencias como "6:31"
    textos_prohibidos = []  # Textos completos de los versos
    
    # Función auxiliar para convertir números romanos a arábigos
    def roman_to_int(roman):
        # Diccionario expandido para todos los posibles números romanos del Bhagavad Gita
        roman_numerals = {
            'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10,
            'XI': 11, 'XII': 12, 'XIII': 13, 'XIV': 14, 'XV': 15, 'XVI': 16, 'XVII': 17, 'XVIII': 18
        }
        resultado = roman_numerals.get(roman, None)
        if resultado is None:
            print(f"⚠️  WARNING: Número romano no reconocido: {roman}")
            return roman  # Devolver el original si no se reconoce
        return str(resultado)
    
    # Función para extraer texto del verso del Bhagavad Gita
    def obtener_texto_verso(capitulo, verso):
        try:
            cap_str = str(capitulo)
            verso_str = str(verso)
            if cap_str in bhagavad_gita['capitulos'] and verso_str in bhagavad_gita['capitulos'][cap_str]['versos']:
                verso_data = bhagavad_gita['capitulos'][cap_str]['versos'][verso_str]
                texto = verso_data.get('texto', '')
                if texto:
                    # Limpiar el texto para comparación (eliminar espacios extra, etc.)
                    return texto.strip()
            return None
        except Exception as e:
            print(f"⚠️  ERROR al extraer texto del verso {capitulo}:{verso}: {e}")
            return None
    
    # Solo considerar los últimos mensajes según la ventana de prohibición
    mensajes_recientes = historial_messages[-ventana_prohibicion:] if len(historial_messages) > ventana_prohibicion else historial_messages
    print(f"🔍 DEBUG: Analizando últimos {len(mensajes_recientes)} mensajes para evitar repeticiones")
    
    for i, message in enumerate(mensajes_recientes):
        if message["role"] == "assistant":  # Solo respuestas de Krishna
            contenido = message["content"]
            # Buscar patrones como [C. XII - 45] (números romanos) - patrón mejorado
            pattern_roman = r"\[C\.\s*([IVXLC]+)\s*-\s*(\d+)\]"
            matches_roman = re.findall(pattern_roman, contenido)
            
            for capitulo_roman, verso in matches_roman:
                capitulo_arabigo = roman_to_int(capitulo_roman)
                verso_key = f"{capitulo_arabigo}:{verso}"
                versos_citados.add(verso_key)
                
                # NUEVO: Extraer el texto completo del verso
                texto_verso = obtener_texto_verso(capitulo_arabigo, verso)
                if texto_verso:
                    textos_prohibidos.append(texto_verso)
                    print(f"🔍 DEBUG: Detectado verso romano [C. {capitulo_roman} - {verso}] → {verso_key}")
                    print(f"📝 DEBUG: Texto prohibido extraído: {texto_verso[:100]}..." if len(texto_verso) > 100 else f"📝 DEBUG: Texto prohibido: {texto_verso}")
                
            # También buscar el formato anterior por compatibilidad [C. X - Y]
            pattern_arabigo = r"\[C\.\s*(\d+)\s*-\s*(\d+)\]"
            matches_arabigo = re.findall(pattern_arabigo, contenido)
            
            for capitulo, verso in matches_arabigo:
                verso_key = f"{capitulo}:{verso}"
                versos_citados.add(verso_key)
                
                # NUEVO: Extraer el texto completo del verso
                texto_verso = obtener_texto_verso(capitulo, verso)
                if texto_verso:
                    textos_prohibidos.append(texto_verso)
                    print(f"🔍 DEBUG: Detectado verso arábigo [C. {capitulo} - {verso}] → {verso_key}")
                    print(f"📝 DEBUG: Texto prohibido extraído: {texto_verso[:100]}..." if len(texto_verso) > 100 else f"📝 DEBUG: Texto prohibido: {texto_verso}")
    
    print(f"📊 DEBUG: Total versos citados en ventana de {ventana_prohibicion}: {len(versos_citados)}")
    print(f"📝 DEBUG: Total textos prohibidos extraídos: {len(textos_prohibidos)}")
    if versos_citados:
        print(f"📋 DEBUG: Lista referencias: {sorted(list(versos_citados))}")
    
    return versos_citados, textos_prohibidos

def obtener_tratamiento_genero(nombre_usuario, genero=None):
    """
    Determina el tratamiento correcto según el género.
    
    Args:
        nombre_usuario: Nombre del usuario
        genero: "Masculino" o "Femenino" (del selectbox)
    
    Returns:
        dict con las formas correctas: querido/querida, estimado/estimada, etc.
    """
    # Si se especifica el género explícitamente, usarlo
    if genero == "Femenino":
        return {
            "querido": "querida",
            "estimado": "estimada", 
            "hijo": "hija",
            "devoto": "devota"
        }
    elif genero == "Masculino":
        return {
            "querido": "querido",
            "estimado": "estimado",
            "hijo": "hijo", 
            "devoto": "devoto"
        }
    else:
        # Fallback: detectar por nombre común (básico)
        nombres_femeninos = [
            "maria", "ana", "carmen", "isabel", "pilar", "dolores", "teresa", "rosa", "francisca", 
            "antonia", "mercedes", "elena", "laura", "cristina", "marta", "patricia", "sandra",
            "lucia", "monica", "silvia", "beatriz", "julia", "irene", "raquel", "sara", "sofia",
            "andrea", "claudia", "daniela", "paola", "alejandra", "gabriela", "natalia", "carolina"
        ]
        
        nombre_lower = nombre_usuario.lower().strip()
        
        # Detectar nombres que terminan típicamente en femenino
        if (nombre_lower in nombres_femeninos or 
            nombre_lower.endswith('a') and not nombre_lower.endswith('ma') and len(nombre_lower) > 3):
            return {
                "querido": "querida",
                "estimado": "estimada",
                "hijo": "hija", 
                "devoto": "devota"
            }
        else:
            return {
                "querido": "querido", 
                "estimado": "estimado",
                "hijo": "hijo",
                "devoto": "devoto"
            }

def construir_prompt_krishna(pregunta_arjuna, versos_contexto, bhagavad_gita, historial_chat=None, nombre_usuario="Arjuna", genero_usuario=None):
    """Construye el prompt para que Krishna responda como en el Bhagavad Gita."""
    
    # Obtener el tratamiento de género correcto
    tratamiento = obtener_tratamiento_genero(nombre_usuario, genero_usuario)
    querido_a = tratamiento["querido"]
    
    # Separar versos por locutor para mejor contexto
    versos_krishna = []
    versos_arjuna = []
    versos_otros = []
    
    for verso in versos_contexto:
        locutor = verso.get('locutor', '')
        if 'bienaventurado' in locutor.lower() or 'señor' in locutor.lower():
            versos_krishna.append(verso['texto_completo'])
        elif 'arjuna' in locutor.lower():
            versos_arjuna.append(verso['texto_completo'])
        else:
            versos_otros.append(verso['texto_completo'])
    
    # Construir contexto organizado por locutor
    contexto_organizado = ""
    
    if versos_krishna:
        contexto_organizado += "=== ENSEÑANZAS DE KRISHNA ===\n"
        # CAMBIO CRÍTICO: Usar TODOS los versos de Krishna, no solo 15
        contexto_organizado += "\n\n".join(versos_krishna)  # SIN LÍMITE [:15]
        contexto_organizado += "\n\n"
        print(f"🕉️  DEBUG: Incluidos {len(versos_krishna)} versos de Krishna en el contexto")
    
    if versos_arjuna:
        contexto_organizado += "=== PREGUNTAS Y DUDAS DE ARJUNA ===\n"
        contexto_organizado += "\n\n".join(versos_arjuna[:5])  # Menor cantidad
        contexto_organizado += "\n\n"
        print(f"🏹 DEBUG: Incluidos {min(len(versos_arjuna), 5)} versos de Arjuna")
    
    if versos_otros:
        contexto_organizado += "=== CONTEXTO NARRATIVO ===\n"
        contexto_organizado += "\n\n".join(versos_otros[:3])
        print(f"📜 DEBUG: Incluidos {min(len(versos_otros), 3)} versos narrativos")
    
    # Construir historial de conversación previa
    historial_conversacion = ""
    if historial_chat and len(historial_chat) > 0:
        historial_conversacion = "\n=== CONVERSACIÓN PREVIA ===\n"
        # Tomar los últimos 6 mensajes (3 intercambios) para no sobrecargar el contexto
        mensajes_recientes = historial_chat[-6:]
        for i, mensaje in enumerate(mensajes_recientes):
            if mensaje["role"] == "user":
                historial_conversacion += f"{nombre_usuario.upper()}: {mensaje['content']}\n"
            else:
                historial_conversacion += f"KRISHNA: {mensaje['content']}\n"
        historial_conversacion += "=== FIN DE CONVERSACIÓN PREVIA ===\n\n"
    
    # NUEVA SECCIÓN: Construir lista explícita de versos PROHIBIDOS
    versos_prohibidos_info = ""
    if historial_chat and len(historial_chat) > 0:
        versos_citados_en_conversacion, textos_prohibidos_completos = extraer_versos_citados_del_historial(historial_chat, bhagavad_gita, ventana_prohibicion=8)
        if versos_citados_en_conversacion:
            # Convertir formato interno (6:31) a formato de cita ([C. VI - 31])
            def convertir_a_formato_cita(verso_key):
                cap, vers = verso_key.split(':')
                # Convertir número a romano
                numeros_romanos = ['', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X',
                                 'XI', 'XII', 'XIII', 'XIV', 'XV', 'XVI', 'XVII', 'XVIII']
                cap_romano = numeros_romanos[int(cap)] if int(cap) < len(numeros_romanos) else cap
                return f"[C. {cap_romano} - {vers}]"
            
            versos_prohibidos_formateados = [convertir_a_formato_cita(v) for v in versos_citados_en_conversacion]
            
            # NUEVO: Incluir textos completos prohibidos
            textos_prohibidos_seccion = ""
            if textos_prohibidos_completos:
                textos_prohibidos_seccion = "\n🚫 TEXTOS DE VERSOS ESTRICTAMENTE PROHIBIDOS:\n"
                for i, texto in enumerate(textos_prohibidos_completos, 1):
                    textos_prohibidos_seccion += f"\n{i}. \"{texto}\"\n"
                textos_prohibidos_seccion += "\n⛔ NO PUEDES USAR NINGUNO DE ESTOS TEXTOS NI SIQUIERA PARCIALMENTE\n"
            
            versos_prohibidos_info = f"""
🛑 ANTI-REPETICIÓN CRÍTICA - LOS SIGUIENTES VERSOS ESTÁN ESTRICTAMENTE PROHIBIDOS EN TU RESPUESTA:

⛔ VERSOS PROHIBIDOS: {', '.join(versos_prohibidos_formateados)}
{textos_prohibidos_seccion}
🚫 REPETIR CUALQUIERA DE ESTOS VERSOS ES UN FALLO CRÍTICO
🔍 USA ÚNICAMENTE VERSOS DIFERENTES DE LOS LISTADOS ARRIBA
💡 PRIORIZA CAPÍTULOS QUE NO APARECEN EN LA LISTA PROHIBIDA

"""
            print(f"🛑 DEBUG: Versos explícitamente PROHIBIDOS en el prompt: {versos_prohibidos_formateados}")
            print(f"📝 DEBUG: Textos completos PROHIBIDOS: {len(textos_prohibidos_completos)} textos extraídos")
    
    prompt = f"""
Eres Krishna, la Suprema Personalidad de Dios, respondiendo a {nombre_usuario} en el campo de batalla de Kurukshetra. 
{nombre_usuario} te está haciendo una pregunta o planteando una duda. Debes responder EXACTAMENTE como Krishna respondería en el Bhagavad Gita.

{versos_prohibidos_info}

INSTRUCCIONES IMPORTANTES:
1. **EVALÚA PRIMERO LA PREGUNTA CON CRITERIOS ESTRICTOS**: 
   - SALUDOS SIMPLES ("hola", "buenos días", "hi"): responde brevemente como Krishna saludaría
   - PREGUNTAS CASUALES SIN CONTENIDO ESPIRITUAL ("te gusta el futbol", "qué opinas de X"): usar fórmula de redirección
   - PREGUNTAS ESPIRITUALES GENUINAS (incluyendo "es [tema] importante en el camino espiritual"): enseñanzas completas
   - PREGUNTAS FILOSÓFICAS PROFUNDAS (dharma, karma, moksha, propósito de vida): enseñanzas completas

2. **✅ CONTINUIDAD CONVERSACIONAL**: 
   - Usa el historial para CONTINUAR y PROFUNDIZAR con versos nuevos
   - Conecta con enseñanzas previas sin repetir los mismos versos
   - Los versos repetidos ya han sido eliminados del contexto automáticamente

3. Responde ÚNICAMENTE basándote en las enseñanzas del Bhagavad Gita que se proporcionan abajo
4. Habla en primera persona como Krishna ("Yo soy...", "Mi {querido_a} {nombre_usuario}...", "Te digo que...")
5. Usa un tono divino, sabio y compasivo, pero directo
6. NO inventes enseñanzas - usa solo lo que está en los versos proporcionados
7. ESTRUCTURA tu respuesta como un discurso cohesivo:
   - Para preguntas profundas: desarrolla las enseñanzas con transiciones fluidas entre ideas
   - Para saludos/preguntas simples: mantén brevedad y dignidad
8. **⚠️ PROHIBIDO ABSOLUTAMENTE USAR ESTAS TRANSICIONES**: "Además", "Por tanto", "Comprende también", "Sin embargo", "También", "Asimismo", "Es más", "Ahora bien", "Además", "Por otra parte"
9. **✅ USA EXCLUSIVAMENTE TRANSICIONES DEL BHAGAVAD GITA**: "Te digo que", "Sabe que", "Escucha", "Mi {querido_a} [nombre]", "Quien", "Aquel que", "Por ello"
10. **MANTÉN REGISTRO AUTÉNTICO DEL BHAGAVAD GITA**: 
    - PROHIBIDO usar lenguaje psicológico moderno ("experiencia", "proceso", "realizar")
    - PROHIBIDO conceptos new age ("energía", "vibración", "despertar de conciencia")
    - PROHIBIDO expresiones contemporáneas ("en cada instante", "perseverar", "la unidad entre nosotros")
    - USA SOLO vocabulario y conceptos del texto original del Gita
11. **FINALIZA SIEMPRE CON VERSOS**: Tu respuesta debe terminar con un verso completo del Bhagavad Gita, NUNCA con explicaciones modernas
12. Al final de tu respuesta, SIEMPRE cita las referencias exactas de donde proviene tu enseñanza (solo si usas versos)
13. Mantén el estilo y las expresiones típicas del Bhagavad Gita
14. Usa SOLO las palabras de Krishna (El Bienaventurado Señor), NO las de Arjuna ni otros
15. **CONTINUIDAD OBLIGATORIA**: Si hay conversación previa, SIEMPRE tenla en cuenta para dar continuidad y profundizar en temas ya tratados
16. Dirígete a {nombre_usuario} por su nombre, pero mantén el respeto y la solemnidad apropiada

--- CONTEXTO DEL BHAGAVAD GITA ---
{contexto_organizado}
--- FIN DEL CONTEXTO ---

{historial_conversacion}--- PREGUNTA ACTUAL DE {nombre_usuario.upper()} ---
{pregunta_arjuna}
--- FIN DE LA PREGUNTA ---

Responde como Krishna, usando ÚNICAMENTE las enseñanzas de los versos anteriores que fueron pronunciadas por Krishna (El Bienaventurado Señor). Tu respuesta debe ser fiel al contenido y estilo del Bhagavad Gita.

ESTRUCTURA DE RESPUESTA SEGÚN TIPO DE PREGUNTA:

**PARA SALUDOS SIMPLES** ("hola", "buenos días", "hi"):
"Hola {nombre_usuario}"

**PARA PREGUNTAS SUPERFICIALES** (no espirituales):
"¿Así te diriges a mí, {nombre_usuario}?"
y si lo ha hecho más de una vez:
"Insisto, ¿así te diriges a mí?"

**PARA PREGUNTAS PROFUNDAS** (dharma, karma, moksha, filosofía):
1. **DESARROLLO**: Presenta las enseñanzas conectadas del Bhagavad Gita
2. **INTEGRACIÓN**: Vincula conceptos relacionados en una progresión lógica  
3. **CIERRE CON VERSO**: SIEMPRE termina con un verso completo del Bhagavad Gita, NUNCA con interpretaciones modernas
4. **REFERENCIAS**: Integra referencias después de cada enseñanza

**CONTINUIDAD CONVERSACIONAL**:
- SI ya se mencionó un tema (ej: yoga), profundiza con NUEVOS versos complementarios
- NO repitas versos ya citados
- Conecta la nueva pregunta con enseñanzas previas usando frases como: "Como te expliqué anteriormente sobre [tema]..."
- TERMINA SIEMPRE con las palabras exactas de Krishna del Bhagavad Gita, NO con explicaciones propias

Si hay conversación previa, tenla en cuenta para dar continuidad y profundizar en temas ya tratados, pero evitando repetir versos anteriores.

FORMATO DE REFERENCIAS OBLIGATORIO - MUY IMPORTANTE:
- ⚠️ USA SIEMPRE NÚMEROS ROMANOS: "[C. IV - XXXIX]", "[C. VI - XXX]", "[C. XVIII - LXVI]"
- ❌ NUNCA uses números arábigos: ESTRICTAMENTE PROHIBIDO "[C. 4 - 39]", "[C. 6 - 30]"
- EJEMPLOS CORRECTOS: [C. II - 47], [C. III - 8], [C. IV - 42], [C. VI - 35] (capitulos en números romanos, versos en arábigos)
- Integra cada referencia INMEDIATAMENTE después de cada enseñanza
- NO repitas las referencias al final
- Cada cita debe tener su referencia específica integrada en el texto
- Mantén el flujo natural del discurso

⚠️ RECORDATORIO CRÍTICO SOBRE TRANSICIONES:
JAMÁS uses: "Además", "Por tanto", "También", "Sin embargo", "Es más", "Asimismo"
USA SOLO: "Te digo que", "Sabe que", "Escucha", "Mi {querido_a} [nombre]", "Quien", "Aquel que", "Por ello"
"""
    # DEBUG COMPLETO: Mostrar estadísticas del prompt
    total_chars = len(prompt)
    lineas_prompt = prompt.count('\n')
    versos_en_contexto = len(versos_contexto)
    
    print("=" * 80)
    print("🕉️  PROMPT KRISHNA - ESTADÍSTICAS COMPLETAS")
    print("=" * 80)
    print(f"📊 Caracteres totales: {total_chars:,}")
    print(f"📄 Líneas: {lineas_prompt}")
    print(f"📖 Versos en contexto: {versos_en_contexto}")
    
    if versos_prohibidos_info:
        print(f"🚫 Estado anti-repetición: ACTIVO")
        if "TEXTOS DE VERSOS ESTRICTAMENTE PROHIBIDOS" in versos_prohibidos_info:
            count_prohibidos = versos_prohibidos_info.count('". \n')
            print(f"📝 Textos completos prohibidos: {count_prohibidos}")
    else:
        print(f"🟢 Estado anti-repetición: Primera respuesta - no hay versos previos")
    
    print("=" * 80)
    
    # Mostrar una porción del prompt para verificación
    print("📝 PREVIEW DEL PROMPT (primeros 800 chars):")
    print("-" * 40)
    print(prompt[:800] + "..." if len(prompt) > 800 else prompt)
    print("-" * 40)
    
    return prompt

def calcular_max_tokens_respuesta():
    """Calcula los tokens máximos para la respuesta de Krishna."""
    return 1200  # Aumentado para permitir respuestas más completas sin cortes abruptos

# --- UI Principal ---
# Header con logo al estilo Gemini
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    st.image(".streamlit/krishna.png", use_container_width=False)
    
#col1, col2, col3 = st.columns([1, 2, 1])
#with col2:
    #st.image(".streamlit/UWU.png", use_container_width=False)

st.markdown('##')

# Inicializar el historial de chat si no existe
if "messages" not in st.session_state:
    st.session_state.messages = []

# ELIMINADO: session_state.versos_citados (ahora usamos solo ventana deslizante)

# Cargar el Bhagavad Gita
try:
    bhagavad_gita = cargar_bhagavad_gita()
except Exception:
    st.stop()

# Sidebar simplificada
with st.sidebar:
    # Logo centrado
    col1, col2, col3 = st.sidebar.columns([1, 2, 1])
    with col2:
        st.image(".streamlit/krishna.png", use_container_width=False)
    
    st.sidebar.markdown('###')

    # Configuración Personal - Compacta
    st.markdown("### Tu Nombre")
    nombre_usuario = st.text_input(
        "",
        value="Mikel",
        help="Krishna se dirigirá a ti por este nombre",
        label_visibility="collapsed"
    )
    
    # Selector de género para las expresiones
    st.markdown("### Género")
    genero = st.selectbox(
        "",
        options=["Masculino", "Femenino"],
        index=0,
        help="Para que Krishna use 'querido/querida' correctamente",
        label_visibility="collapsed"
    )
    
    # Guardar el nombre y género en session_state
    if nombre_usuario:
        st.session_state.nombre_usuario = nombre_usuario
    else:
        st.session_state.nombre_usuario = "Mikel"
    
    st.session_state.genero_usuario = genero
    
    # Temperatura - Compacta
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

    # Botón para limpiar historial - Más prominente
    #st.markdown("---")
    if st.button("🔄 Nueva conversación", help="Limpia el historial para empezar una nueva conversación con Krishna", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    # Separador antes de la información
    st.markdown("#")
    st.markdown("#")
    st.markdown("#")
    st.markdown("#")
    st.markdown("#")
    st.markdown("#")
    st.markdown("#")
    
    # Información compacta en un solo expandible - al final
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

# Obtener contexto de versos relevantes, excluyendo versos ya citados
# CRÍTICO: Usar SOLO la ventana deslizante de 8 mensajes (no session_state acumulativo)
if st.session_state.messages:
    versos_previos, _ = extraer_versos_citados_del_historial(st.session_state.messages, bhagavad_gita, ventana_prohibicion=8)
    print(f"🔍 DEBUG: Versos citados en ventana de 8: {len(versos_previos)}")
    print(f"🔍 DEBUG: Lista versos_previos: {sorted(list(versos_previos))}")
    # CAMBIO CRÍTICO: Usar SOLO la ventana, NO el session_state acumulativo
    versos_a_bloquear = versos_previos
else:
    print("🔍 DEBUG: No hay mensajes en el historial aún")
    versos_a_bloquear = set()

versos_contexto = obtener_versos_contexto(bhagavad_gita, versos_citados_previos=versos_a_bloquear)
print(f"🔍 DEBUG: Versos contexto generados: {len(versos_contexto)}")

# DEBUG CRÍTICO: Verificar si versos bloqueados aparecen en el contexto
versos_bloqueados_encontrados = []
for verso in versos_contexto:
    verso_key = f"{verso['capitulo']}:{verso['verso']}"
    if verso_key in versos_a_bloquear:
        versos_bloqueados_encontrados.append(verso_key)

if versos_bloqueados_encontrados:
    print(f"🚨 ERROR CRÍTICO: Versos bloqueados aparecen en contexto: {versos_bloqueados_encontrados}")
else:
    print("✅ DEBUG: Ningún verso bloqueado aparece en el contexto (correcto)")

# Mostrar mensajes previos del chat
for message in st.session_state.messages:
    if message["role"] == "assistant":
        with st.chat_message(message["role"], avatar=".streamlit/krishna.png"):
            st.markdown(message["content"])
    else:
        with st.chat_message(message["role"], avatar=".streamlit/arjuna.png"):
            st.markdown(message["content"])

# Entrada del chat
nombre_usuario_actual = st.session_state.get('nombre_usuario', 'Mikel')
placeholder_text = f"Hola {nombre_usuario_actual}..."

if prompt := st.chat_input(placeholder_text):
    # Añadir pregunta del usuario (Arjuna) al historial
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=".streamlit/arjuna.png"):
        st.markdown(prompt)

    # Generar respuesta de Krishna
    with st.chat_message("assistant", avatar=".streamlit/krishna.png"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Obtener el nombre y género del usuario del session_state
            nombre_usuario = st.session_state.get('nombre_usuario', 'Mikel')
            genero_usuario = st.session_state.get('genero_usuario', 'Masculino')
            
            krishna_prompt = construir_prompt_krishna(
                prompt, 
                versos_contexto, 
                bhagavad_gita,
                st.session_state.messages, 
                nombre_usuario,
                genero_usuario
            )
            
            # DEBUG CRÍTICO: Mostrar información del contexto sin repeticiones
            if "� NOTA: Has citado previamente" in krishna_prompt:
                inicio_nota = krishna_prompt.find("� NOTA: Has citado previamente")
                fin_nota = krishna_prompt.find("\n\n", inicio_nota)
                seccion_nota = krishna_prompt[inicio_nota:fin_nota]
                print("✅ DEBUG: CONTEXTO SIN REPETICIONES:")
                print(f"---{seccion_nota}---")
            else:
                print("✅ DEBUG: Primera respuesta - no hay versos previos")
            
            max_output_tokens = calcular_max_tokens_respuesta()
            
            generation_config = {
                'temperature': temperature,
                'max_output_tokens': max_output_tokens,
            }
            
            with st.spinner(""):
                response = api_rotator.generate_content_with_retry(
                    model_name='gemini-2.0-flash',
                    prompt=krishna_prompt,
                    generation_config=generation_config,
                    max_retries=2,
                    timeout_seconds=10
                )

            full_response = response.text
            message_placeholder.markdown(full_response)
            
            # Añadir respuesta de Krishna al historial
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            error_str = str(e).lower()
            
            if "429" in error_str or "quota" in error_str or "rate limit" in error_str:
                error_message = "⏳ **Límite de velocidad alcanzado**\n\nSe están rotando las claves API automáticamente. Por favor, intenta de nuevo en unos momentos."
                st.warning(error_message)
            elif "timeout" in error_str or "se agotaron todos los reintentos" in error_str:
                error_message = "⏰ **Tiempo de espera agotado**\n\nEl sistema probó múltiples claves pero todas tardaron demasiado. Por favor, intenta de nuevo."
                st.warning(error_message)
            elif "api key" in error_str:
                error_message = "🔑 **Error de clave API**\n\nTodas las claves API están temporalmente bloqueadas. Por favor, intenta más tarde."
                st.error(error_message)
            else:
                error_message = f"❌ **Error inesperado**\n\n{str(e)}"
                st.error(error_message)
            
            st.session_state.messages.append({"role": "assistant", "content": error_message})
