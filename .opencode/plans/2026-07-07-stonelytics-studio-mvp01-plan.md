# Stonelytics Studio — MVP 01 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build Stonelytics Studio — a platform that converts a client conversation into a structured Enterprise Blueprint (diagnostic + proposal PDF). MVP 01 covers: client CRM, AI-guided interview, AS-IS/TO-BE twin, gap analysis, SRIE recommendation engine, quotation, and proposal PDF.

**Architecture:** Flask 3.1 app with Jinja2 templates, PostgreSQL, OpenAI/Gemini AI, WeasyPrint PDF. New `modules/studio/` blueprint integrated into existing Stonelytics app at `C:\Users\Usuario\stonelytics\stonelytics\`.

**Tech Stack:** Flask 3.1, SQLAlchemy, PostgreSQL, OpenAI API, Bootstrap 5, Alpine.js, WeasyPrint.

## Global Constraints

- All new models use `BaseModel` from `core/models/base.py` (UUID PK, timestamps, to_dict)
- All new blueprints use `@login_required` from Flask-Login
- All new templates extend `base.html` and use the admin layout pattern
- Follow existing patterns in `modules/cotizador/routes.py` for blueprint structure
- Use `core/errors.py` exceptions (NotFoundError, ValidationError)
- Use `core/extensions.py` imports (db, login_manager)
- All prices stored as `Numeric(12, 2)` in COP
- All JSON fields stored as `db.JSON` with `default=dict`
- All routes use `/studio/` prefix
- All templates live in `templates/studio/`
- All static JS lives in `static/studio/`
- All AI calls go through OpenAI API (GPT-4o-mini), configurable via `OPENAI_API_KEY` env var

---

### Task 1: Models — Consultoria, Twin, Brecha, Plan

**Files:**
- Create: `stonelytics/core/models/consultoria.py`
- Create: `stonelytics/core/models/twin_asis.py`
- Create: `stonelytics/core/models/twin_tobe.py`
- Create: `stonelytics/core/models/brecha.py`
- Create: `stonelytics/core/models/plan_recomendado.py`
- Modify: `stonelytics/core/models/__init__.py` (add imports)

**Interfaces:**
- Consumes: `BaseModel` from `core/models/base.py`, `Client` from `core/models/client.py`
- Produces: 6 new SQLAlchemy model classes with `to_dict()` support

**Model: Consultoria**
```
id (UUID PK), cliente_id (FK clients.id), 
estado (String 20, default='borrador'), 
fecha_inicio (DateTime), notas (Text nullable),
created_at, updated_at
Relations: cliente (Client backref 'consultorias'), mensajes (ConsultoriaMensaje), twin_asis (TwinASIS), twin_tobe (TwinTOBE), brechas (Brecha), plan (PlanRecomendado)
```

**Model: ConsultoriaMensaje**
```
id (UUID PK), consultoria_id (FK consultorias.id),
rol (String 10: 'ia' or 'usuario'),
contenido (Text), capa (String 50 nullable),
timestamp (DateTime, default=utcnow)
Relation: consultoria (Consultoria backref 'mensajes')
```

**Model: TwinASIS**
```
id (UUID PK), consultoria_id (FK consultorias.id, unique),
capas (JSON), problemas (JSON, default=list),
created_at, updated_at
Relation: consultoria (Consultoria backref 'twin_asis', uselist=False)
```

**Model: TwinTOBE**
```
id (UUID PK), consultoria_id (FK consultorias.id, unique),
capas (JSON), objetivos (JSON, default=list),
created_at, updated_at
Relation: consultoria (Consultoria backref 'twin_tobe', uselist=False)
```

**Model: Brecha**
```
id (UUID PK), consultoria_id (FK consultorias.id),
capa (String 50), problema_actual (Text),
estado_deseado (Text), impacto (String 10: 'alta'/'media'/'baja'),
prioridad (String 10: 'alta'/'media'/'baja'),
solucion (Text nullable), sort_order (Integer default=0),
created_at, updated_at
Relation: consultoria (Consultoria backref 'brechas')
```

**Model: PlanRecomendado**
```
id (UUID PK), consultoria_id (FK consultorias.id, unique),
items (JSON, default=list), total_estimado (Numeric 12,2 default=0),
duracion_estimada (String 50 nullable), created_at
Relation: consultoria (Consultoria backref 'plan', uselist=False)
```

- [ ] **Step 1: Create consultoria.py**

Write `core/models/consultoria.py`:
```python
from core import db
from core.models.base import BaseModel

class Consultoria(BaseModel):
    __tablename__ = 'consultorias'
    cliente_id = db.Column(db.String(36), db.ForeignKey('clients.id'), nullable=False)
    estado = db.Column(db.String(20), nullable=False, default='borrador')
    fecha_inicio = db.Column(db.DateTime(timezone=True))
    notas = db.Column(db.Text)

    cliente = db.relationship('Client', backref=db.backref('consultorias', lazy=True))


class ConsultoriaMensaje(BaseModel):
    __tablename__ = 'consultoria_mensajes'
    consultoria_id = db.Column(db.String(36), db.ForeignKey('consultorias.id'), nullable=False)
    rol = db.Column(db.String(10), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    capa = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime(timezone=True), default=db.func.now())

    consultoria = db.relationship('Consultoria', backref=db.backref('mensajes', lazy=True, cascade='all, delete-orphan'))
```

- [ ] **Step 2: Create twin_asis.py**

Write `core/models/twin_asis.py`:
```python
from core import db
from core.models.base import BaseModel

class TwinASIS(BaseModel):
    __tablename__ = 'twin_asis'
    consultoria_id = db.Column(db.String(36), db.ForeignKey('consultorias.id'), unique=True, nullable=False)
    capas = db.Column(db.JSON, default=dict)
    problemas = db.Column(db.JSON, default=list)
```

- [ ] **Step 3: Create twin_tobe.py**

Write `core/models/twin_tobe.py`:
```python
from core import db
from core.models.base import BaseModel

class TwinTOBE(BaseModel):
    __tablename__ = 'twin_tobe'
    consultoria_id = db.Column(db.String(36), db.ForeignKey('consultorias.id'), unique=True, nullable=False)
    capas = db.Column(db.JSON, default=dict)
    objetivos = db.Column(db.JSON, default=list)
```

- [ ] **Step 4: Create brecha.py**

Write `core/models/brecha.py`:
```python
from core import db
from core.models.base import BaseModel

class Brecha(BaseModel):
    __tablename__ = 'brechas'
    consultoria_id = db.Column(db.String(36), db.ForeignKey('consultorias.id'), nullable=False)
    capa = db.Column(db.String(50), nullable=False)
    problema_actual = db.Column(db.Text, nullable=False)
    estado_deseado = db.Column(db.Text, nullable=False)
    impacto = db.Column(db.String(10), default='media')
    prioridad = db.Column(db.String(10), default='media')
    solucion = db.Column(db.Text)
    sort_order = db.Column(db.Integer, default=0)
```

- [ ] **Step 5: Create plan_recomendado.py**

Write `core/models/plan_recomendado.py`:
```python
from core import db
from core.models.base import BaseModel

class PlanRecomendado(BaseModel):
    __tablename__ = 'planes_recomendados'
    consultoria_id = db.Column(db.String(36), db.ForeignKey('consultorias.id'), unique=True, nullable=False)
    items = db.Column(db.JSON, default=list)
    total_estimado = db.Column(db.Numeric(12, 2), default=0)
    duracion_estimada = db.Column(db.String(50))
```

- [ ] **Step 6: Update models/__init__.py**

Edit `core/models/__init__.py` — add after existing imports:
```python
from core.models.consultoria import Consultoria, ConsultoriaMensaje
from core.models.twin_asis import TwinASIS
from core.models.twin_tobe import TwinTOBE
from core.models.brecha import Brecha
from core.models.plan_recomendado import PlanRecomendado
```
And add to `__all__` list the new model names.

- [ ] **Step 7: Run tables creation**

```bash
cd /c/Users/Usuario/stonelytics/stonelytics
python -c "from core import db; from app import create_app; app = create_app(); app.app_context().push(); db.create_all(); print('OK')"
```

---

### Task 2: AI Prompts Module

**Files:**
- Create: `modules/studio/ai_prompts.py`

**Interfaces:**
- Produces: `get_system_prompt(capa, checklist_progress)` and `CAPAS` checklist dict

- [ ] **Step 1: Create ai_prompts.py**

Write `modules/studio/ai_prompts.py`:
```python
"""AI prompts organized by enterprise layer."""

CAPAS = [
    {
        "id": "proposito",
        "titulo": "Propósito",
        "icono": "target-arrow",
        "preguntas": [
            "¿Cuál es la misión de su empresa? ¿Para qué existe?",
            "¿Cuáles son sus objetivos principales para este año?",
            "¿Quiénes son sus stakeholders clave? (dueños, inversores, junta, etc.)",
            "¿Qué restricciones o regulaciones enfrentan como empresa?",
        ]
    },
    {
        "id": "clientes",
        "titulo": "Clientes",
        "icono": "users",
        "preguntas": [
            "¿Quiénes son sus clientes? ¿Los tiene segmentados por tipo?",
            "¿Cómo adquieren clientes hoy? ¿Cuál es su proceso de venta?",
            "¿Usan algún CRM o herramienta para gestionar clientes?",
            "¿Qué canales de comunicación usan con sus clientes?",
            "¿Cómo miden la satisfacción del cliente?",
        ]
    },
    {
        "id": "servicios",
        "titulo": "Servicios",
        "icono": "package",
        "preguntas": [
            "¿Cuál es su catálogo de productos o servicios?",
            "¿Cómo definen los precios? ¿Tienen diferentes planes?",
            "¿Cómo entregan sus servicios o productos?",
            "¿Tienen SLAs o tiempos de entrega definidos?",
        ]
    },
    {
        "id": "procesos",
        "titulo": "Procesos",
        "icono": "route",
        "preguntas": [
            "¿Cuáles son los procesos críticos de su empresa?",
            "¿Tienen procesos documentados o estandarizados?",
            "¿Qué procesos son manuales hoy?",
            "¿Qué procesos cree que deberían automatizarse?",
        ]
    },
    {
        "id": "personas",
        "titulo": "Personas",
        "icono": "user",
        "preguntas": [
            "¿Cuántas personas trabajan en la empresa? ¿Cómo están organizados?",
            "¿Tienen un organigrama definido?",
            "¿Qué roles o perfiles tienen actualmente?",
            "¿Cómo gestionan permisos y responsabilidades?",
        ]
    },
    {
        "id": "informacion",
        "titulo": "Información",
        "icono": "database",
        "preguntas": [
            "¿Qué datos manejan diariamente? (clientes, ventas, inventario, etc.)",
            "¿Qué documentos generan como empresa? (facturas, contratos, informes)",
            "¿Cómo almacenan y organizan su información?",
            "¿Qué indicadores (KPIs) miden hoy?",
        ]
    },
    {
        "id": "tecnologia",
        "titulo": "Tecnología",
        "icono": "server",
        "preguntas": [
            "¿Qué software o herramientas usan actualmente?",
            "¿Qué problemas les genera su tecnología actual?",
            "¿Tienen página web, landing o presencia digital?",
            "¿Cómo gestionan su infraestructura tecnológica?",
        ]
    },
    {
        "id": "inteligencia",
        "titulo": "Inteligencia",
        "icono": "chart-bar",
        "preguntas": [
            "¿Cómo toman decisiones hoy? ¿Basadas en datos o intuición?",
            "¿Tienen dashboards o reportes automatizados?",
            "¿Usan IA o automatizaciones actualmente?",
            "¿Qué información les gustaría tener para mejorar decisiones?",
        ]
    },
    {
        "id": "gobierno",
        "titulo": "Gobierno",
        "icono": "shield-check",
        "preguntas": [
            "¿Tienen políticas de seguridad de la información?",
            "¿Cómo gestionan riesgos empresariales?",
            "¿Tienen requisitos de cumplimiento normativo o auditoría?",
            "¿Cómo controlan accesos y permisos a la información?",
        ]
    },
    {
        "id": "evolucion",
        "titulo": "Evolución",
        "icono": "trending-up",
        "preguntas": [
            "¿Cómo ha evolucionado su empresa en los últimos 2 años?",
            "¿Tienen un roadmap o plan de crecimiento?",
            "¿Qué proyectos tienen pendientes o en cola?",
            "Si pudiera cambiar algo de su empresa mañana, ¿qué sería?",
        ]
    },
]

