"""
Módulo RAG (Retrieval-Augmented Generation) para Krishna AI.
Genera embeddings semánticos de los versos del Bhagavad Gita
y recupera los más relevantes para cada pregunta del usuario.
"""

import json
import os
import pickle
import numpy as np
import google.generativeai as genai
import logging

logger = logging.getLogger(__name__)

EMBEDDING_CACHE = "embeddings_cache.pkl"
EMBEDDING_MODEL = "models/embedding-001"

class RAGKrishna:
    def __init__(self, bhagavad_gita: dict, api_rotator=None):
        self.bhagavad_gita = bhagavad_gita
        self.api_rotator = api_rotator
        self.verse_embeddings: list[dict] = []
        self._load_or_build_embeddings()

    def _get_embedding(self, text: str) -> list[float]:
        if self.api_rotator:
            key_info = self.api_rotator.api_keys[self.api_rotator.current_key_index]
            genai.configure(api_key=key_info.key)
        try:
            result = genai.embed_content(model=EMBEDDING_MODEL, content=text)
            return result['embedding']
        except Exception as e:
            logger.warning(f"Embedding falló, usando fallback: {e}")
            return [0.0] * 768

    def _build_all_embeddings(self) -> list[dict]:
        verses = []
        for cap_num in sorted(self.bhagavad_gita['capitulos'].keys(), key=int):
            capitulo = self.bhagavad_gita['capitulos'][cap_num]
            for verso_num in sorted(capitulo['versos'].keys(), key=int):
                verso = capitulo['versos'][verso_num]
                locutor = verso.get('locutor', '')
                texto = verso.get('texto', '')
                significado = verso.get('significado', '')
                texto_completo = f"Capítulo {cap_num}, Verso {verso_num}"
                if locutor:
                    texto_completo += f" ({locutor})"
                if texto:
                    texto_completo += f": {texto}"
                if significado:
                    texto_completo += f" SIGNIFICADO: {significado}"
                verses.append({
                    'capitulo': int(cap_num),
                    'verso': int(verso_num),
                    'texto_completo': texto_completo,
                    'locutor': locutor,
                    'es_krishna': 'El Bienaventurado Señor' in locutor,
                    'embedding': None
                })
        total = len(verses)
        logger.info(f"Generando embeddings para {total} versos...")
        for i, v in enumerate(verses):
            if i % 20 == 0:
                logger.info(f"  Embedding {i+1}/{total}")
            try:
                v['embedding'] = self._get_embedding(v['texto_completo'])
            except Exception as e:
                logger.warning(f"  Error en embedding {i+1}: {e}")
                v['embedding'] = [0.0] * 768
        return verses

    def _load_or_build_embeddings(self):
        if os.path.exists(EMBEDDING_CACHE):
            try:
                with open(EMBEDDING_CACHE, 'rb') as f:
                    self.verse_embeddings = pickle.load(f)
                logger.info(f"Embeddings cargados desde caché: {len(self.verse_embeddings)} versos")
                return
            except Exception as e:
                logger.warning(f"No se pudo cargar caché de embeddings: {e}")
        logger.info("Construyendo embeddings desde cero...")
        self.verse_embeddings = self._build_all_embeddings()
        try:
            with open(EMBEDDING_CACHE, 'wb') as f:
                pickle.dump(self.verse_embeddings, f)
            logger.info("Embeddings guardados en caché")
        except Exception as e:
            logger.warning(f"No se pudo guardar caché de embeddings: {e}")

    def obtener_versos_relevantes(self, pregunta: str, top_k: int = 25, versos_citados_previos: set | None = None) -> list[dict]:
        if versos_citados_previos is None:
            versos_citados_previos = set()
        try:
            query_emb = self._get_embedding(pregunta)
            query_vec = np.array(query_emb, dtype=np.float32)
            similarities = []
            for v in self.verse_embeddings:
                verso_key = f"{v['capitulo']}:{v['verso']}"
                if verso_key in versos_citados_previos:
                    similarities.append(-1.0)
                    continue
                if not v.get('es_krishna', False):
                    similarities.append(-2.0)
                    continue
                if v['embedding'] is None or all(x == 0.0 for x in v['embedding']):
                    similarities.append(-1.0)
                    continue
                emb_vec = np.array(v['embedding'], dtype=np.float32)
                cos_sim = np.dot(query_vec, emb_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(emb_vec) + 1e-10)
                similarities.append(float(cos_sim))
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            resultados = []
            for idx in top_indices:
                sim = similarities[idx]
                if sim > 0.3:
                    resultados.append(self.verse_embeddings[idx])
            logger.info(f"RAG: '{pregunta[:50]}...' → {len(resultados)} versos recuperados de {top_k} candidatos")
            return resultados
        except Exception as e:
            logger.warning(f"Error en RAG, usando fallback: {e}")
            return self._fallback_versos(versos_citados_previos)

    def _fallback_versos(self, versos_citados_previos: set) -> list[dict]:
        resultados = []
        for cap_num in sorted(self.bhagavad_gita['capitulos'].keys(), key=int):
            capitulo = self.bhagavad_gita['capitulos'][cap_num]
            for verso_num in sorted(capitulo['versos'].keys(), key=int):
                verso = capitulo['versos'][verso_num]
                verso_key = f"{cap_num}:{verso_num}"
                if verso_key in versos_citados_previos:
                    continue
                locutor = verso.get('locutor', '')
                if 'El Bienaventurado Señor' not in locutor:
                    continue
                texto = verso.get('texto', '')
                significado = verso.get('significado', '')
                texto_completo = f"Capítulo {cap_num}, Verso {verso_num}"
                if locutor:
                    texto_completo += f" ({locutor})"
                if texto:
                    texto_completo += f": {texto}"
                if significado:
                    texto_completo += f" SIGNIFICADO: {significado}"
                resultados.append({
                    'capitulo': int(cap_num),
                    'verso': int(verso_num),
                    'texto_completo': texto_completo,
                    'locutor': locutor,
                    'es_krishna': True,
                })
                if len(resultados) >= 25:
                    break
            if len(resultados) >= 25:
                break
        return resultados
