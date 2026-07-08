"""Technical constructor service: generates specs from Blueprint."""
import json
import logging

from modules.studio.services import OpenAIClient
from modules.studio.constructor_prompts import (
    PROMPT_GENERAR_MODELO_DATOS,
    PROMPT_GENERAR_API,
    PROMPT_GENERAR_ARQUITECTURA,
    PROMPT_GENERAR_ROADMAP,
)

logger = logging.getLogger(__name__)


class ConstructorService:

    def __init__(self):
        self.ai = OpenAIClient()

    def generar_modelo_datos(self, gemelo_asis: dict, gemelo_tobe: dict, brechas: list) -> dict:
        prompt = PROMPT_GENERAR_MODELO_DATOS.format(
            gemelo_asis=json.dumps(gemelo_asis, indent=2, ensure_ascii=False),
            gemelo_tobe=json.dumps(gemelo_tobe, indent=2, ensure_ascii=False),
            brechas=json.dumps([b.to_dict() if hasattr(b, 'to_dict') else b for b in brechas], indent=2, ensure_ascii=False),
        )
        return self._call_ai(prompt)

    def generar_api(self, gemelo_tobe: dict, procesos: str, servicios: str) -> dict:
        prompt = PROMPT_GENERAR_API.format(
            gemelo_tobe=json.dumps(gemelo_tobe, indent=2, ensure_ascii=False),
            procesos=procesos,
            servicios=servicios,
        )
        return self._call_ai(prompt)

    def generar_arquitectura(self, gemelo_tobe: dict, plan: dict) -> dict:
        prompt = PROMPT_GENERAR_ARQUITECTURA.format(
            gemelo_tobe=json.dumps(gemelo_tobe, indent=2, ensure_ascii=False),
            plan=json.dumps(plan, indent=2, ensure_ascii=False),
        )
        return self._call_ai(prompt)

    def generar_roadmap(self, brechas: list, plan: dict, arquitectura: dict) -> dict:
        prompt = PROMPT_GENERAR_ROADMAP.format(
            brechas=json.dumps([b.to_dict() if hasattr(b, 'to_dict') else b for b in brechas], indent=2, ensure_ascii=False),
            plan=json.dumps(plan, indent=2, ensure_ascii=False),
            arquitectura=json.dumps(arquitectura, indent=2, ensure_ascii=False),
        )
        return self._call_ai(prompt)

    def _call_ai(self, prompt: str) -> dict:
        try:
            respuesta = self.ai.chat([
                {"role": "system", "content": "Eres un arquitecto de software senior. Genera especificaciones tecnicas precisas en JSON."},
                {"role": "user", "content": prompt},
            ])
            return json.loads(respuesta)
        except Exception as e:
            logger.error(f"Constructor AI error: {e}")
            return {"error": str(e)}