PROMPT_SISTEMA_BASE = """Eres un consultor empresarial experto de Stonelytics, una firma de Ingeniería Empresarial. Tu objetivo es entender profundamente cómo funciona la empresa del cliente en cada área.

REGLAS:
1. Haz UNA pregunta a la vez. Sé conversacional, no parezcas un formulario.
2. Basado en la respuesta del usuario, decide:
   a) PROFUNDIZAR si la respuesta es superficial (pide ejemplos concretos)
   b) AVANZAR a la siguiente pregunta si está cubierta
   c) DETECTAR problemas y registrarlos como hallazgos
3. Cuando completes todas las preguntas de una capa, haz un resumen de lo que entendiste.
4. Pregunta "¿Hay algo más que agregar sobre [capa]?" antes de pasar a la siguiente.
5. SIEMPRE responde en español, con tono profesional pero cálido.

CAPA ACTUAL: {capa_actual}
CHECKLIST: {checklist}

RESPONDE EXCLUSIVAMENTE CON UN JSON EN ESTE FORMATO:
{{
    "accion": "preguntar" | "profundizar" | "resumir" | "siguiente_capa" | "completar",
    "mensaje": "Texto visible para el usuario",
    "capa_actual": "{capa_actual}",
    "progreso": {{ "respondidas": N, "total": N }},
    "hallazgos": [{{ "categoria": "problema" | "observacion", "descripcion": "texto", "impacto": "alto" | "medio" | "bajo" }}]
}}
"""

PROMPT_GENERAR_CAPAS = """Basado en la siguiente conversación con un cliente, genera la estructura completa de las 10 capas empresariales.

Conversación:
{conversacion}

Genera un JSON con las 10 capas. Cada capa debe tener contenido estructurado y una lista de problemas detectados.

Formato:
{{
    "capas": {{
        "proposito": {{ "mision": "...", "vision": "...", "objetivos": [...], "stakeholders": [...], "restricciones": [...] }},
        "clientes": {{ "segmentos": [...], "canales": [...], "crm": "...", "proceso_venta": "...", "problemas_cliente": [...] }},
        "servicios": {{ "catalogo": [...], "precios": "...", "entregables": [...], "canales_entrega": [...] }},
        "procesos": {{ "criticos": [...], "documentados": "...", "manuales": [...], "automatizados": [...], "cuello_botella": [...] }},
        "personas": {{ "total_empleados": "...", "organigrama": "...", "roles": [...], "perfiles_clave": [...] }},
        "informacion": {{ "datos_clave": [...], "documentos": [...], "almacenamiento": "...", "kpis_actuales": [...] }},
        "tecnologia": {{ "software_actual": [...], "problemas_tecnologia": [...], "presencia_digital": "...", "infraestructura": "..." }},
        "inteligencia": {{ "toma_decisiones": "...", "dashboards": "...", "ia_actual": "...", "necesidades_informacion": [...] }},
        "gobierno": {{ "politicas_seguridad": "...", "gestion_riesgos": "...", "cumplimiento": "...", "control_accesos": "..." }},
        "evolucion": {{ "historia_cambios": "...", "roadmap": "...", "proyectos_pendientes": [...], "cambio_prioritario": "..." }}
    }},
    "problemas": [
        {{ "capa": "clientes", "descripcion": "...", "impacto": "alto|medio|bajo" }}
    ]
}}
"""

PROMPT_SUGERIR_TOBE = """Eres un consultor experto en transformación digital. Para cada capa de la empresa, sugiere cómo podría mejorar.

Estado actual de la capa "{capa}":
{contenido_actual}

Sugiere un máximo de 3 objetivos concretos para esta capa. Responde en JSON:
{{
    "objetivos": [
        {{ "descripcion": "objetivo", "prioridad": "alta|media|baja" }}
    ]
}}
"""

PROMPT_CALCULAR_BRECHAS = """Calcula las brechas entre el estado actual y el estado deseado de una empresa.

Capa: {capa}
Estado Actual: {estado_actual}
Estado Deseado: {estado_deseado}

Genera brechas específicas y accionables. Responde en JSON:
{{
    "brechas": [
        {{
            "problema_actual": "descripción del problema",
            "estado_deseado": "cómo debería ser",
            "impacto": "alto|medio|bajo",
            "solucion_sugerida": "posible solución"
        }}
    ]
}}
"""

def get_system_prompt(capa_actual: str, preguntas_respondidas: list) -> str:
    """Build the system prompt for the current interview layer."""
    capa_info = next((c for c in CAPAS if c["id"] == capa_actual), CAPAS[0])
    todas = capa_info["preguntas"]
    respondidas = [p for p in todas if p in preguntas_respondidas]
    faltantes = [p for p in todas if p not in preguntas_respondidas]
    checklist = f"Respondidas: {len(respondidas)}/{len(todas)}"
    if faltantes:
        checklist += "\nPendientes:\n" + "\n".join(f"- {p}" for p in faltantes)
    return PROMPT_SISTEMA_BASE.format(capa_actual=capa_actual, checklist=checklist)
```

---

### Task 3: SRIE Mapper

**Files:**
- Create: `modules/studio/srie_mapper.py`

**Interfaces:**
- Consumes: list of Brecha objects from models
- Produces: `mapping_rules` dict and `map_brechas_to_soluciones(brechas, capabilities)` function

- [ ] **Step 1: Create srie_mapper.py**

Write `modules/studio/srie_mapper.py`:
```python
"""Maps enterprise gaps to Stonelytics solutions."""

MAPPING_RULES = [
    {
        "keywords": ["crm", "clientes", "ventas", "seguimiento", "oportunidades", "leads"],
        "solucion": "StoneCRM",
        "descripcion": "Sistema de gestión de clientes y ventas",
        "slug_capacidad": "stonecrm",
    },
    {
        "keywords": ["automatización", "automatizar", "manual", "proceso", "flujo", "bpmn", "sop", "workflow"],
        "solucion": "StoneFlow",
        "descripcion": "Automatización de procesos empresariales",
        "slug_capacidad": "stoneflow",
    },
    {
        "keywords": ["dashboard", "reporte", "indicador", "kpi", "métrica", "datos", "power bi", "grafico", "analítica"],
        "solucion": "StoneData",
        "descripcion": "Dashboards e inteligencia de negocio",
        "slug_capacidad": "stonedata",
    },
    {
        "keywords": ["documento", "word", "pdf", "informe", "plantilla", "documentación", "formato"],
        "solucion": "StoneDocs",
        "descripcion": "Generación y gestión de documentos empresariales",
        "slug_capacidad": "stonedocs",
    },
    {
        "keywords": ["página web", "landing", "sitio web", "presencia digital", "website"],
        "solucion": "StoneLanding",
        "descripcion": "Landing page y presencia digital profesional",
        "slug_capacidad": "stonelanding",
    },
    {
        "keywords": ["chatbot", "chat", "atención", "soporte", "preguntas", "whatsapp", "bot"],
        "solucion": "StoneAI",
        "descripcion": "Asistente inteligente con IA para atención al cliente",
        "slug_capacidad": "stoneai",
    },
    {
        "keywords": ["base documental", "conocimiento", "wiki", "manual", "procedimiento", "rag"],
        "solucion": "StoneRAG",
        "descripcion": "Base de conocimiento empresarial con IA",
        "slug_capacidad": "stonerag",
    },
    {
        "keywords": ["contrato", "legal", "abogado", "términos", "condiciones", "documento legal"],
        "solucion": "StoneLegal",
        "descripcion": "Gestión de contratos y documentos legales",
        "slug_capacidad": "stonelegal",
    },
    {
        "keywords": ["finanzas", "contabilidad", "factura", "cobro", "presupuesto", "contable", "impuesto"],
        "solucion": "StoneFinance",
        "descripcion": "Gestión financiera y contable",
        "slug_capacidad": "stonefinance",
    },
    {
        "keywords": ["empleado", "rrhh", "personas", "talento", "nomina", "recurso humano", "colaborador"],
        "solucion": "StonePeople",
        "descripcion": "Portal de empleados y gestión de talento",
        "slug_capacidad": "stonepeople",
    },
    {
        "keywords": ["formulario", "encuesta", "registro", "inscripción", "form"],
        "solucion": "StoneForms",
        "descripcion": "Formularios inteligentes y recolección de datos",
        "slug_capacidad": "stoneforms",
    },
    {
        "keywords": ["infraestructura", "servidor", "nube", "cloud", "devops", "despliegue", "docker"],
        "solucion": "StoneDeploy",
        "descripcion": "Infraestructura cloud y despliegue automatizado",
        "slug_capacidad": "stonedeploy",
    },
]


def map_brechas_to_soluciones(brechas: list, capabilities_query):
    """Map a list of Brecha objects to recommended solutions.
    
    Returns list of dicts: {modulo, descripcion, slug, precio, brecha_id, justificacion}
    """
    from difflib import SequenceMatcher
    
    recomendaciones = []
    slugs_vistos = set()
    
    for brecha in brechas:
        texto = f"{brecha.problema_actual} {brecha.solucion or ''}".lower()
        for rule in MAPPING_RULES:
            for kw in rule["keywords"]:
                if kw in texto or any(SequenceMatcher(None, kw, texto.split()).ratio() > 0.8 for _ in [1]):
                    if rule["slug_capacidad"] not in slugs_vistos:
                        slugs_vistos.add(rule["slug_capacidad"])
                        capability = capabilities_query.filter_by(
                            slug=rule["slug_capacidad"]
                        ).first() if hasattr(capabilities_query, 'filter_by') else None
                        
                        precio = float(capability.price) if capability and hasattr(capability, 'price') else 0
                        
                        recomendaciones.append({
                            "modulo": rule["solucion"],
                            "descripcion": rule["descripcion"],
                            "slug": rule["slug_capacidad"],
                            "precio": precio,
                            "brecha_id": brecha.id,
                            "justificacion": f"Se detectó necesidad de {rule['descripcion'].lower()} basado en: {brecha.problema_actual[:100]}",
                        })
                    break
    
    return recomendaciones


