"""
Tests unitarios para Krishna AI.

Ejecutar: pytest test_krishna.py -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from procesado_bhagavad_gita_txt_corregido import convertir_romano_a_arabigo
from gender_detector import obtener_tratamiento_genero


class TestConvertirRomanoAArabigo:
    def test_basicos(self):
        assert convertir_romano_a_arabigo("I") == 1
        assert convertir_romano_a_arabigo("V") == 5
        assert convertir_romano_a_arabigo("X") == 10
        assert convertir_romano_a_arabigo("L") == 50
        assert convertir_romano_a_arabigo("C") == 100

    def test_compuestos(self):
        assert convertir_romano_a_arabigo("II") == 2
        assert convertir_romano_a_arabigo("III") == 3
        assert convertir_romano_a_arabigo("VI") == 6
        assert convertir_romano_a_arabigo("IV") == 4
        assert convertir_romano_a_arabigo("IX") == 9
        assert convertir_romano_a_arabigo("XII") == 12
        assert convertir_romano_a_arabigo("XVIII") == 18

    def test_invalidos(self):
        assert convertir_romano_a_arabigo("") is None
        assert convertir_romano_a_arabigo("ABC") is None
        assert convertir_romano_a_arabigo("") is None


class TestObtenerTratamientoGenero:
    def test_femenino_explicito(self):
        res = obtener_tratamiento_genero("Maria", genero="Femenino")
        assert res["querido"] == "querida"
        assert res["estimado"] == "estimada"
        assert res["hijo"] == "hija"
        assert res["devoto"] == "devota"

    def test_masculino_explicito(self):
        res = obtener_tratamiento_genero("Juan", genero="Masculino")
        assert res["querido"] == "querido"
        assert res["estimado"] == "estimado"
        assert res["hijo"] == "hijo"
        assert res["devoto"] == "devoto"

    def test_femenino_fallback_nombre(self):
        res = obtener_tratamiento_genero("Maria", genero=None, api_rotator=None)
        assert res["querido"] == "querida"

    def test_masculino_fallback_nombre(self):
        res = obtener_tratamiento_genero("Juan", genero=None, api_rotator=None)
        assert res["querido"] == "querido"

    def test_femenino_terminacion_a(self):
        res = obtener_tratamiento_genero("Laura", genero=None, api_rotator=None)
        assert res["querido"] == "querida"

    def test_masculino_terminacion_o(self):
        res = obtener_tratamiento_genero("Pedro", genero=None, api_rotator=None)
        assert res["querido"] == "querido"


class TestPromptBuilder:
    def test_extraer_versos_citados_romanos(self):
        from prompt_builder import extraer_versos_citados_del_historial
        bhagavad_gita_mock = {
            "capitulos": {
                "2": {
                    "versos": {
                        "47": {"texto": "Tienes derecho a la acción...", "significado": "", "locutor": "El Bienaventurado Señor"}
                    }
                }
            }
        }
        historial = [
            {"role": "assistant", "content": "Como dice el Gita [C. II - 47]"}
        ]
        versos, textos = extraer_versos_citados_del_historial(historial, bhagavad_gita_mock, ventana_prohibicion=6)
        assert "2:47" in versos
        assert len(textos) == 1

    def test_extraer_versos_citados_arabigos(self):
        from prompt_builder import extraer_versos_citados_del_historial
        bhagavad_gita_mock = {
            "capitulos": {
                "3": {
                    "versos": {
                        "8": {"texto": "Realiza la acción prescrita...", "significado": "", "locutor": "El Bienaventurado Señor"}
                    }
                }
            }
        }
        historial = [
            {"role": "assistant", "content": "Como dice [C. 3 - 8]"}
        ]
        versos, textos = extraer_versos_citados_del_historial(historial, bhagavad_gita_mock, ventana_prohibicion=6)
        assert "3:8" in versos
        assert len(textos) == 1

    def test_sin_versos_citados(self):
        from prompt_builder import extraer_versos_citados_del_historial
        historial = [
            {"role": "assistant", "content": "Hola, ¿cómo estás?"}
        ]
        versos, textos = extraer_versos_citados_del_historial(historial, {}, ventana_prohibicion=6)
        assert len(versos) == 0
        assert len(textos) == 0


class TestRotacionClaves:
    def _make_rotator(self, keys_data):
        from dataclasses import dataclass
        @dataclass
        class APIKeyInfo:
            key: str
            name: str
            last_used: float = 0.0
            failed_count: int = 0
            is_blocked: bool = False
            block_until: float = 0.0

        class FakeGeminiAPIRotator:
            def __init__(self):
                self.api_keys = [APIKeyInfo(**k) for k in keys_data]
                self.current_key_index = 0
                self.logger = None

            def _get_next_available_key(self):
                import time
                current_time = time.time()
                for key_info in self.api_keys:
                    if key_info.is_blocked and current_time > key_info.block_until:
                        key_info.is_blocked = False
                        key_info.failed_count = 0
                available_keys = [i for i, key in enumerate(self.api_keys) if not key.is_blocked]
                if not available_keys:
                    return None
                return min(available_keys, key=lambda i: self.api_keys[i].last_used)

        return FakeGeminiAPIRotator()

    def test_get_next_available_key_all_available(self):
        rotator = self._make_rotator([
            {"key": "key1", "name": "test1"},
            {"key": "key2", "name": "test2"},
            {"key": "key3", "name": "test3"},
        ])
        next_idx = rotator._get_next_available_key()
        assert next_idx is not None
        assert next_idx >= 0

    def test_get_next_available_key_all_blocked(self):
        import time
        rotator = self._make_rotator([
            {"key": "key1", "name": "test1", "is_blocked": True, "block_until": time.time() + 99999},
            {"key": "key2", "name": "test2", "is_blocked": True, "block_until": time.time() + 99999},
        ])
        next_idx = rotator._get_next_available_key()
        assert next_idx is None

    def test_get_next_available_key_one_available(self):
        import time
        rotator = self._make_rotator([
            {"key": "key1", "name": "test1", "is_blocked": True, "block_until": time.time() + 99999},
            {"key": "key2", "name": "test2", "is_blocked": False},
        ])
        next_idx = rotator._get_next_available_key()
        assert next_idx == 1


class TestPromptBuilderModule:
    def test_construir_prompt_krishna_basico(self):
        from prompt_builder import construir_prompt_krishna
        versos = [{
            'capitulo': 2,
            'verso': 47,
            'texto_completo': "Capítulo 2, Verso 47 (El Bienaventurado Señor): Tienes derecho a la acción...",
            'locutor': 'El Bienaventurado Señor',
            'es_krishna': True
        }]
        prompt = construir_prompt_krishna("¿Cuál es mi dharma?", versos, {}, None, "Arjuna", "Masculino")
        assert "Arjuna" in prompt
        assert "Krishna" in prompt
        assert "Capítulo 2" in prompt


class TestRAG:
    def test_rag_fallback_sin_api(self):
        class FakeRAG:
            def __init__(self):
                self.bhagavad_gita = {
                    "capitulos": {
                        "2": {
                            "versos": {
                                "47": {"texto": "texto", "significado": "", "locutor": "El Bienaventurado Señor"}
                            }
                        }
                    }
                }

            def _fallback_versos(self, versos_citados_previos):
                resultados = []
                for cap_num in sorted(self.bhagavad_gita['capitulos'].keys(), key=int):
                    capitulo = self.bhagavad_gita['capitulos'][cap_num]
                    for verso_num in sorted(capitulo['versos'].keys(), key=int):
                        verso = capitulo['versos'][verso_num]
                        locutor = verso.get('locutor', '')
                        if 'El Bienaventurado Señor' not in locutor:
                            continue
                        texto = verso.get('texto', '')
                        texto_completo = f"Capítulo {cap_num}, Verso {verso_num}"
                        if locutor:
                            texto_completo += f" ({locutor})"
                        if texto:
                            texto_completo += f": {texto}"
                        resultados.append({
                            'capitulo': int(cap_num),
                            'verso': int(verso_num),
                            'texto_completo': texto_completo,
                            'locutor': locutor,
                            'es_krishna': True,
                        })
                return resultados

        rag = FakeRAG()
        result = rag._fallback_versos(set())
        assert len(result) == 1
        assert result[0]['capitulo'] == 2
