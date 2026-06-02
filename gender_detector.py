"""
Detección de género para tratamiento de Krishna AI.
"""

import logging

logger = logging.getLogger(__name__)

NOMBRES_FEMENINOS = [
    "maria", "ana", "carmen", "isabel", "pilar", "dolores", "teresa", "rosa",
    "francisca", "antonia", "mercedes", "elena", "laura", "cristina", "marta",
    "patricia", "sandra", "lucia", "monica", "silvia", "beatriz", "julia",
    "irene", "raquel", "sara", "sofia", "andrea", "claudia", "daniela",
    "paola", "alejandra", "gabriela", "natalia", "carolina"
]

def obtener_tratamiento_genero(nombre_usuario, genero=None, api_rotator=None):
    if genero == "Femenino":
        return {"querido": "querida", "estimado": "estimada", "hijo": "hija", "devoto": "devota"}
    elif genero == "Masculino":
        return {"querido": "querido", "estimado": "estimado", "hijo": "hijo", "devoto": "devoto"}
    else:
        if api_rotator and nombre_usuario.strip():
            try:
                prompt_genero = f"""
Analiza el nombre "{nombre_usuario}" y determina si es típicamente masculino o femenino.

Responde ÚNICAMENTE con una sola palabra:
- "MASCULINO" si es un nombre típicamente masculino
- "FEMENINO" si es un nombre típicamente femenino
- "MASCULINO" si no estás seguro (por defecto)

Nombre: {nombre_usuario}
Respuesta:"""
                response = api_rotator.generate_content_with_retry(
                    model_name='gemini-2.0-flash',
                    prompt=prompt_genero,
                    generation_config={'temperature': 0.1, 'max_output_tokens': 10},
                    max_retries=1,
                    timeout_seconds=5
                )
                resultado = response.text.strip().upper()
                logger.info(f"Gemini infirió género para '{nombre_usuario}': {resultado}")
                if "FEMENINO" in resultado:
                    return {"querido": "querida", "estimado": "estimada", "hijo": "hija", "devoto": "devota"}
                else:
                    return {"querido": "querido", "estimado": "estimado", "hijo": "hijo", "devoto": "devoto"}
            except Exception as e:
                logger.warning(f"Error en inferencia de género con Gemini: {e}")

        nombre_lower = nombre_usuario.lower().strip()
        if (nombre_lower in NOMBRES_FEMENINOS or
            nombre_lower.endswith('a') and not nombre_lower.endswith('ma') and len(nombre_lower) > 3):
            logger.info(f"Detección fallback para '{nombre_usuario}': FEMENINO")
            return {"querido": "querida", "estimado": "estimada", "hijo": "hija", "devoto": "devota"}
        else:
            logger.info(f"Detección fallback para '{nombre_usuario}': MASCULINO")
            return {"querido": "querido", "estimado": "estimado", "hijo": "hijo", "devoto": "devoto"}