def get_all_soluciones():
    """Return all possible solutions (for manual selection)."""
    return [
        {"modulo": r["solucion"], "descripcion": r["descripcion"], "slug": r["slug_capacidad"]}
        for r in MAPPING_RULES
    ]
```

---

### Task 4: Services — Entrevista IA, Twin, Brecha, Plan

**Files:**
- Create: `modules/studio/services.py`

**Interfaces:**
- Consumes: all models created in Task 1, AI prompts from Task 2, SRIE mapper from Task 3
- Produces: `EntrevistaIAService`, `TwinService`, `BrechaService`, `PlanService`

- [ ] **Step 1: Create services.py**

Write `modules/studio/services.py`:
```python
"""Services for Stonelytics Studio: AI interview, twins, gaps, and plan generation."""
import json
import os
import logging
from datetime import datetime, timezone

from core import db
from core.models import Client
from core.models.consultoria import Consultoria, ConsultoriaMensaje
from core.models.twin_asis import TwinASIS
from core.models.twin_tobe import TwinTOBE
from core.models.brecha import Brecha
from core.models.plan_recomendado import PlanRecomendado

from modules.studio.ai_prompts import CAPAS, get_system_prompt, PROMPT_GENERAR_CAPAS, PROMPT_SUGERIR_TOBE, PROMPT_CALCULAR_BRECHAS
from modules.studio.srie_mapper import map_brechas_to_soluciones

logger = logging.getLogger(__name__)


class OpenAIClient:
    """Minimal OpenAI client wrapper."""
    
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
        }
        if response_format:
            payload["response_format"] = response_format
        
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers, json=payload, timeout=60
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


class EntrevistaIAService:
    
    def __init__(self):
        self.ai = OpenAIClient()
    
    def procesar_mensaje(self, consultoria_id: str, mensaje_usuario: str) -> dict:
        """Process a user message and return the AI response."""
        consultoria = Consultoria.query.get(consultoria_id)
        if not consultoria:
            raise ValueError("Consultoría no encontrada")
        
        # Get conversation history
        historial = ConsultoriaMensaje.query.filter_by(
            consultoria_id=consultoria_id
        ).order_by(ConsultoriaMensaje.timestamp).all()
        
        # Determine current layer from last AI message
        capa_actual = self._determinar_capa_actual(historial)
        preguntas_respondidas = self._get_preguntas_respondidas(historial, capa_actual)
        
        # Build messages for AI
        system_prompt = get_system_prompt(capa_actual, preguntas_respondidas)
        messages = [{"role": "system", "content": system_prompt}]
        
        for msg in historial[-20:]:  # Last 20 messages for context
            role = "assistant" if msg.rol == "ia" else "user"
            messages.append({"role": role, "content": msg.contenido})
        
        messages.append({"role": "user", "content": mensaje_usuario})
        
        # Save user message
        user_msg = ConsultoriaMensaje(
            consultoria_id=consultoria_id,
            rol="usuario",
            contenido=mensaje_usuario,
            capa=capa_actual,
        )
        db.session.add(user_msg)
        db.session.flush()
        
        # Get AI response
        try:
            respuesta_raw = self.ai.chat(messages)
            respuesta = json.loads(respuesta_raw)
        except Exception as e:
            logger.error(f"AI error: {e}")
            respuesta = {
                "accion": "preguntar",
                "mensaje": "Disculpa, no entendí bien. ¿Podrías explicarlo de otra forma?",
                "capa_actual": capa_actual,
                "progreso": {"respondidas": len(preguntas_respondidas), "total": len(self._get_preguntas_totales(capa_actual))},
                "hallazgos": [],
            }
        
        ai_content = respuesta.get("mensaje", "¿Podrías contarme más?")
        siguiente_capa = respuesta.get("capa_actual", capa_actual)
        
        # Save AI message
        ai_msg = ConsultoriaMensaje(
            consultoria_id=consultoria_id,
            rol="ia",
            contenido=ai_content,
            capa=siguiente_capa,
        )
        db.session.add(ai_msg)
        
        # Save findings as notes
        hallazgos = respuesta.get("hallazgos", [])
        if hallazgos:
            notas_extra = []
            for h in hallazgos:
                notas_extra.append(f"[{h.get('impacto','medio').upper()}] {h.get('categoria','')}: {h.get('descripcion','')}")
            if notas_extra:
                consultoria.notas = (consultoria.notas or "") + "\n" + "\n".join(notas_extra)
        
        # Update interview completion
        if respuesta.get("accion") == "completar":
            consultoria.estado = "activa"
        
        db.session.commit()
        
        return {
            "mensaje": ai_content,
            "capa_actual": siguiente_capa,
            "accion": respuesta.get("accion", "preguntar"),
            "progreso": respuesta.get("progreso", {"respondidas": 0, "total": 0}),
            "hallazgos": hallazgos,
        }
    
    def generar_twin_asis(self, consultoria_id: str) -> dict:
        """Generate the AS IS twin from completed interview."""
        consultoria = Consultoria.query.get(consultoria_id)
        if not consultoria:
            raise ValueError("Consultoría no encontrada")
        
        # Get all messages
        mensajes = ConsultoriaMensaje.query.filter_by(
            consultoria_id=consultoria_id
        ).order_by(ConsultoriaMensaje.timestamp).all()
        
        conversacion = "\n".join(
            f"{'Cliente' if m.rol == 'usuario' else 'Consultor'}: {m.contenido}"
            for m in mensajes
        )
        
        prompt = PROMPT_GENERAR_CAPAS.format(conversacion=conversacion)
        
        try:
            ai = OpenAIClient()
            respuesta_raw = ai.chat([
                {"role": "system", "content": "Eres un consultor empresarial experto. Genera estructuras JSON precisas basadas en la conversación."},
                {"role": "user", "content": prompt},
            ])
            resultado = json.loads(respuesta_raw)
        except Exception as e:
            logger.error(f"Error generating twin AS IS: {e}")
            resultado = {"capas": {}, "problemas": []}
        
        # Save or update twin
        twin = TwinASIS.query.filter_by(consultoria_id=consultoria_id).first()
        if twin:
            twin.capas = resultado.get("capas", {})
            twin.problemas = resultado.get("problemas", [])
        else:
            twin = TwinASIS(
                consultoria_id=consultoria_id,
                capas=resultado.get("capas", {}),
                problemas=resultado.get("problemas", []),
            )
            db.session.add(twin)
        
        db.session.commit()
        return twin.to_dict()
    
    def _determinar_capa_actual(self, historial):
        """Determine which layer the interview is currently on."""
        mensajes_ia = [m for m in historial if m.rol == "ia" and m.capa]
        if mensajes_ia:
            ultimo = mensajes_ia[-1]
            for i, capa in enumerate(CAPAS):
                if capa["id"] == ultimo.capa:
                    return capa["id"]
        return CAPAS[0]["id"]
    
    def _get_preguntas_respondidas(self, historial, capa):
        capa_info = next((c for c in CAPAS if c["id"] == capa), None)
        if not capa_info:
            return []
        return [p for p in capa_info["preguntas"] 
                if any(p.lower() in m.contenido.lower() or m.contenido.lower()[:20] in p.lower() 
                       for m in historial if m.capa == capa)]
    
    def _get_preguntas_totales(self, capa):
        capa_info = next((c for c in CAPAS if c["id"] == capa), None)
        return capa_info["preguntas"] if capa_info else []


class TwinService:
    
    @staticmethod
    def get_asis(consultoria_id: str) -> dict:
        twin = TwinASIS.query.filter_by(consultoria_id=consultoria_id).first()
        return twin.to_dict() if twin else {"capas": {}, "problemas": []}
    
    @staticmethod
    def update_asis(consultoria_id: str, capas: dict) -> TwinASIS:
        twin = TwinASIS.query.filter_by(consultoria_id=consultoria_id).first()
        if twin:
            twin.capas = capas
        else:
            twin = TwinASIS(consultoria_id=consultoria_id, capas=capas)
            db.session.add(twin)
        db.session.commit()
        return twin
    
    @staticmethod
    def get_tobe(consultoria_id: str) -> dict:
        twin = TwinTOBE.query.filter_by(consultoria_id=consultoria_id).first()
        return twin.to_dict() if twin else {"capas": {}, "objetivos": []}
    
    @staticmethod
    def update_tobe(consultoria_id: str, capas: dict) -> TwinTOBE:
        twin = TwinTOBE.query.filter_by(consultoria_id=consultoria_id).first()
        if twin:
            twin.capas = capas
        else:
            twin = TwinTOBE(consultoria_id=consultoria_id, capas=capas)
            db.session.add(twin)
        db.session.commit()
        return twin
    
    @staticmethod
    def sugerir_tobe(capa: str, contenido_actual: dict) -> list:
        """Ask AI to suggest improvements for a layer."""
        try:
            ai = OpenAIClient()
            prompt = PROMPT_SUGERIR_TOBE.format(
                capa=capa,
                contenido_actual=json.dumps(contenido_actual, indent=2, ensure_ascii=False),
            )
            respuesta_raw = ai.chat([
                {"role": "system", "content": "Eres un consultor experto en transformación digital."},
                {"role": "user", "content": prompt},
            ])
            resultado = json.loads(respuesta_raw)
            return resultado.get("objetivos", [])
        except Exception:
            return []


class BrechaService:
    
    @staticmethod
    def get_brechas(consultoria_id: str) -> list:
        return Brecha.query.filter_by(consultoria_id=consultoria_id).order_by(Brecha.sort_order).all()
    
    @staticmethod
    def calcular_brechas(consultoria_id: str) -> list:
        """Calculate gaps between AS IS and TO BE for all layers."""
        twin_asis = TwinASIS.query.filter_by(consultoria_id=consultoria_id).first()
        twin_tobe = TwinTOBE.query.filter_by(consultoria_id=consultoria_id).first()
        
        if not twin_asis or not twin_tobe:
            raise ValueError("Se requieren ambos gemelos (AS IS y TO BE)")
        
        # Delete existing gaps
        Brecha.query.filter_by(consultoria_id=consultoria_id).delete()
        
        brechas_creadas = []
        for capa_info in CAPAS:
            capa_id = capa_info["id"]
            contenido_asis = twin_asis.capas.get(capa_id, {})
            contenido_tobe = twin_tobe.capas.get(capa_id, {})
            
            if not contenido_tobe:
                continue
            
            try:
                ai = OpenAIClient()
                prompt = PROMPT_CALCULAR_BRECHAS.format(
                    capa=capa_info["titulo"],
                    estado_actual=json.dumps(contenido_asis, indent=2, ensure_ascii=False),
                    estado_deseado=json.dumps(contenido_tobe, indent=2, ensure_ascii=False),
                )
                respuesta_raw = ai.chat([
                    {"role": "system", "content": "Eres un analista experto en brechas empresariales."},
                    {"role": "user", "content": prompt},
                ])
                resultado = json.loads(respuesta_raw)
                
                for i, b in enumerate(resultado.get("brechas", [])):
                    brecha = Brecha(
                        consultoria_id=consultoria_id,
                        capa=capa_id,
                        problema_actual=b.get("problema_actual", ""),
                        estado_deseado=b.get("estado_deseado", ""),
                        impacto=b.get("impacto", "media"),
                        prioridad=b.get("impacto", "media"),
                        solucion=b.get("solucion_sugerida", ""),
                        sort_order=i,
                    )
                    db.session.add(brecha)
                    brechas_creadas.append(brecha)
            except Exception as e:
                logger.error(f"Error calculating gaps for {capa_id}: {e}")
        
        db.session.commit()
        return brechas_creadas
    
    @staticmethod
    def update_brecha(brecha_id: str, data: dict) -> Brecha:
        brecha = Brecha.query.get(brecha_id)
        if not brecha:
            raise ValueError("Brecha no encontrada")
        if "impacto" in data:
            brecha.impacto = data["impacto"]
        if "prioridad" in data:
            brecha.prioridad = data["prioridad"]
        if "solucion" in data:
            brecha.solucion = data["solucion"]
        db.session.commit()
        return brecha


