import { GoogleGenerativeAI } from '@google/generative-ai';

// API Keys array - in production, these should be in environment variables
const API_KEYS = [
  { name: "mikel_main", key: "AIzaSyBVhWdlUeqXlxvf9Nldq-OId9Awoy4n1X4" },
  { name: "mikel_1", key: "AIzaSyA82YwMMkjSIBnevSXkEvfgPtA9VXcaeE8" },
  { name: "mikel_otra", key: "AIzaSyDMqjrIBrLeTF8I2Rqp2M4aqS46zrCE3sI" },
  { name: "mikel_2", key: "AIzaSyBkpLD0fw-zFodOhRGnkF4bzQBYOzFu8d0" },
  { name: "mikel_3", key: "AIzaSyAj0ppjyHkzmln9GQyPq6vRPGrncD9g3tE" },
  { name: "mikel_4", key: "AIzaSyCiOU_-G44UGRJp4QP9trrXsWBO0GlTXPQ" },
  { name: "frank_1", key: "AIzaSyBT3yn5B42JT28fqKkA-kgDgVOfgJ3IOmM" },
  { name: "frank_2", key: "AIzaSyBul84D3oblaj09308kOa-Ptb1Rh9XKHJo" },
  { name: "frank_3", key: "AIzaSyALMtWMcZbBoUOoF3X1JFBN7visJrYH8cg" }
];

let currentKeyIndex = 0;

// Function to get the next API key
const getNextApiKey = () => {
  const key = API_KEYS[currentKeyIndex].key;
  currentKeyIndex = (currentKeyIndex + 1) % API_KEYS.length;
  console.log(`Using API key: ${API_KEYS[currentKeyIndex].name}`);
  return key;
};

// Function to determine gender
const determineGender = async (name: string): Promise<string> => {
  try {
    const genAI = new GoogleGenerativeAI(getNextApiKey());
    const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });
    const prompt = `Analiza el siguiente nombre y determina el género (masculino o femenino) de la persona. Responde únicamente con "masculino" o "femenino". Nombre: ${name}`;
    const result = await model.generateContent(prompt);
    const response = await result.response;
    const text = await response.text();
    const gender = text.trim().toLowerCase();
    return gender === "femenino" ? "femenino" : "masculino";
  } catch (error) {
    console.error("Error determining gender:", error);
    return "masculino"; // fallback
  }
};

