# KrishnAI

Chat with Krishna -- Bhagavad Gita wisdom via Gemini + RAG

A Streamlit chatbot that lets you converse with Krishna from the Bhagavad Gita. You take the role of Arjuna on the battlefield of Kurukshetra, and Krishna answers your questions using exact verses from the scripture, delivered in his authentic voice.

## How It Works

### RAG (Retrieval-Augmented Generation)

The system generates semantic embeddings for every verse in the Bhagavad Gita using Google's embedding model. When you ask a question, KrishnAI retrieves the most contextually relevant verses -- prioritizing those spoken by Krishna himself -- and feeds them into the language model as grounded context. This ensures every answer is anchored in the actual text of the Gita.

### Gemini Generation

The retrieved verses are assembled into a structured prompt that instructs Google Gemini to respond as Krishna would: in first person, with divine authority, using vocabulary and reasoning drawn directly from the Gita. An anti-repetition system tracks which verses have already been cited in the conversation and prevents them from being reused, allowing discussions to deepen naturally.

### Key Features

- **Scripture-grounded responses** -- every answer traces back to specific chapter-verse citations
- **Semantic verse retrieval** -- embeddings find the most relevant Gita passages for your question
- **Conversational memory** -- anti-repetition mechanism tracks cited verses across the session
- **API key rotation** -- built-in rotation across multiple Gemini keys to handle rate limits
- **Gender-aware address** -- automatic detection adjusts Krishna's address (querido/querida)
- **Configurable creativity** -- temperature slider to balance fidelity vs. variation

## Installation

```bash
pip install -r requirements.txt
```

## Usage

1. Process the Bhagavad Gita text and build the structured JSON database:

```bash
python setup_gita.py
```

2. Configure your Google Gemini API keys in `.streamlit/secrets.toml` (see `.streamlit/secrets.example.toml`).

3. Launch the app:

```bash
streamlit run app.py
```

4. Enter your name in the sidebar -- KrishnAI will address you as Arjuna and detect the appropriate gender for the address.

## Project Structure

```
├── app.py                          # Streamlit application entry point
├── rag_krishna.py                  # RAG module -- embeddings and semantic retrieval
├── prompt_builder.py               # Prompt construction with anti-repetition logic
├── gita_loader.py                  # Bhagavad Gita JSON loader
├── gender_detector.py              # Gender inference for proper address
├── rotacion_claves.py              # API key rotation manager
├── ui.py                           # UI components and helpers
├── setup_gita.py                   # One-time setup to build the verse database
├── bhagavad_gita_txt_corregido.json # Structured verse database
├── Bhagavad-Gita-Anonimo.txt       # Source text
├── requirements.txt                # Python dependencies
├── .streamlit/
│   ├── secrets.toml                # API keys (user-configured)
│   ├── secrets.example.toml        # Example secrets template
│   ├── _style.css                  # Custom UI styling
│   ├── krishna.png                 # Krishna avatar
│   └── arjuna.png                  # Arjuna avatar
└── KrishnAI_Mobile_New/            # React Native mobile app (separate)
```

## Requirements

- Python 3.10+
- Google Gemini API key(s)
- Dependencies listed in `requirements.txt`

## Configuration

### API Keys

Add your Gemini API keys to `.streamlit/secrets.toml`:

```toml
[gkeys]
keys = ["AIzaSy...", "AIzaSy..."]
```

The built-in key rotator cycles through keys automatically when rate limits are hit.

### Parameters

- **Temperature** (0.0-0.8): control response creativity. Lower values stay closer to the source text.
- **Context window**: defaults to ~80K tokens of verse context; adjustable in `obtener_versos_contexto()`.
- **Response tokens**: defaults to 1200 max output tokens.

## License

MIT. The Bhagavad Gita text used in this project is the translation by A.C. Bhaktivedanta Swami Prabhupada, copyright The Bhaktivedanta Book Trust.