class PlanService:
    
    @staticmethod
    def generar_plan(consultoria_id: str) -> dict:
        """Generate recommended plan from gaps using SRIE mapper."""
        from core.models.capability import Capability
        
        brechas = Brecha.query.filter_by(consultoria_id=consultoria_id).all()
        capabilities = Capability.query
        
        items = map_brechas_to_soluciones(brechas, capabilities)
        total = sum(item.get("precio", 0) for item in items)
        
        plan = PlanRecomendado.query.filter_by(consultoria_id=consultoria_id).first()
        if plan:
            plan.items = items
            plan.total_estimado = total
        else:
            plan = PlanRecomendado(
                consultoria_id=consultoria_id,
                items=items,
                total_estimado=total,
            )
            db.session.add(plan)
        
        db.session.commit()
        return {"items": items, "total_estimado": float(total)}
    
    @staticmethod
    def get_plan(consultoria_id: str) -> dict:
        plan = PlanRecomendado.query.filter_by(consultoria_id=consultoria_id).first()
        if not plan:
            return {"items": [], "total_estimado": 0}
        return {"items": plan.items, "total_estimado": float(plan.total_estimado), "id": plan.id}
```

---

### Task 5: Blueprint Routes

**Files:**
- Create: `modules/studio/__init__.py`
- Create: `modules/studio/routes.py`

**Interfaces:**
- Consumes: services from Task 4
- Produces: Flask blueprint with 9 screen routes

- [ ] **Step 1: Create modules/studio/__init__.py**

```python
from modules.studio.routes import studio_bp
```

- [ ] **Step 2: Create modules/studio/routes.py**

```python
"""Stonelytics Studio routes."""
from __future__ import annotations

import json
from datetime import datetime, timezone

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required

from core import db
from core.models import Client
from core.models.consultoria import Consultoria
from core.models.quotation import Quotation
from core.services.quotation_service import QuotationService
from core.services.pdf_service import generate_quotation_pdf

from modules.studio.services import EntrevistaIAService, TwinService, BrechaService, PlanService

studio_bp = Blueprint('studio', __name__, template_folder='templates')

# Initialize services
entrevista_service = EntrevistaIAService()
twin_service = TwinService()
brecha_service = BrechaService()
plan_service = PlanService()


@studio_bp.route('/')
@login_required
def dashboard():
    consultorias = Consultoria.query.order_by(Consultoria.created_at.desc()).all()
    stats = {
        'total': len(consultorias),
        'activas': sum(1 for c in consultorias if c.estado == 'activa'),
        'completadas': sum(1 for c in consultorias if c.estado == 'completada'),
        'borradores': sum(1 for c in consultorias if c.estado == 'borrador'),
    }
    return render_template('studio/dashboard.html', consultorias=consultorias, stats=stats, active_page='studio')


@studio_bp.route('/nueva', methods=['GET', 'POST'])
@login_required
def nueva_consultoria():
    if request.method == 'POST':
        client_id = request.form.get('client_id')
        if not client_id:
            flash('Selecciona un cliente', 'error')
            return redirect(url_for('studio.nueva_consultoria'))
        
        consultoria = Consultoria(
            cliente_id=client_id,
            estado='borrador',
            fecha_inicio=datetime.now(timezone.utc),
        )
        db.session.add(consultoria)
        db.session.commit()
        
        flash('Consultoría creada. Iniciemos la entrevista.', 'success')
        return redirect(url_for('studio.entrevista', consultoria_id=consultoria.id))
    
    clients = Client.query.order_by(Client.company_name).all()
    return render_template('studio/seleccionar_cliente.html', clients=clients, active_page='studio')


@studio_bp.route('/<consultoria_id>/entrevista')
@login_required
def entrevista(consultoria_id: str):
    consultoria = Consultoria.query.get_or_404(consultoria_id)
    return render_template('studio/entrevista.html', consultoria=consultoria, active_page='studio')


@studio_bp.route('/api/<consultoria_id>/mensaje', methods=['POST'])
@login_required
def enviar_mensaje(consultoria_id: str):
    consultoria = Consultoria.query.get_or_404(consultoria_id)
    data = request.get_json()
    mensaje = data.get('mensaje', '')
    
    try:
        resultado = entrevista_service.procesar_mensaje(consultoria_id, mensaje)
        return jsonify({'ok': True, **resultado})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@studio_bp.route('/api/<consultoria_id>/generar-twin', methods=['POST'])
@login_required
def generar_twin(consultoria_id: str):
    try:
        twin = entrevista_service.generar_twin_asis(consultoria_id)
        return jsonify({'ok': True, 'twin': twin})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@studio_bp.route('/<consultoria_id>/gemelo-asis')
@login_required
def gemelo_asis(consultoria_id: str):
    consultoria = Consultoria.query.get_or_404(consultoria_id)
    twin = twin_service.get_asis(consultoria_id)
    return render_template('studio/gemelo_asis.html', consultoria=consultoria, twin=twin, active_page='studio')


@studio_bp.route('/api/<consultoria_id>/gemelo-asis', methods=['PUT'])
@login_required
def actualizar_gemelo_asis(consultoria_id: str):
    data = request.get_json()
    twin_service.update_asis(consultoria_id, data.get('capas', {}))
    return jsonify({'ok': True})


@studio_bp.route('/<consultoria_id>/gemelo-tobe')
@login_required
def gemelo_tobe(consultoria_id: str):
    consultoria = Consultoria.query.get_or_404(consultoria_id)
    twin_asis = twin_service.get_asis(consultoria_id)
    twin_tobe = twin_service.get_tobe(consultoria_id)
    return render_template('studio/gemelo_tobe.html', consultoria=consultoria, twin_asis=twin_asis, twin_tobe=twin_tobe, active_page='studio')


@studio_bp.route('/api/<consultoria_id>/gemelo-tobe', methods=['PUT'])
@login_required
def actualizar_gemelo_tobe(consultoria_id: str):
    data = request.get_json()
    twin_service.update_tobe(consultoria_id, data.get('capas', {}))
    return jsonify({'ok': True})


@studio_bp.route('/api/<consultoria_id>/sugerir-tobe', methods=['POST'])
@login_required
def sugerir_tobe(consultoria_id: str):
    data = request.get_json()
    capa = data.get('capa', '')
    contenido = data.get('contenido', {})
    objetivos = twin_service.sugerir_tobe(capa, contenido)
    return jsonify({'ok': True, 'objetivos': objetivos})


@studio_bp.route('/<consultoria_id>/brechas')
@login_required
def brechas(consultoria_id: str):
    consultoria = Consultoria.query.get_or_404(consultoria_id)
    brechas_list = brecha_service.get_brechas(consultoria_id)
    return render_template('studio/brechas.html', consultoria=consultoria, brechas=brechas_list, active_page='studio')


@studio_bp.route('/api/<consultoria_id>/calcular-brechas', methods=['POST'])
@login_required
def calcular_brechas(consultoria_id: str):
    try:
        brechas_list = brecha_service.calcular_brechas(consultoria_id)
        return jsonify({'ok': True, 'total': len(brechas_list)})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@studio_bp.route('/api/brechas/<brecha_id>', methods=['PUT'])
@login_required
def actualizar_brecha(brecha_id: str):
    data = request.get_json()
    brecha_service.update_brecha(brecha_id, data)
    return jsonify({'ok': True})


@studio_bp.route('/<consultoria_id>/plan')
@login_required
def plan(consultoria_id: str):
    consultoria = Consultoria.query.get_or_404(consultoria_id)
    plan_data = plan_service.get_plan(consultoria_id)
    return render_template('studio/plan.html', consultoria=consultoria, plan=plan_data, active_page='studio')


@studio_bp.route('/api/<consultoria_id>/generar-plan', methods=['POST'])
@login_required
def generar_plan(consultoria_id: str):
    try:
        plan_data = plan_service.generar_plan(consultoria_id)
        return jsonify({'ok': True, **plan_data})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@studio_bp.route('/<consultoria_id>/cotizacion', methods=['GET', 'POST'])
@login_required
def cotizacion(consultoria_id: str):
    consultoria = Consultoria.query.get_or_404(consultoria_id)
    plan_data = plan_service.get_plan(consultoria_id)
    
    if request.method == 'POST':
        try:
            quotation = QuotationService.create(
                client_id=consultoria.cliente_id,
                title=request.form.get('title', f'Plan Empresarial - {consultoria.cliente.company_name}'),
                items=json.loads(request.form.get('items', '[]')),
                scope=request.form.get('scope', ''),
                discount_pct=float(request.form.get('discount_pct', 0)),
                created_by=str(consultoria.id),
            )
            consultoria.estado = 'completada'
            db.session.commit()
            flash(f'Cotización {quotation.quotation_number} creada', 'success')
            return redirect(url_for('studio.propuesta', consultoria_id=consultoria_id))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    from core.models.capability import Capability
    capabilities = Capability.query.filter_by(is_active_=True).all()
    
    return render_template('studio/cotizacion.html', consultoria=consultoria, plan=plan_data, capabilities=capabilities, active_page='studio')


@studio_bp.route('/<consultoria_id>/propuesta')
@login_required
def propuesta(consultoria_id: str):
    consultoria = Consultoria.query.get_or_404(consultoria_id)
    quotation = Quotation.query.filter_by(created_by=str(consultoria_id)).order_by(Quotation.created_at.desc()).first()
    
    twin_asis = twin_service.get_asis(consultoria_id)
    twin_tobe = twin_service.get_tobe(consultoria_id)
    brechas_list = brecha_service.get_brechas(consultoria_id)
    plan_data = plan_service.get_plan(consultoria_id)
    
    return render_template('studio/propuesta.html', consultoria=consultoria, quotation=quotation,
                          twin_asis=twin_asis, twin_tobe=twin_tobe, brechas=brechas_list,
                          plan=plan_data, active_page='studio')