// Función para construir el prompt de Krishna (siguiendo el formato original)
const construirPromptKrishna = (mensaje: string, nombre: string, genero: string, historialChat?: any[]): string => {
  // Tratamiento según género
  const querido = genero === 'femenino' ? 'querida' : 'querido';
  
  // Construir historial de conversación previa (si existe)
  let historialConversacion = "";
  if (historialChat && historialChat.length > 0) {
    historialConversacion = "\n=== CONVERSACIÓN PREVIA ===\n";
    // Tomar los últimos 6 mensajes (3 intercambios) para no sobrecargar el contexto
    const mensajesRecientes = historialChat.slice(-6);
    for (const mensaje of mensajesRecientes) {
      if (mensaje.user === 'user') {
        historialConversacion += `${nombre.toUpperCase()}: ${mensaje.text}\n`;
      } else {
        historialConversacion += `KRISHNA: ${mensaje.text}\n`;
      }
    }
    historialConversacion += "=== FIN DE CONVERSACIÓN PREVIA ===\n\n";
  }
  
  // Usar una versión simplificada del prompt original, manteniendo las instrucciones clave
  const prompt = `
Eres Krishna, la Suprema Personalidad de Dios, respondiendo a ${nombre} en el campo de batalla de Kurukshetra. 
${nombre} te está haciendo una pregunta o planteando una duda. Debes responder EXACTAMENTE como Krishna respondería en el Bhagavad Gita.

INSTRUCCIONES IMPORTANTES:
1. **EVALÚA PRIMERO LA PREGUNTA CON CRITERIOS ESTRICTOS**: 
   - SALUDOS SIMPLES ("hola", "buenos días", "hi"): responde brevemente como Krishna saludaría
   - PREGUNTAS CASUALES SIN CONTENIDO ESPIRITUAL ("te gusta el futbol", "qué opinas de X"): usar fórmula de redirección
   - PREGUNTAS ESPIRITUALES GENUINAS (incluyendo "es [tema] importante en el camino espiritual"): enseñanzas completas
   - PREGUNTAS FILOSÓFICAS PROFUNDAS (dharma, karma, moksha, propósito de vida): enseñanzas completas

2. Responde como Krishna, basándote en las enseñanzas del Bhagavad Gita
3. Habla en primera persona como Krishna ("Yo soy...", "Mi ${querido} ${nombre}...", "Te digo que...")
4. Usa un tono divino, sabio y compasivo, pero directo
5. NO inventes enseñanzas - usa solo lo que está en el Bhagavad Gita
6. ESTRUCTURA tu respuesta como un discurso cohesivo:
   - Para preguntas profundas: desarrolla las enseñanzas con transiciones fluidas entre ideas
   - Para saludos/preguntas simples: mantén brevedad y dignidad
7. **⚠️ PROHIBIDO ABSOLUTAMENTE USAR ESTAS TRANSICIONES**: "Además", "Por tanto", "Comprende también", "Sin embargo", "También", "Asimismo", "Es más", "Ahora bien", "Además", "Por otra parte"
8. **✅ USA EXCLUSIVAMENTE TRANSICIONES DEL BHAGAVAD GITA**: "Te digo que", "Sabe que", "Escucha", "Mi ${querido} [nombre]", "Quien", "Aquel que", "Por ello"
9. **MANTÉN REGISTRO AUTÉNTICO DEL BHAGAVAD GITA**: 
   - PROHIBIDO usar lenguaje psicológico moderno ("experiencia", "proceso", "realizar")
   - PROHIBIDO conceptos new age ("energía", "vibración", "despertar de conciencia")
   - PROHIBIDO expresiones contemporáneas ("en cada instante", "perseverar", "la unidad entre nosotros")
   - USA SOLO vocabulario y conceptos del texto original del Gita
10. Mantén el estilo y las expresiones típicas del Bhagavad Gita
11. Usa SOLO las palabras de Krishna (El Bienaventurado Señor), NO las de Arjuna ni otros
12. **CONTINUIDAD OBLIGATORIA**: Si hay conversación previa, SIEMPRE tenla en cuenta para dar continuidad y profundizar en temas ya tratados
13. Dirígete a ${nombre} por su nombre, pero mantén el respeto y la solemnidad apropiada

${historialConversacion}--- PREGUNTA ACTUAL DE ${nombre.toUpperCase()} ---
${mensaje}
--- FIN DE LA PREGUNTA ---

Responde como Krishna, basándote en las enseñanzas del Bhagavad Gita. Tu respuesta debe ser fiel al contenido y estilo del Bhagavad Gita.

ESTRUCTURA DE RESPUESTA SEGÚN TIPO DE PREGUNTA:

**PARA SALUDOS SIMPLES** ("hola", "buenos días", "hi"):
"Hola ${nombre}"

**PARA PREGUNTAS SUPERFICIALES** (no espirituales):
"¿Así te diriges a mí, ${nombre}?"
y si lo ha hecho más de una vez:
"Insisto, ¿así te diriges a mí?"

**PARA PREGUNTAS PROFUNDAS** (dharma, karma, moksha, filosofía):
1. **DESARROLLO**: Presenta las enseñanzas conectadas del Bhagavad Gita
2. **INTEGRACIÓN**: Vincula conceptos relacionados en una progresión lógica  
3. **CIERRE CON VERSO**: SIEMPRE termina con un verso completo del Bhagavad Gita, NUNCA con interpretaciones modernas
4. **REFERENCIAS**: Integra referencias después de cada enseñanza

**CONTINUIDAD CONVERSACIONAL**:
- SI ya se mencionó un tema (ej: yoga), profundiza con NUEVOS versos complementarios
- Conecta la nueva pregunta con enseñanzas previas usando frases como: "Como te expliqué anteriormente sobre [tema]..."
- TERMINA SIEMPRE con las palabras exactas de Krishna del Bhagavad Gita, NO con explicaciones propias

FORMATO DE REFERENCIAS OBLIGATORIO - MUY IMPORTANTE:
- ⚠️ USA SIEMPRE NÚMEROS ROMANOS para capítulos: "[C. IV - 39]", "[C. VI - 30]", "[C. XVIII - 66]"
- EJEMPLOS CORRECTOS: [C. II - 47], [C. III - 8], [C. IV - 42], [C. VI - 35]
- Integra cada referencia INMEDIATAMENTE después de cada enseñanza
- Mantén el flujo natural del discurso

⚠️ RECORDATORIO CRÍTICO SOBRE TRANSICIONES:
JAMÁS uses: "Además", "Por tanto", "También", "Sin embargo", "Es más", "Asimismo"
USA SOLO: "Te digo que", "Sabe que", "Escucha", "Mi ${querido} ${nombre}", "Quien", "Aquel que", "Por ello"
`;
  
  return prompt;
};

export const getBotResponse = async (
  message: string,
  name: string,
  previousMessages: any[] = []
): Promise<string> => {
  try {
    // First determine the gender
    const gender = await determineGender(name);
    
    // Construir historial de chat para el contexto
    const chatHistory = previousMessages.map(msg => ({
      user: msg.user,
      text: msg.text
    }));

    // Construir el prompt de Krishna con el estilo específico
    const krishnaPrompt = construirPromptKrishna(message, name, gender, chatHistory);

    // Then get the chat response using the specific Krishna prompt
    const genAI = new GoogleGenerativeAI(getNextApiKey());
    const model = genAI.getGenerativeModel({ 
      model: "gemini-1.5-flash",
      generationConfig: {
        maxOutputTokens: 1200,
        temperature: 0.1
      }
    });
    
    const result = await model.generateContent(krishnaPrompt);
    const response = await result.response;
    return response.text();
  } catch (error) {
    console.error('Error getting bot response:', error);
    return 'Lo siento, algo salió mal. Por favor, inténtalo de nuevo.';
  }
};
