"""
Construcción del prompt de Krishna con contexto del Bhagavad Gita
y sistema anti-repetición.
"""

import re
import logging

logger = logging.getLogger(__name__)

NUMEROS_ROMANOS = ['', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X',
                   'XI', 'XII', 'XIII', 'XIV', 'XV', 'XVI', 'XVII', 'XVIII']

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

def extraer_versos_citados_del_historial(historial_messages, bhagavad_gita, ventana_prohibicion=6):
    import re
    versos_citados = set()
    textos_prohibidos = []

    def obtener_texto_verso(capitulo, verso):
        try:
            cap_str = str(capitulo)
            verso_str = str(verso)
            if cap_str in bhagavad_gita['capitulos'] and verso_str in bhagavad_gita['capitulos'][cap_str]['versos']:
                texto = bhagavad_gita['capitulos'][cap_str]['versos'][verso_str].get('texto', '')
                return texto.strip() if texto else None
            return None
        except Exception:
            return None

    mensajes_recientes = historial_messages[-ventana_prohibicion:] if len(historial_messages) > ventana_prohibicion else historial_messages
    logger.info(f"Analizando últimos {len(mensajes_recientes)} mensajes para evitar repeticiones")

    for message in mensajes_recientes:
        if message["role"] == "assistant":
            contenido = message["content"]
            pattern_roman = r"\[C\.\s*([IVXLC]+)\s*-\s*(\d+)\]"
            matches_roman = re.findall(pattern_roman, contenido)
            for capitulo_roman, verso in matches_roman:
                capitulo_arabigo = convertir_romano_a_arabigo(capitulo_roman)
                if capitulo_arabigo is None:
                    roman_map = {'I':1,'II':2,'III':3,'IV':4,'V':5,'VI':6,'VII':7,'VIII':8,'IX':9,'X':10,
                                 'XI':11,'XII':12,'XIII':13,'XIV':14,'XV':15,'XVI':16,'XVII':17,'XVIII':18}
                    capitulo_arabigo = roman_map.get(capitulo_roman)
                if capitulo_arabigo:
                    verso_key = f"{capitulo_arabigo}:{verso}"
                    versos_citados.add(verso_key)
                    texto_verso = obtener_texto_verso(capitulo_arabigo, verso)
                    if texto_verso:
                        textos_prohibidos.append(texto_verso)
                        logger.info(f"Detectado verso [C. {capitulo_roman} - {verso}] → {verso_key}")

            pattern_arabigo = r"\[C\.\s*(\d+)\s*-\s*(\d+)\]"
            matches_arabigo = re.findall(pattern_arabigo, contenido)
            for capitulo, verso in matches_arabigo:
                verso_key = f"{capitulo}:{verso}"
                versos_citados.add(verso_key)
                texto_verso = obtener_texto_verso(capitulo, verso)
                if texto_verso:
                    textos_prohibidos.append(texto_verso)
                    logger.info(f"Detectado verso [C. {capitulo} - {verso}] → {verso_key}")

    logger.info(f"Total versos citados: {len(versos_citados)}, textos prohibidos: {len(textos_prohibidos)}")
    return versos_citados, textos_prohibidos

def construir_prompt_krishna(pregunta_arjuna, versos_contexto, bhagavad_gita,
                              historial_chat=None, nombre_usuario="Arjuna",
                              genero_usuario=None, api_rotator=None):
    from gender_detector import obtener_tratamiento_genero
    tratamiento = obtener_tratamiento_genero(nombre_usuario, genero_usuario, api_rotator)
    querido_a = tratamiento["querido"]

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

    contexto_organizado = ""
    if versos_krishna:
        contexto_organizado += "=== ENSEÑANZAS DE KRISHNA ===\n"
        contexto_organizado += "\n\n".join(versos_krishna) + "\n\n"
        logger.info(f"Incluidos {len(versos_krishna)} versos de Krishna en el contexto")
    if versos_arjuna:
        contexto_organizado += "=== PREGUNTAS Y DUDAS DE ARJUNA ===\n"
        contexto_organizado += "\n\n".join(versos_arjuna[:5]) + "\n\n"
    if versos_otros:
        contexto_organizado += "=== CONTEXTO NARRATIVO ===\n"
        contexto_organizado += "\n\n".join(versos_otros[:3])

    historial_conversacion = ""
    if historial_chat and len(historial_chat) > 0:
        historial_conversacion = "\n=== CONVERSACIÓN PREVIA ===\n"
        mensajes_recientes = historial_chat[-6:]
        for msg in mensajes_recientes:
            if msg["role"] == "user":
                historial_conversacion += f"{nombre_usuario.upper()}: {msg['content']}\n"
            else:
                historial_conversacion += f"KRISHNA: {msg['content']}\n"
        historial_conversacion += "=== FIN DE CONVERSACIÓN PREVIA ===\n\n"

    versos_prohibidos_info = ""
    if historial_chat and len(historial_chat) > 0:
        versos_citados_en_conversacion, textos_prohibidos_completos = extraer_versos_citados_del_historial(
            historial_chat, bhagavad_gita, ventana_prohibicion=8)
        if versos_citados_en_conversacion:
            def convertir_a_formato_cita(verso_key):
                cap, ver = verso_key.split(':')
                cap_romano = NUMEROS_ROMANOS[int(cap)] if int(cap) < len(NUMEROS_ROMANOS) else cap
                return f"[C. {cap_romano} - {ver}]"

            versos_prohibidos_formateados = [convertir_a_formato_cita(v) for v in versos_citados_en_conversacion]
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
            logger.info(f"Versos prohibidos: {versos_prohibidos_formateados}")

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

    total_chars = len(prompt)
    logger.info(f"Prompt construido: {total_chars:,} caracteres, {len(versos_contexto)} versos en contexto")
    return prompt

def calcular_max_tokens_respuesta():
    return 1200