@studio_bp.route('/<consultoria_id>/pdf')
@login_required
def descargar_pdf(consultoria_id: str):
    quotation = Quotation.query.filter_by(created_by=str(consultoria_id)).order_by(Quotation.created_at.desc()).first()
    if not quotation:
        flash('Primero genera la cotización', 'error')
        return redirect(url_for('studio.propuesta', consultoria_id=consultoria_id))
    
    try:
        pdf_buffer = generate_quotation_pdf(quotation)
        from flask import send_file
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'propuesta-{quotation.quotation_number}.pdf',
        )
    except Exception as e:
        flash(f'Error generando PDF: {str(e)}', 'error')
        return redirect(url_for('studio.propuesta', consultoria_id=consultoria_id))


@studio_bp.route('/api/clientes/search')
@login_required
def clientes_search():
    q = request.args.get('q', '')
    clients = Client.query.filter(
        Client.company_name.ilike(f'%{q}%') | Client.contact_name.ilike(f'%{q}%')
    ).limit(10).all()
    return jsonify([{'id': c.id, 'text': f'{c.company_name} - {c.contact_name}'} for c in clients])
```

---

### Task 6: Templates (9 screens)

**Files:**
- Create: `templates/studio/dashboard.html`
- Create: `templates/studio/seleccionar_cliente.html`
- Create: `templates/studio/entrevista.html`
- Create: `templates/studio/gemelo_asis.html`
- Create: `templates/studio/gemelo_tobe.html`
- Create: `templates/studio/brechas.html`
- Create: `templates/studio/plan.html`
- Create: `templates/studio/cotizacion.html`
- Create: `templates/studio/propuesta.html`

- [ ] **Step 1-9: Create each template**

Each template follows the admin layout pattern. Here are the first 3 templates (critical ones); remaining 6 follow the same pattern.

**dashboard.html:**
```html
{% extends "base.html" %}
{% block title %}Studio — Stonelytics{% endblock %}
{% block extra_css %}<link rel="stylesheet" href="/static/css/admin.css"><link rel="stylesheet" href="/static/css/studio.css">{% endblock %}
{% block body %}
<div class="admin-layout">
  {% set active_page = 'studio' %}
  {% include "admin/_sidebar.html" %}
  <main class="admin-main">
    <header class="admin-header">
      <h1>Studio — Consultorías</h1>
      <a href="/studio/nueva" class="btn btn--primary btn--sm"><i class="ti ti-plus"></i> Nueva Consultoría</a>
    </header>
    <div class="admin-content">
      <div class="admin-stats">
        <div class="admin-stat">
          <div class="admin-stat__icon" style="background:rgba(37,99,235,0.1);color:var(--accent-blue);"><i class="ti ti-folder"></i></div>
          <div><span class="admin-stat__value">{{ stats.total }}</span><span class="admin-stat__label">Total</span></div>
        </div>
        <div class="admin-stat">
          <div class="admin-stat__icon" style="background:rgba(16,185,129,0.1);color:var(--accent-green);"><i class="ti ti-message-chatbot"></i></div>
          <div><span class="admin-stat__value">{{ stats.activas }}</span><span class="admin-stat__label">En entrevista</span></div>
        </div>
        <div class="admin-stat">
          <div class="admin-stat__icon" style="background:rgba(217,119,6,0.1);color:var(--accent-amber);"><i class="ti ti-file-text"></i></div>
          <div><span class="admin-stat__value">{{ stats.completadas }}</span><span class="admin-stat__label">Completadas</span></div>
        </div>
        <div class="admin-stat">
          <div class="admin-stat__icon" style="background:rgba(99,102,241,0.1);color:var(--accent-indigo);"><i class="ti ti-clock"></i></div>
          <div><span class="admin-stat__value">{{ stats.borradores }}</span><span class="admin-stat__label">Borrador</span></div>
        </div>
      </div>
      <div class="admin-card">
        <div class="admin-card__header"><h3>Consultorías</h3></div>
        <div class="admin-card__body">
          <table class="admin-table">
            <thead><tr><th>Cliente</th><th>Estado</th><th>Fecha</th><th>Acciones</th></tr></thead>
            <tbody>
              {% for c in consultorias %}
              <tr>
                <td><strong>{{ c.cliente.company_name }}</strong><br><small style="color:var(--text-muted)">{{ c.cliente.contact_name }}</small></td>
                <td><span class="badge badge--{{ 'success' if c.estado == 'completada' else 'warning' if c.estado == 'activa' else 'outline' }}">{{ c.estado }}</span></td>
                <td>{{ c.created_at.strftime('%d/%m/%Y') if c.created_at else '—' }}</td>
                <td>
                  <a href="/studio/{{ c.id }}/entrevista" class="btn btn--sm btn--outline">Entrevista</a>
                  <a href="/studio/{{ c.id }}/gemelo-asis" class="btn btn--sm btn--outline">Gemelo</a>
                  <a href="/studio/{{ c.id }}/propuesta" class="btn btn--sm btn--outline">Propuesta</a>
                </td>
              </tr>
              {% else %}
              <tr><td colspan="4" style="text-align:center;padding:40px;color:var(--text-muted);">No hay consultorías aún. <a href="/studio/nueva">Crear la primera</a></td></tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </main>
</div>
{% endblock %}
```

**seleccionar_cliente.html:**
```html
{% extends "base.html" %}
{% block title %}Nueva Consultoría — Studio{% endblock %}
{% block extra_css %}<link rel="stylesheet" href="/static/css/admin.css"><link rel="stylesheet" href="/static/css/studio.css">{% endblock %}
{% block body %}
<div class="admin-layout">
  {% set active_page = 'studio' %}
  {% include "admin/_sidebar.html" %}
  <main class="admin-main">
    <header class="admin-header"><h1>Nueva Consultoría</h1></header>
    <div class="admin-content">
      <div class="admin-form" style="max-width:500px;">
        <form method="POST">
          <div class="form-group">
            <label>Seleccionar Cliente</label>
            <select name="client_id" required class="client-select" style="width:100%;padding:12px;border:1.5px solid var(--border);border-radius:8px;">
              <option value="">— Selecciona un cliente —</option>
              {% for client in clients %}
              <option value="{{ client.id }}">{{ client.company_name }} — {{ client.contact_name }}</option>
              {% endfor %}
            </select>
          </div>
          <p style="color:var(--text-muted);font-size:0.85rem;margin-bottom:20px;">¿No encuentras al cliente? <a href="/admin/clients/new" target="_blank">Crear nuevo cliente</a></p>
          <button type="submit" class="btn btn--primary" style="width:100%;padding:14px;">Iniciar Entrevista</button>
        </form>
      </div>
    </div>
  </main>
</div>
{% endblock %}
```

**entrevista.html:**
```html
{% extends "base.html" %}
{% block title %}Entrevista — {{ consultoria.cliente.company_name }}{% endblock %}
{% block extra_css %}<link rel="stylesheet" href="/static/css/admin.css"><link rel="stylesheet" href="/static/css/studio.css">{% endblock %}
{% block body %}
<div class="admin-layout">
  {% set active_page = 'studio' %}
  {% include "admin/_sidebar.html" %}
  <main class="admin-main">
    <header class="admin-header">
      <h1>Entrevista: {{ consultoria.cliente.company_name }}</h1>
      <div style="display:flex;gap:8px;align-items:center;">
        <span id="capa-indicator" style="font-size:0.85rem;color:var(--text-muted);">Capa 1 de 10</span>
        <button id="btn-finalizar" class="btn btn--sm btn--primary" onclick="finalizarEntrevista()" style="display:none;">Generar Gemelo Digital</button>
      </div>
    </header>
    <div class="admin-content">
      <div id="chat-container" class="studio-chat">
        <div id="chat-messages" class="studio-chat__messages">
          <div class="studio-chat__message studio-chat__message--ia">
            <div class="studio-chat__avatar"><i class="ti ti-robot"></i></div>
            <div class="studio-chat__bubble">
              <p>¡Hola! Soy el asistente de Stonelytics. Voy a ayudarte a construir el diagnóstico empresarial de <strong>{{ consultoria.cliente.company_name }}</strong>.</p>
              <p>Empecemos por el principio: <strong>¿Cuál es la misión de su empresa? ¿Para qué existe?</strong></p>
            </div>
          </div>
        </div>
        <div class="studio-chat__progress">
          <div class="studio-chat__progress-bar" id="progress-bar" style="width:0%"></div>
        </div>
        <div class="studio-chat__input">
          <textarea id="chat-input" placeholder="Escribe tu respuesta aquí..." rows="2" style="width:100%;padding:12px;border:1.5px solid var(--border);border-radius:8px;font-family:inherit;resize:none;"></textarea>
          <button id="btn-enviar" class="btn btn--primary" onclick="enviarMensaje()">Enviar</button>
        </div>
        <div id="typing-indicator" class="studio-chat__typing" style="display:none;">
          <span class="dot"></span><span class="dot"></span><span class="dot"></span>
        </div>
      </div>
    </div>
  </main>
</div>
{% endblock %}
{% block scripts %}
{{ super() }}
<script src="/static/studio/entrevista.js"></script>
<script>const CONSULTORIA_ID = '{{ consultoria.id }}';</script>
{% endblock %}
```

For brevity, the remaining 6 templates (gemelo_asis.html, gemelo_tobe.html, brechas.html, plan.html, cotizacion.html, propuesta.html) follow the same pattern. They will be created during implementation with their full content.

---

### Task 7: Static JS — Alpine.js Components

**Files:**
- Create: `static/studio/entrevista.js`
- Create: `static/studio/gemelo.js`
- Create: `static/css/studio.css`

- [ ] **Step 1: Create entrevista.js**

```javascript
// Stonelytics Studio — Interview Chat
const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const btnEnviar = document.getElementById('btn-enviar');
const typingIndicator = document.getElementById('typing-indicator');
const progressBar = document.getElementById('progress-bar');
const capaIndicator = document.getElementById('capa-indicator');
const btnFinalizar = document.getElementById('btn-finalizar');

let isProcessing = false;

function addMessage(text, isIA) {
    const div = document.createElement('div');
    div.className = 'studio-chat__message studio-chat__message--' + (isIA ? 'ia' : 'user');
    div.innerHTML = `
        <div class="studio-chat__avatar"><i class="ti ti-${isIA ? 'robot' : 'user'}"></i></div>
        <div class="studio-chat__bubble"><p>${text.replace(/\n/g, '<br>')}</p></div>
    `;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function updateProgress(progreso) {
    if (!progreso) return;
    const pct = progreso.total > 0 ? Math.round((progreso.respondidas / progreso.total) * 100) : 0;
    progressBar.style.width = Math.min(pct, 100) + '%';
}

function updateCapa(capaActual) {
    const capas = ['proposito','clientes','servicios','procesos','personas','informacion','tecnologia','inteligencia','gobierno','evolucion'];
    const idx = capas.indexOf(capaActual);
    const nombres = ['Propósito','Clientes','Servicios','Procesos','Personas','Información','Tecnología','Inteligencia','Gobierno','Evolución'];
    if (idx >= 0) {
        capaIndicator.textContent = `${nombres[idx]} (${idx + 1}/10)`;
    }
}

function showTyping() {
    typingIndicator.style.display = 'flex';
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function hideTyping() {
    typingIndicator.style.display = 'none';
}

function setProcessing(state) {
    isProcessing = state;
    chatInput.disabled = state;
    btnEnviar.disabled = state;
}

async function enviarMensaje() {
    const mensaje = chatInput.value.trim();
    if (!mensaje || isProcessing) return;
    
    addMessage(mensaje, false);
    chatInput.value = '';
    setProcessing(true);
    showTyping();
    
    try {
        const resp = await fetch(`/studio/api/${CONSULTORIA_ID}/mensaje`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ mensaje }),
        });
        const data = await resp.json();
        hideTyping();
        
        if (data.ok) {
            addMessage(data.mensaje, true);
            updateProgress(data.progreso);
            updateCapa(data.capa_actual);
            
            if (data.accion === 'completar') {
                btnFinalizar.style.display = 'inline-flex';
                addMessage('✅ La entrevista está completa. Haz clic en "Generar Gemelo Digital" para continuar.', true);
            }
        } else {
            addMessage('❌ Error: ' + (data.error || 'Error de conexión'), true);
        }
    } catch (e) {
        hideTyping();
        addMessage('❌ Error de conexión. Verifica tu internet e intenta de nuevo.', true);
    }
    
    setProcessing(false);
}

