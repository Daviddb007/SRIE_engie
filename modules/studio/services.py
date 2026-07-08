"""Services for SRIE Engine: phase-based interview, auto twin generation, maturity scoring."""
import json
import os
import re
import logging
from datetime import datetime, timezone

from core import db
from core.models import Client
from core.models.consultoria import Consultoria, ConsultoriaMensaje
from core.models.twin_asis import TwinASIS
from core.models.twin_tobe import TwinTOBE
from core.models.brecha import Brecha
from core.models.plan_recomendado import PlanRecomendado

from modules.studio.ai_prompts import FASES, get_system_prompt, PROMPT_GENERAR_TWIN
from modules.studio.industry_packs import get_industry_prompt_extension
from modules.studio.srie_mapper import map_brechas_to_soluciones

logger = logging.getLogger(__name__)


class OpenAIClient:

    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY', '')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')

    def chat(self, messages, response_format=None):
        import requests
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "response_format": {"type": "json_object"},
        }
        if response_format:
            payload["response_format"] = response_format
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers, json=payload, timeout=90
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


class EntrevistaIAService:

    def __init__(self):
        self.ai = OpenAIClient()

    def procesar_mensaje(self, consultoria_id: str, mensaje_usuario: str) -> dict:
        consultoria = Consultoria.query.get(consultoria_id)
        if not consultoria:
            raise ValueError("Consultoria no encontrada")

        historial = ConsultoriaMensaje.query.filter_by(
            consultoria_id=consultoria_id
        ).order_by(ConsultoriaMensaje.timestamp).all()

        fase_idx, progreso_fase = self._determinar_fase(historial)
        contexto = self._construir_contexto(historial)

        system_prompt = get_system_prompt(fase_idx, contexto, progreso_fase)
        if consultoria.industria and consultoria.industria != 'general':
            system_prompt += get_industry_prompt_extension(consultoria.industria)
        messages = [{"role": "system", "content": system_prompt}]

        for msg in historial[-20:]:
            role = "assistant" if msg.rol == "ia" else "user"
            messages.append({"role": role, "content": msg.contenido})

        messages.append({"role": "user", "content": mensaje_usuario})

        user_msg = ConsultoriaMensaje(
            consultoria_id=consultoria_id, rol="usuario",
            contenido=mensaje_usuario, capa=FASES[fase_idx]["nombre"],
        )
        db.session.add(user_msg)
        db.session.flush()

        try:
            respuesta_raw = self.ai.chat(messages)
            try:
                respuesta = json.loads(respuesta_raw)
            except json.JSONDecodeError:
                match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', respuesta_raw)
                respuesta = json.loads(match.group(1).strip()) if match else {"accion": "preguntar", "mensaje": "Disculpa, no entendi bien. Podrias explicarlo de otra forma?", "hallazgos": []}
        except Exception as e:
            logger.error(f"AI error: {type(e).__name__}: {e}")
            respuesta = {"accion": "preguntar", "mensaje": "Disculpa, no entendi bien. Podrias explicarlo de otra forma?", "hallazgos": []}

        ai_content = respuesta.get("mensaje", "Podrias contarme mas?")
        accion = respuesta.get("accion", "preguntar")
        nuevo_progreso = respuesta.get("progreso_fase", progreso_fase + 1)
        resumen = respuesta.get("resumen_fase", "")

        ai_msg = ConsultoriaMensaje(
            consultoria_id=consultoria_id, rol="ia",
            contenido=ai_content, capa=FASES[fase_idx]["nombre"],
        )
        db.session.add(ai_msg)

        hallazgos = respuesta.get("hallazgos", [])
        if hallazgos:
            notas = []
            for h in hallazgos:
                tipo = h.get('tipo', 'hipotesis')
                iconos = {'confirmado': '[OK]', 'inferido': '[i]', 'hipotesis': '[?]'}
                capa_h = h.get('capa', 'general')
                desc = h.get('descripcion', '')
                detalle = h.get('detalle', '')
                linea = f"{iconos.get(tipo, '[?]')} [{tipo.upper()}] [{capa_h}] {desc}"
                if detalle:
                    linea += f" | {detalle}"
                notas.append(linea)
            consultoria.notas = (consultoria.notas or "") + "\n" + "\n".join(notas)
            if resumen:
                consultoria.notas += f"\n--- {resumen} ---"

        if accion == "completar":
            consultoria.estado = "activa"

        db.session.commit()

        return {
            "mensaje": ai_content,
            "accion": accion,
            "fase_actual": FASES[fase_idx]["nombre"],
            "progreso_fase": nuevo_progreso,
            "hallazgos": hallazgos,
            "resumen": resumen,
        }

    def generar_blueprint(self, consultoria_id: str) -> dict:
        """Generate complete blueprint: AS IS + maturity + TO BE + breaches + plan."""
        consultoria = Consultoria.query.get(consultoria_id)
        if not consultoria:
            raise ValueError("Consultoria no encontrada")

        mensajes = ConsultoriaMensaje.query.filter_by(
            consultoria_id=consultoria_id
        ).order_by(ConsultoriaMensaje.timestamp).all()

        conversacion = "\n".join(
            f"{'Cliente' if m.rol == 'usuario' else 'Consultor'}: {m.contenido}"
            for m in mensajes
        )

        hallazgos_texto = consultoria.notas or "Sin hallazgos registrados"
        industria_contexto = ""
        if consultoria.industria and consultoria.industria != 'general':
            from modules.studio.industry_packs import get_industry_pack
            pack = get_industry_pack(consultoria.industria)
            if pack:
                industria_contexto = f"\n\nINDUSTRIA: {pack['nombre']}\nKPIs del sector: {', '.join(pack['kpi_industria'])}\nSoluciones tipicas: {', '.join(s['modulo'] for s in pack['soluciones_prioritarias'])}"
        
        prompt = PROMPT_GENERAR_TWIN.format(conversacion=conversacion + industria_contexto, hallazgos=hallazgos_texto)

        try:
            ai = OpenAIClient()
            respuesta_raw = ai.chat([
                {"role": "system", "content": "Eres un arquitecto empresarial experto. Genera diagnosticos completos y precisos en JSON."},
                {"role": "user", "content": prompt},
            ])
            resultado = json.loads(respuesta_raw)
        except Exception as e:
            logger.error(f"Error generating blueprint: {e}")
            raise

        madurez = resultado.get("madurez", {"general": 50, "por_capa": {}})

        twin_asis = TwinASIS.query.filter_by(consultoria_id=consultoria_id).first()
        asis_data = resultado.get("gemelo_asis", {})
        problemas = resultado.get("brechas", [])
        if twin_asis:
            twin_asis.capas = {"madurez": madurez, **asis_data}
            twin_asis.problemas = problemas
        else:
            twin_asis = TwinASIS(consultoria_id=consultoria_id, capas={"madurez": madurez, **asis_data}, problemas=problemas)
            db.session.add(twin_asis)

        twin_tobe = TwinTOBE.query.filter_by(consultoria_id=consultoria_id).first()
        tobe_data = resultado.get("gemelo_tobe", {})
        if twin_tobe:
            twin_tobe.capas = tobe_data
        else:
            twin_tobe = TwinTOBE(consultoria_id=consultoria_id, capas=tobe_data)
            db.session.add(twin_tobe)

        Brecha.query.filter_by(consultoria_id=consultoria_id).delete()
        brechas_creadas = []
        for i, b in enumerate(resultado.get("brechas", [])):
            brecha = Brecha(
                consultoria_id=consultoria_id,
                capa=b.get("capa", "general"),
                problema_actual=b.get("problema_actual", ""),
                estado_deseado=b.get("estado_deseado", ""),
                impacto=b.get("impacto", "media"),
                prioridad=str(b.get("complejidad", "media")),
                solucion=b.get("solucion_sugerida", ""),
                sort_order=i,
            )
            db.session.add(brecha)
            brechas_creadas.append(brecha)

        plan_data = resultado.get("plan_sugerido", {})
        items = plan_data.get("items", [])
        total = plan_data.get("inversion_estimada", 0)
        plan = PlanRecomendado.query.filter_by(consultoria_id=consultoria_id).first()
        if plan:
            plan.items = items
            plan.total_estimado = total
            plan.duracion_estimada = plan_data.get("tiempo_estimado", "")
        else:
            plan = PlanRecomendado(consultoria_id=consultoria_id, items=items, total_estimado=total, duracion_estimada=plan_data.get("tiempo_estimado", ""))
            db.session.add(plan)

        consultoria.estado = "completada"
        db.session.commit()

        return {
            "madurez": madurez,
            "resumen_ejecutivo": resultado.get("resumen_ejecutivo", {}),
            "gemelo_asis": asis_data,
            "gemelo_tobe": tobe_data,
            "brechas": [b.to_dict() for b in brechas_creadas],
            "plan": items,
        }

    def _determinar_fase(self, historial):
        """Determine which phase the interview is in."""
        mensajes_ia = [m for m in historial if m.rol == "ia"]
        total_intercambios = len([m for m in historial if m.rol == "usuario"])

        if total_intercambios <= 4:
            return 0, total_intercambios + 1
        elif total_intercambios <= 8:
            return 1, total_intercambios - 3
        elif total_intercambios <= 11:
            return 2, total_intercambios - 7
        elif total_intercambios <= 14:
            return 3, total_intercambios - 10
        else:
            return 3, 4

    def _construir_contexto(self, historial):
        """Build a context summary of what has been discussed."""
        mensajes = [m for m in historial if m.rol == "usuario"]
        if not mensajes:
            return ""
        textos = [m.contenido[:100] for m in mensajes[-5:]]
        return "El cliente ha mencionado: " + "; ".join(textos)


class TwinService:

    @staticmethod
    def get_asis(consultoria_id: str) -> dict:
        twin = TwinASIS.query.filter_by(consultoria_id=consultoria_id).first()
        return twin.to_dict() if twin else {"capas": {}, "problemas": []}

    @staticmethod
    def get_tobe(consultoria_id: str) -> dict:
        twin = TwinTOBE.query.filter_by(consultoria_id=consultoria_id).first()
        return twin.to_dict() if twin else {"capas": {}, "objetivos": []}


class BrechaService:

    @staticmethod
    def get_brechas(consultoria_id: str) -> list:
        return Brecha.query.filter_by(consultoria_id=consultoria_id).order_by(Brecha.sort_order).all()


class PlanService:

    @staticmethod
    def get_plan(consultoria_id: str) -> dict:
        plan = PlanRecomendado.query.filter_by(consultoria_id=consultoria_id).first()
        if not plan:
            return {"items": [], "total_estimado": 0, "duracion_estimada": ""}
        return {"items": plan.items, "total_estimado": float(plan.total_estimado), "id": plan.id, "duracion_estimada": plan.duracion_estimada or ""}
