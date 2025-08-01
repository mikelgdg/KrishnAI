# Krishna AI - Bhagavad Gita Chatbot 🕉️

Un chatbot inteligente que te permite dialogar directamente con Krishna del Bhagavad Gita. Tú eres Arjuna en el campo de batalla de Kurukshetra, y Krishna responderá tus dudas con las enseñanzas exactas del texto sagrado.

## ✨ Características

- **Respuestas Fieles**: Todas las respuestas están basadas únicamente en los versos del Bhagavad Gita
- **Referencias Exactas**: Cada respuesta incluye citas precisas de capítulo y verso
- **Interfaz Intuitiva**: Diseño limpio y espiritual para una experiencia inmersiva
- **Rotación de Claves**: Sistema robusto de manejo de claves API de Google Gemini
- **Contexto Inteligente**: Prioriza los capítulos más importantes del Gita para respuestas relevantes

## 🚀 Instalación y Uso

### Requisitos
```bash
pip install streamlit google-generativeai PyMuPDF
```

### Configuración
1. **Claves API**: Configura tus claves de Google Gemini en `rotacion_claves.py`
2. **Procesar el Gita**: Ejecuta el procesamiento del Bhagavad Gita:
   ```bash
   python procesado_bhagavad_gita.py
   ```
3. **Ejecutar la aplicación**:
   ```bash
   streamlit run app.py
   ```

## 📚 Estructura del Proyecto

```
├── app.py                      # Aplicación principal Krishna AI
├── procesado_bhagavad_gita.py  # Script para procesar el PDF por capítulos/versos
├── bhagavad_gita.json         # Base de datos estructurada del Gita
├── rotacion_claves.py         # Sistema de rotación de claves API
├── SABIDURÍA/                 # Carpeta con el PDF del Bhagavad Gita
│   └── Bhagavad-gita_Tal_Como_Es_1978_condensed.pdf
└── .streamlit/                # Recursos de la interfaz
    ├── logo2.png
    ├── UWU.png
    └── _style.css
```

## 🧠 Cómo Funciona

### Procesamiento del Texto
El script `procesado_bhagavad_gita.py` extrae el texto del PDF y lo estructura por:
- **Capítulos**: 18 capítulos del Bhagavad Gita
- **Versos**: Cada verso con su número, texto y significado
- **Referencias**: Sistema preciso de citado (Capítulo X, Verso Y)

### Generación de Respuestas
Krishna AI utiliza Google Gemini con:
- **Contexto Priorizado**: Capítulos más importantes (2, 4, 7, 9, 18) tienen prioridad
- **Prompt Especializado**: Instrucciones específicas para responder como Krishna
- **Fidelidad al Texto**: Solo usa contenido real del Bhagavad Gita

### Ejemplo de Uso
```
Usuario (Arjuna): "¿Cuál es mi dharma en esta situación difícil?"

Krishna AI: "Mi querido Arjuna, tu dharma como kshatriya es pelear por la justicia. 
Es mejor morir cumpliendo el dharma propio, aunque imperfectamente, que cumplir 
perfectamente el dharma de otro, pues eso es peligroso.

[Fuente: Bhagavad Gita, Capítulo 3, Verso 35]"
```

## ⚙️ Configuración Avanzada

### Ajuste de Parámetros
- **Temperatura**: Controla la creatividad (0.0-0.8, recomendado: 0.3)
- **Max Tokens**: Tokens máximos para respuestas (default: 1000)
- **Contexto**: Número de versos incluidos en el contexto (default: 80,000 tokens)

### Personalización
- **Capítulos Prioritarios**: Modifica la lista en `obtener_versos_contexto()`
- **Estilo de Respuesta**: Ajusta el prompt en `construir_prompt_krishna()`
- **Interfaz**: Personaliza CSS en `.streamlit/_style.css`

## 🔧 Mantenimiento

### Rotación de Claves API
El sistema incluye rotación automática de claves para:
- Evitar límites de velocidad
- Maximizar disponibilidad
- Manejar errores automáticamente

### Actualización del Contenido
Para actualizar o cambiar la traducción del Bhagavad Gita:
1. Reemplaza el PDF en `SABIDURÍA/`
2. Ejecuta `python procesado_bhagavad_gita.py`
3. Reinicia la aplicación

## 📖 Estructura de Datos

El archivo `bhagavad_gita.json` tiene la siguiente estructura:
```json
{
  "titulo": "Bhagavad Gita",
  "autor": "Vyasadeva",
  "traductor": "A.C. Bhaktivedanta Swami Prabhupada",
  "capitulos": {
    "1": {
      "numero": 1,
      "titulo": "Observando los ejércitos...",
      "versos": {
        "1": {
          "numero": 1,
          "texto": "Dhrtarastra dijo: Oh Sañjaya...",
          "significado": "Dhrtarastra era ciego..."
        }
      }
    }
  }
}
```

## 🤝 Contribuir

Si quieres contribuir al proyecto:
1. Fork el repositorio
2. Crea una rama para tu feature
3. Commit tus cambios
4. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. El contenido del Bhagavad Gita usado pertenece a The Bhaktivedanta Book Trust.

## 🙏 Reconocimientos

- **Traducción**: A.C. Bhaktivedanta Swami Prabhupada
- **Editor**: The Bhaktivedanta Book Trust
- **IA**: Google Gemini
- **Interface**: Streamlit

---

*"Abandona toda variedad de religiones y tan sólo entrégate a Mí. Yo te libraré de toda reacción pecaminosa. No temas."* - Bhagavad Gita 18.66