async function finalizarEntrevista() {
    btnFinalizar.disabled = true;
    btnFinalizar.textContent = 'Generando...';
    addMessage('🔄 Generando el Gemelo Digital de tu empresa...', true);
    
    try {
        const resp = await fetch(`/studio/api/${CONSULTORIA_ID}/generar-twin`, { method: 'POST' });
        const data = await resp.json();
        if (data.ok) {
            window.location.href = `/studio/${CONSULTORIA_ID}/gemelo-asis`;
        } else {
            addMessage('❌ Error: ' + (data.error || 'Error generando gemelo'), true);
        }
    } catch (e) {
        addMessage('❌ Error de conexión', true);
    }
    
    btnFinalizar.disabled = false;
    btnFinalizar.textContent = 'Generar Gemelo Digital';
}

chatInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        enviarMensaje();
    }
});

// Focus input on load
chatInput.focus();
```

- [ ] **Step 2: Create gemelo.js**

```javascript
// Stonelytics Studio — Twin Visualization

function toggleCapa(id) {
    const content = document.getElementById('capa-content-' + id);
    const icon = document.getElementById('capa-icon-' + id);
    if (content.style.display === 'none' || !content.style.display) {
        content.style.display = 'block';
        icon.classList.replace('ti-chevron-right', 'ti-chevron-down');
    } else {
        content.style.display = 'none';
        icon.classList.replace('ti-chevron-down', 'ti-chevron-right');
    }
}

function editarCapa(capaId) {
    const modal = document.getElementById('modal-capa');
    const textarea = document.getElementById('capa-editor');
    const currentContent = document.getElementById('capa-json-' + capaId);
    
    document.getElementById('modal-capa-title').textContent = 'Editando: ' + capaId;
    document.getElementById('modal-capa-id').value = capaId;
    
    if (currentContent) {
        const content = JSON.parse(currentContent.value);
        textarea.value = JSON.stringify(content, null, 2);
    }
    
    modal.style.display = 'flex';
}

function cerrarModal() {
    document.getElementById('modal-capa').style.display = 'none';
}

async function guardarCapa() {
    const capaId = document.getElementById('modal-capa-id').value;
    const content = document.getElementById('capa-editor').value;
    
    try {
        JSON.parse(content);
    } catch (e) {
        alert('JSON inválido. Corrige antes de guardar.');
        return;
    }
    
    const resp = await fetch(`/studio/api/${CONSULTORIA_ID}/gemelo-asis`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ capas: { [capaId]: JSON.parse(content) } }),
    });
    const data = await resp.json();
    if (data.ok) {
        cerrarModal();
        location.reload();
    } else {
        alert('Error: ' + data.error);
    }
}

async function calcularBrechas() {
    const btn = document.getElementById('btn-calcular-brechas');
    btn.disabled = true;
    btn.textContent = 'Calculando...';
    
    try {
        const resp = await fetch(`/studio/api/${CONSULTORIA_ID}/calcular-brechas`, { method: 'POST' });
        const data = await resp.json();
        if (data.ok) {
            window.location.href = `/studio/${CONSULTORIA_ID}/brechas`;
        } else {
            alert('Error: ' + data.error);
        }
    } catch (e) {
        alert('Error de conexión');
    }
    
    btn.disabled = false;
    btn.textContent = 'Calcular Brechas';
}

async function generarPlan() {
    const btn = document.getElementById('btn-generar-plan');
    btn.disabled = true;
    btn.textContent = 'Generando...';
    
    try {
        const resp = await fetch(`/studio/api/${CONSULTORIA_ID}/generar-plan`, { method: 'POST' });
        const data = await resp.json();
        if (data.ok) {
            window.location.href = `/studio/${CONSULTORIA_ID}/plan`;
        } else {
            alert('Error: ' + data.error);
        }
    } catch (e) {
        alert('Error de conexión');
    }
    
    btn.disabled = false;
    btn.textContent = 'Generar Plan';
}

async function sugerirTobe(capa) {
    const btn = document.getElementById('sugerir-' + capa);
    if (btn) btn.disabled = true;
    
    const contenidoEl = document.getElementById('capa-json-' + capa);
    const contenido = contenidoEl ? JSON.parse(contenidoEl.value) : {};
    
    try {
        const resp = await fetch(`/studio/api/${CONSULTORIA_ID}/sugerir-tobe`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ capa, contenido }),
        });
        const data = await resp.json();
        if (data.ok && data.objetivos) {
            const container = document.getElementById('objetivos-' + capa);
            if (container) {
                container.innerHTML = data.objetivos.map((o, i) =>
                    `<div class="objetivo-item"><input type="checkbox" checked> <span>${o.descripcion}</span> <span class="badge badge--${o.prioridad === 'alta' ? 'error' : 'warning'}">${o.prioridad}</span></div>`
                ).join('');
            }
        }
    } catch (e) {
        console.error('Error suggesting TO BE:', e);
    }
    
    if (btn) btn.disabled = false;
}

// Close modal on background click
document.addEventListener('click', function(e) {
    const modal = document.getElementById('modal-capa');
    if (modal && e.target === modal) cerrarModal();
});
```

- [ ] **Step 3: Create studio.css**

Write `static/css/studio.css` with all styles for chat, twin cards, gap matrix, plan cards, proposal, modal, animations, responsive. (Full CSS in Task 7 steps above.)

---

### Task 8: Integration — App Factory, Sidebar, Migrations

**Files:**
- Modify: `app.py` (register studio blueprint)
- Modify: `templates/admin/_sidebar.html` (add Studio nav link)
- Modify: `core/models/__init__.py` (verify imports)

- [ ] **Step 1: Register blueprint in app.py**

Edit `app.py` — add import and registration in `_register_blueprints()`:

After `from modules.cotizador.routes import cotizador_bp`, add:
```python
from modules.studio.routes import studio_bp
```

After `app.register_blueprint(cotizador_bp, url_prefix='/cotizador')`, add:
```python
app.register_blueprint(studio_bp, url_prefix='/studio')
```

- [ ] **Step 2: Add Studio link to sidebar**

Edit `templates/admin/_sidebar.html` — add after the Cotizador link:
```html
<a href="/studio/" {{ 'class="active"' if active_page == 'studio' }}><i class="ti ti-message-chatbot"></i> Studio</a>
```

- [ ] **Step 3: Verify models import**

The `core/models/__init__.py` was updated in Task 1. Verify by running:
```bash
cd /c/Users/Usuario/stonelytics/stonelytics && python -c "from core.models import Consultoria, ConsultoriaMensaje, TwinASIS, TwinTOBE, Brecha, PlanRecomendado; print('All imports OK')"
```

- [ ] **Step 4: Create database tables**

```bash
cd /c/Users/Usuario/stonelytics/stonelytics && python -c "
from app import create_app
from core import db
app = create_app()
with app.app_context():
    db.create_all()
    print('Tables created/verified')
"
```

---

### Task 9: Create remaining 6 templates

**Files:**
- Create: `templates/studio/gemelo_asis.html`
- Create: `templates/studio/gemelo_tobe.html`
- Create: `templates/studio/brechas.html`
- Create: `templates/studio/plan.html`
- Create: `templates/studio/cotizacion.html`
- Create: `templates/studio/propuesta.html`

- [ ] **Step 1: gemelo_asis.html**

```html
{% extends "base.html" %}
{% block title %}Gemelo AS IS — {{ consultoria.cliente.company_name }}{% endblock %}
{% block extra_css %}<link rel="stylesheet" href="/static/css/admin.css"><link rel="stylesheet" href="/static/css/studio.css">{% endblock %}
{% block body %}
<div class="admin-layout">
  {% set active_page = 'studio' %}
  {% include "admin/_sidebar.html" %}
  <main class="admin-main">
    <header class="admin-header">
      <h1>Gemelo Digital — Estado Actual (AS IS)</h1>
      <div style="display:flex;gap:8px;">
        <a href="/studio/{{ consultoria.id }}/gemelo-tobe" class="btn btn--primary btn--sm">Ir al Estado Deseado →</a>
      </div>
    </header>
    <div class="admin-content">
      <div class="twin-grid">
        {% set capas_info = [
          ('proposito', 'target-arrow', 'Propósito'),
          ('clientes', 'users', 'Clientes'),
          ('servicios', 'package', 'Servicios'),
          ('procesos', 'route', 'Procesos'),
          ('personas', 'user', 'Personas'),
          ('informacion', 'database', 'Información'),
          ('tecnologia', 'server', 'Tecnología'),
          ('inteligencia', 'chart-bar', 'Inteligencia'),
          ('gobierno', 'shield-check', 'Gobierno'),
          ('evolucion', 'trending-up', 'Evolución'),
        ] %}
        {% for capa_id, icono, titulo in capas_info %}
        {% set contenido = twin.capas.get(capa_id, {}) if twin and twin.capas else {} %}
        <div class="twin-card">
          <div class="twin-card__header" onclick="toggleCapa('{{ capa_id }}')">
            <h3><i class="ti ti-{{ icono }}"></i> {{ titulo }}</h3>
            <div style="display:flex;gap:8px;align-items:center;">
              {% if contenido %}
              <span class="badge badge--success" style="font-size:0.7rem;">Completo</span>
              {% else %}
              <span class="badge badge--outline" style="font-size:0.7rem;">Pendiente</span>
              {% endif %}
              <i class="ti ti-chevron-right" id="capa-icon-{{ capa_id }}"></i>
            </div>
          </div>
          <div class="twin-card__body" id="capa-content-{{ capa_id }}" style="display:none;">
            <input type="hidden" id="capa-json-{{ capa_id }}" value='{{ contenido | tojson | safe }}'>
            {% if contenido %}
              {% for key, value in contenido.items() %}
              <div class="twin-field">
                <strong>{{ key | replace('_', ' ') | title }}</strong>
                {% if value is string %}
                <p>{{ value }}</p>
                {% elif value is sequence and value is not mapping %}
                <ul style="margin:4px 0;padding-left:16px;">
                  {% for item in value %}
                  <li style="font-size:0.9rem;">{{ item }}</li>
                  {% endfor %}
                </ul>
                {% elif value is mapping %}
                <pre>{{ value | tojson(indent=2) }}</pre>
                {% endif %}
              </div>
              {% endfor %}
            {% else %}
            <p style="color:var(--text-muted);">No hay información para esta capa.</p>
            {% endif %}
            <div style="margin-top:12px;">
              <button class="btn btn--sm btn--outline" onclick="editarCapa('{{ capa_id }}')">Editar</button>
            </div>
          </div>
        </div>
        {% endfor %}
      </div>

      {% set problemas = twin.problemas if twin and twin.problemas else [] %}
      {% if problemas %}
      <div class="admin-card" style="margin-top:24px;">
        <div class="admin-card__header"><h3>Problemas Detectados</h3></div>
        <div class="admin-card__body">
          {% for p in problemas %}
          <div class="problema-item problema-item--{{ p.get('impacto', 'medio') }}">
            <strong>{{ p.get('capa', '') }}</strong>: {{ p.get('descripcion', '') }}
            <span class="badge badge--{{ 'error' if p.get('impacto') == 'alto' else 'warning' if p.get('impacto') == 'medio' else 'success' }}" style="margin-left:auto;">
              {{ p.get('impacto', 'medio') }}
            </span>
          </div>
          {% endfor %}
        </div>
      </div>
      {% endif %}

      <div class="twin-actions">
        <button class="btn btn--primary" onclick="calcularBrechas()" id="btn-calcular-brechas">Calcular Brechas</button>
      </div>
    </div>
  </main>
</div>
{% endblock %}
{% block scripts %}
{{ super() }}
<script src="/static/studio/gemelo.js"></script>
<script>const CONSULTORIA_ID = '{{ consultoria.id }}';</script>
{% endblock %}
```

- [ ] **Step 2: gemelo_tobe.html**

```html
{% extends "base.html" %}
{% block title %}Gemelo TO BE — {{ consultoria.cliente.company_name }}{% endblock %}
{% block extra_css %}<link rel="stylesheet" href="/static/css/admin.css"><link rel="stylesheet" href="/static/css/studio.css">{% endblock %}
{% block body %}
<div class="admin-layout">
  {% set active_page = 'studio' %}
  {% include "admin/_sidebar.html" %}
  <main class="admin-main">
    <header class="admin-header">
      <h1>Gemelo Digital — Estado Deseado (TO BE)</h1>
      <div style="display:flex;gap:8px;">
        <a href="/studio/{{ consultoria.id }}/gemelo-asis" class="btn btn--outline btn--sm">← Volver al AS IS</a>
        <button class="btn btn--primary btn--sm" onclick="calcularBrechas()">Calcular Brechas</button>
      </div>
    </header>
    <div class="admin-content">
      <div class="twin-grid">
        {% set capas_info = [
          ('proposito', 'target-arrow', 'Propósito'),
          ('clientes', 'users', 'Clientes'),
          ('servicios', 'package', 'Servicios'),
          ('procesos', 'route', 'Procesos'),
          ('personas', 'user', 'Personas'),
          ('informacion', 'database', 'Información'),
          ('tecnologia', 'server', 'Tecnología'),
          ('inteligencia', 'chart-bar', 'Inteligencia'),
          ('gobierno', 'shield-check', 'Gobierno'),
          ('evolucion', 'trending-up', 'Evolución'),
        ] %}
        {% for capa_id, icono, titulo in capas_info %}
        {% set contenido_asis = twin_asis.capas.get(capa_id, {}) if twin_asis and twin_asis.capas else {} %}
        {% set contenido_tobe = twin_tobe.capas.get(capa_id, {}) if twin_tobe and twin_tobe.capas else {} %}
        <div class="twin-card">
          <div class="twin-card__header" onclick="toggleCapa('{{ capa_id }}')">
            <h3><i class="ti ti-{{ icono }}"></i> {{ titulo }}</h3>
            <i class="ti ti-chevron-right" id="capa-icon-{{ capa_id }}"></i>
          </div>
          <div class="twin-card__body" id="capa-content-{{ capa_id }}" style="display:none;">
            <h4 style="font-size:0.9rem;color:var(--text-muted);margin-bottom:8px;">Estado Actual</h4>
            <input type="hidden" id="capa-json-{{ capa_id }}" value='{{ contenido_asis | tojson | safe }}'>
            {% for key, value in contenido_asis.items() %}
            <div class="twin-field">
              <strong>{{ key | replace('_', ' ') | title }}</strong>
              <p>{{ value if value is string else value | tojson }}</p>
            </div>
            {% endfor %}

            <hr style="margin:16px 0;border-color:var(--border);">

            <h4 style="font-size:0.9rem;color:var(--accent-blue);margin-bottom:8px;">Estado Deseado</h4>
            <textarea class="tobe-editor" id="tobe-{{ capa_id }}" rows="4" style="width:100%;padding:10px;border:1.5px solid var(--border);border-radius:6px;font-family:inherit;font-size:0.9rem;">{{ contenido_tobe.get('objetivo', '') }}</textarea>
            <div style="margin-top:8px;display:flex;gap:8px;">
              <button class="btn btn--sm btn--outline" onclick="sugerirTobe('{{ capa_id }}')" id="sugerir-{{ capa_id }}">Sugerir con IA</button>
            </div>
            <div id="objetivos-{{ capa_id }}" style="margin-top:8px;"></div>
          </div>
        </div>
        {% endfor %}
      </div>

      <div class="twin-actions">
        <button class="btn btn--primary" onclick="guardarTobe()" style="margin-right:8px;">Guardar Estado Deseado</button>
        <button class="btn btn--primary" onclick="calcularBrechas()">Calcular Brechas</button>
      </div>
    </div>
  </main>
</div>
{% endblock %}
{% block scripts %}
{{ super() }}
<script src="/static/studio/gemelo.js"></script>
<script>
const CONSULTORIA_ID = '{{ consultoria.id }}';

async function guardarTobe() {
    const capas = {};
    document.querySelectorAll('.tobe-editor').forEach(el => {
        const capaId = el.id.replace('tobe-', '');
        if (el.value.trim()) {
            capas[capaId] = { objetivo: el.value.trim() };
        }
    });
    
    const resp = await fetch(`/studio/api/${CONSULTORIA_ID}/gemelo-tobe`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ capas }),
    });
    const data = await resp.json();
    if (data.ok) {
        alert('Estado deseado guardado correctamente');
    } else {
        alert('Error: ' + data.error);
    }
}
</script>
{% endblock %}
```

- [ ] **Step 3: brechas.html**

```html
{% extends "base.html" %}
{% block title %}Brechas — {{ consultoria.cliente.company_name }}{% endblock %}
{% block extra_css %}<link rel="stylesheet" href="/static/css/admin.css"><link rel="stylesheet" href="/static/css/studio.css">{% endblock %}
{% block body %}
<div class="admin-layout">
  {% set active_page = 'studio' %}
  {% include "admin/_sidebar.html" %}
  <main class="admin-main">
    <header class="admin-header">
      <h1>Matriz de Brechas</h1>
      <div style="display:flex;gap:8px;">
        <a href="/studio/{{ consultoria.id }}/plan" class="btn btn--primary btn--sm">Generar Plan SRIE →</a>
      </div>
    </header>
    <div class="admin-content">
      {% if brechas %}
      <table class="brechas-table">
        <thead>
          <tr>
            <th>Capa</th>
            <th>Problema Actual</th>
            <th>Estado Deseado</th>
            <th>Impacto</th>
            <th>Prioridad</th>
            <th>Solución</th>
          </tr>
        </thead>
        <tbody>
          {% for b in brechas %}
          <tr>
            <td><strong>{{ b.capa }}</strong></td>
            <td>{{ b.problema_actual }}</td>
            <td>{{ b.estado_deseado }}</td>
            <td>
              <select class="impacto-select" onchange="actualizarBrecha('{{ b.id }}', 'impacto', this.value)">
                <option value="alta" {{ 'selected' if b.impacto == 'alta' }}>Alto</option>
                <option value="media" {{ 'selected' if b.impacto == 'media' }}>Medio</option>
                <option value="baja" {{ 'selected' if b.impacto == 'baja' }}>Bajo</option>
              </select>
            </td>
            <td>
              <select class="prioridad-select" onchange="actualizarBrecha('{{ b.id }}', 'prioridad', this.value)">
                <option value="alta" {{ 'selected' if b.prioridad == 'alta' }}>Alta</option>
                <option value="media" {{ 'selected' if b.prioridad == 'media' }}>Media</option>
                <option value="baja" {{ 'selected' if b.prioridad == 'baja' }}>Baja</option>
              </select>
            </td>
            <td>
              <input type="text" value="{{ b.solucion or '' }}" class="prioridad-select" style="width:100%;" onchange="actualizarBrecha('{{ b.id }}', 'solucion', this.value)" placeholder="Solución...">
            </td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
      <div class="twin-actions">
        <button class="btn btn--primary" onclick="generarPlan()" id="btn-generar-plan">Generar Plan Recomendado</button>
      </div>
      {% else %}
      <div class="admin-card">
        <div class="admin-card__body" style="text-align:center;padding:60px;">
          <i class="ti ti-alert-triangle" style="font-size:2rem;color:var(--text-muted);"></i>
          <p style="color:var(--text-muted);margin-top:16px;">No hay brechas calculadas aún.</p>
          <button class="btn btn--primary" onclick="calcularBrechas()">Calcular Brechas</button>
        </div>
      </div>
      {% endif %}
    </div>
  </main>
</div>
{% endblock %}
{% block scripts %}
{{ super() }}
<script src="/static/studio/gemelo.js"></script>
<script>
const CONSULTORIA_ID = '{{ consultoria.id }}';

async function actualizarBrecha(brechaId, campo, valor) {
    await fetch(`/studio/api/brechas/${brechaId}`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ [campo]: valor }),
    });
}
</script>
{% endblock %}
```

- [ ] **Step 4: plan.html**

```html
{% extends "base.html" %}
{% block title %}Plan — {{ consultoria.cliente.company_name }}{% endblock %}
{% block extra_css %}<link rel="stylesheet" href="/static/css/admin.css"><link rel="stylesheet" href="/static/css/studio.css">{% endblock %}
{% block body %}
<div class="admin-layout">
  {% set active_page = 'studio' %}
  {% include "admin/_sidebar.html" %}
  <main class="admin-main">
    <header class="admin-header">
      <h1>Plan Recomendado</h1>
      <div style="display:flex;gap:8px;">
        <a href="/studio/{{ consultoria.id }}/cotizacion" class="btn btn--primary btn--sm">Generar Cotización →</a>
      </div>
    </header>
    <div class="admin-content">
      {% if plan and plan.items %}
      <div class="plan-grid">
        {% for item in plan.items %}
        <div class="plan-card">
          <h3><i class="ti ti-package"></i> {{ item.modulo }}</h3>
          <p style="font-size:0.9rem;color:#475569;">{{ item.descripcion }}</p>
          <div class="plan-price">${{ '{:,.2f}'.format(item.precio) if item.precio else 'Pendiente' }}</div>
          <div class="plan-justification">{{ item.justificacion }}</div>
        </div>
        {% endfor %}
      </div>
      <div class="plan-total">
        Total estimado: <span>${{ '{:,.2f}'.format(plan.total_estimado) }}</span>
      </div>
      {% else %}
      <div class="admin-card">
        <div class="admin-card__body" style="text-align:center;padding:60px;">
          <i class="ti ti-sparkles" style="font-size:2rem;color:var(--text-muted);"></i>
          <p style="color:var(--text-muted);margin-top:16px;">No hay un plan generado aún. Calcula las brechas primero.</p>
          <a href="/studio/{{ consultoria.id }}/brechas" class="btn btn--primary">Ir a Brechas</a>
        </div>
      </div>
      {% endif %}
      <div class="twin-actions">
        <a href="/studio/{{ consultoria.id }}/cotizacion" class="btn btn--primary">Generar Cotización</a>
      </div>
    </div>
  </main>
</div>
{% endblock %}
```

- [ ] **Step 5: cotizacion.html**

```html
{% extends "base.html" %}
{% block title %}Cotización — {{ consultoria.cliente.company_name }}{% endblock %}
{% block extra_css %}<link rel="stylesheet" href="/static/css/admin.css"><link rel="stylesheet" href="/static/css/studio.css">{% endblock %}
{% block body %}
<div class="admin-layout">
  {% set active_page = 'studio' %}
  {% include "admin/_sidebar.html" %}
  <main class="admin-main">
    <header class="admin-header">
      <h1>Cotización</h1>
    </header>
    <div class="admin-content">
      <form method="POST" class="admin-form" style="max-width:700px;">
        <h3 style="margin-bottom:20px;">Plan Recomendado para {{ consultoria.cliente.company_name }}</h3>
        
        <div class="form-group">
          <label>Título de la propuesta</label>
          <input type="text" name="title" value="Plan Empresarial - {{ consultoria.cliente.company_name }}" required style="width:100%;padding:12px;border:1.5px solid var(--border);border-radius:6px;">
        </div>

        <div class="form-group">
          <label>Items del Plan</label>
          <div id="items-container">
            {% for item in plan.get('items', []) %}
            <div class="item-row" style="display:flex;gap:8px;align-items:center;margin-bottom:8px;padding:12px;background:#f8fafc;border-radius:6px;">
              <input type="hidden" name="item_type" value="custom">
              <input type="hidden" name="item_type" value="capability">
              <div style="flex:1;">
                <strong>{{ item.modulo }}</strong>
                <p style="font-size:0.85rem;color:var(--text-muted);margin:0;">{{ item.descripcion }}</p>
              </div>
              <input type="hidden" name="description" value="{{ item.modulo }}: {{ item.descripcion }}" data-index="{{ loop.index0 }}">
              <input type="number" name="unit_price" value="{{ item.precio }}" data-index="{{ loop.index0 }}" style="width:120px;padding:8px;border:1.5px solid var(--border);border-radius:6px;">
              <input type="number" name="quantity" value="1" min="1" data-index="{{ loop.index0 }}" style="width:60px;padding:8px;border:1.5px solid var(--border);border-radius:6px;">
              <input type="checkbox" checked onchange="this.closest('.item-row').style.opacity=this.checked?'1':'0.5'">
            </div>
            {% else %}
            <p style="color:var(--text-muted);">No hay items en el plan.</p>
            {% endfor %}
          </div>
        </div>

        <div class="form-group">
          <label>Alcance del proyecto</label>
          <textarea name="scope" rows="4" style="width:100%;padding:12px;border:1.5px solid var(--border);border-radius:6px;font-family:inherit;">Implementación del plan empresarial para {{ consultoria.cliente.company_name }} incluyendo los módulos seleccionados.</textarea>
        </div>

        <div class="form-group">
          <label>Descuento (%)</label>
          <input type="number" name="discount_pct" value="0" min="0" max="100" step="5" style="width:120px;padding:12px;border:1.5px solid var(--border);border-radius:6px;">
        </div>

        <input type="hidden" name="items" id="items-json">

        <button type="submit" class="btn btn--primary" style="width:100%;padding:14px;margin-top:16px;">Guardar y Generar Propuesta</button>
      </form>
    </div>
  </main>
</div>
{% endblock %}
{% block scripts %}
{{ super() }}
<script>
document.querySelector('form').addEventListener('submit', function(e) {
    const items = [];
    document.querySelectorAll('.item-row').forEach(row => {
        if (row.querySelector('input[type="checkbox"]').checked) {
            const description = row.querySelector('[name="description"]').value;
            const price = parseFloat(row.querySelector('[name="unit_price"]').value) || 0;
            const qty = parseInt(row.querySelector('[name="quantity"]').value) || 1;
            items.push({
                item_type: 'custom',
                description: description,
                unit_price: price,
                quantity: qty,
            });
        }
    });
    document.getElementById('items-json').value = JSON.stringify(items);
});
</script>
{% endblock %}
```

- [ ] **Step 6: propuesta.html**

```html
{% extends "base.html" %}
{% block title %}Propuesta — {{ consultoria.cliente.company_name }}{% endblock %}
{% block extra_css %}<link rel="stylesheet" href="/static/css/admin.css"><link rel="stylesheet" href="/static/css/studio.css">{% endblock %}
{% block body %}
<div class="admin-layout">
  {% set active_page = 'studio' %}
  {% include "admin/_sidebar.html" %}
  <main class="admin-main">
    <header class="admin-header">
      <h1>Propuesta Comercial</h1>
      <div style="display:flex;gap:8px;">
        {% if quotation %}
        <a href="/studio/{{ consultoria.id }}/pdf" class="btn btn--primary btn--sm"><i class="ti ti-download"></i> Descargar PDF</a>
        {% endif %}
      </div>
    </header>
    <div class="admin-content">
      <div class="proposal">
        <div class="proposal__section">
          <h2>Resumen Ejecutivo</h2>
          <p><strong>Cliente:</strong> {{ consultoria.cliente.company_name }}</p>
          <p><strong>Contacto:</strong> {{ consultoria.cliente.contact_name }}</p>
          <p><strong>Fecha:</strong> {{ consultoria.created_at.strftime('%d/%m/%Y') if consultoria.created_at else '—' }}</p>
          <hr style="margin:16px 0;">
          <p>Diagnóstico empresarial completo con {{ brechas | length }} brechas identificadas y {{ plan.get('items', []) | length }} módulos recomendados.</p>
        </div>

        {% if twin_asis and twin_asis.capas %}
        <div class="proposal__section">
          <h2>Diagnóstico — Estado Actual</h2>
          <table class="admin-table">
            <thead><tr><th>Capa</th><th>Hallazgos Principales</th></tr></thead>
            <tbody>
              {% set capa_nombres = {'proposito':'Propósito','clientes':'Clientes','servicios':'Servicios','procesos':'Procesos','personas':'Personas','informacion':'Información','tecnologia':'Tecnología','inteligencia':'Inteligencia','gobierno':'Gobierno','evolucion':'Evolución'} %}
              {% for capa_id, nombre in capa_nombres.items() %}
              {% set contenido = twin_asis.capas.get(capa_id, {}) %}
              <tr>
                <td><strong>{{ nombre }}</strong></td>
                <td>{{ contenido.get('mision', contenido.get('segmentos', contenido.get('catalogo', contenido.get('criticos', contenido.get('total_empleados', contenido.get('datos_clave', contenido.get('software_actual', contenido.get('toma_decisiones', contenido.get('politicas_seguridad', contenido.get('historia_cambios', '—')))))))))) }}</td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
        {% endif %}

        {% if brechas %}
        <div class="proposal__section">
          <h2>Brechas Priorizadas</h2>
          <table class="admin-table">
            <thead><tr><th>Prioridad</th><th>Brecha</th><th>Solución</th></tr></thead>
            <tbody>
              {% for b in brechas %}
              <tr>
                <td><span class="impacto-{{ b.prioridad }}">{{ b.prioridad | upper }}</span></td>
                <td>{{ b.problema_actual[:100] }}</td>
                <td>{{ b.solucion[:80] if b.solucion else '—' }}</td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
        {% endif %}

        {% if plan and plan.items %}
        <div class="proposal__section">
          <h2>Plan Recomendado</h2>
          <table class="admin-table">
            <thead><tr><th>Módulo</th><th>Descripción</th><th>Inversión</th></tr></thead>
            <tbody>
              {% for item in plan.items %}
              <tr>
                <td><strong>{{ item.modulo }}</strong></td>
                <td>{{ item.descripcion }}</td>
                <td>${{ '{:,.2f}'.format(item.precio) if item.precio else '—' }}</td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
          <div class="plan-total" style="margin-top:16px;">
            Inversión Total Estimada: <span>${{ '{:,.2f}'.format(plan.total_estimado) }}</span>
          </div>
        </div>
        {% endif %}

        {% if quotation %}
        <div class="proposal__section">
          <h2>Cotización</h2>
          <p><strong>Número:</strong> {{ quotation.quotation_number }}</p>
          <p><strong>Valor Final:</strong> ${{ '{:,.2f}'.format(quotation.final_price) }}</p>
          {% if quotation.valid_until %}
          <p><strong>Vigencia:</strong> {{ quotation.valid_until.strftime('%d/%m/%Y') }}</p>
          {% endif %}
          <div style="margin-top:16px;">
            <a href="/studio/{{ consultoria.id }}/pdf" class="btn btn--primary">Descargar PDF Completo</a>
          </div>
        </div>
        {% else %}
        <div class="proposal__section" style="text-align:center;">
          <p style="color:var(--text-muted);">No se ha generado cotización aún.</p>
          <a href="/studio/{{ consultoria.id }}/cotizacion" class="btn btn--primary">Generar Cotización</a>
        </div>
        {% endif %}
      </div>
    </div>
  </main>
</div>
{% endblock %}
```

---

### Task 10: Verify and Test

**Files:**
- No new files

- [ ] **Step 1: Import check**

```bash
cd /c/Users/Usuario/stonelytics/stonelytics && python -c "
from app import create_app
app = create_app()
with app.app_context():
    from core.models import Consultoria, ConsultoriaMensaje, TwinASIS, TwinTOBE, Brecha, PlanRecomendado
    print('Models OK')
    from modules.studio import studio_bp
    print('Blueprint OK')
    from modules.studio.services import EntrevistaIAService, TwinService, BrechaService, PlanService
    print('Services OK')
    from modules.studio.ai_prompts import CAPAS, get_system_prompt
    print('AI Prompts OK')
    from modules.studio.srie_mapper import map_brechas_to_soluciones, get_all_soluciones
    print('SRIE Mapper OK')
print('All imports verified')
"
```

- [ ] **Step 2: List routes**

```bash
cd /c/Users/Usuario/stonelytics/stonelytics && python -c "
from app import create_app
app = create_app()
for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
    if '/studio' in str(rule.rule):
        print(f'{rule.rule:50s} -> {rule.endpoint}')
"
```

Expected output should show all `/studio/` routes listed.

- [ ] **Step 3: Start the application and verify**

```bash
cd /c/Users/Usuario/stonelytics/stonelytics && python run.py
```

Then visit:
- `http://localhost:10000/admin/login` → login with admin credentials
- `http://localhost:10000/studio/` → should show dashboard with "Nueva Consultoría" button
- `http://localhost:10000/studio/nueva` → should show client selector
- `http://localhost:10000/studio/<id>/entrevista` → should show chat interface
