# Stonelytics Studio — MVP 02 Implementation Plan

**Goal:** Add three modules on top of the existing Blueprint: Cotizacion Inteligente (C), Constructor Tecnico (A), Portal Cliente (B)

**Architecture:** Flask 3.1 + Jinja2. Module C modifies existing routes. Module A adds new AI prompts + templates. Module B adds a new blueprint with magic-link auth.

**Tech Stack:** Flask 3.1, SQLAlchemy, OpenAI GPT-4o-mini, Jinja2, Bootstrap 5.

---

### Task Group C: Cotizacion Inteligente

### Task C1: Simplify cotizacion route to one-click

**Files:**
- Modify: `modules/studio/routes.py` (cotizacion route: 182-208)

- [ ] **Step 1: Replace cotizacion route**

Edit the `cotizacion()` function in routes.py to be POST-only, auto-creating the quotation from plan items:

```python
@studio_bp.route('/<consultoria_id>/cotizacion', methods=['POST'])
@login_required
def cotizacion(consultoria_id: str):
    consultoria = Consultoria.query.get_or_404(consultoria_id)
    plan_data = plan_service.get_plan(consultoria_id)
    
    try:
        items = []
        for item in plan_data.get('items', []):
            items.append({
                'item_type': 'capability',
                'description': f"{item.get('modulo', 'Modulo')}: {item.get('descripcion', item.get('justificacion', ''))}",
                'unit_price': float(item.get('precio', 0)),
                'quantity': 1,
            })
        
        quotation = QuotationService.create(
            client_id=consultoria.cliente_id,
            title=f'Plan Empresarial - {consultoria.cliente.company_name}',
            items=items,
            scope='Implementacion del plan basado en el Blueprint Empresarial generado por SRIE Engine.',
            created_by=str(consultoria.id),
        )
        flash(f'Cotizacion {quotation.quotation_number} creada', 'success')
        return redirect(url_for('studio.propuesta', consultoria_id=consultoria_id))
    except Exception as e:
        flash(f'Error generando cotizacion: {str(e)}', 'error')
        return redirect(url_for('studio.plan', consultoria_id=consultoria_id))
```

- [ ] **Step 2: Update plan.html button to POST**

In `templates/studio/plan.html`, change the "Generar Cotizacion" button to a form that POSTs:

```html
<form method="POST" action="/studio/{{ consultoria.id }}/cotizacion" style="display:inline;">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    <button type="submit" class="btn btn--primary">Generar Cotizacion</button>
</form>
```

---

### Task Group A: Constructor Tecnico

### Task A1: Create constructor AI prompts

**Files:**
- Create: `modules/studio/constructor_prompts.py`

- [ ] **Step 1: Create constructor_prompts.py**

```python
"""AI prompts for generating technical specifications from the Blueprint."""

PROMPT_GENERAR_MODELO_DATOS = """Eres un arquitecto de datos senior. Basado en el siguiente diagnostico empresarial, genera el modelo de datos relacional que necesita la empresa para operar.

Estado Actual (AS IS):
{gemelo_asis}

Estado Deseado (TO BE):
{gemelo_tobe}

Brechas identificadas:
{brechas}

Genera un modelo de datos completo con:

1. LISTA DE ENTIDADES: Cada entidad con sus atributos, tipos de dato, y descripcion
2. RELACIONES: Entre entidades con tipo (1:N, N:M, 1:1)
3. TABLAS SQL: Sentencias CREATE TABLE completas con claves primarias y foraneas
4. CAMPOS CLAVE: Identifica cuales son los campos mas importantes para el negocio

Responde en JSON:
{{
    "entidades": [
        {{ "nombre": "Cliente", "descripcion": "Almacena informacion de clientes", "atributos": [{{ "nombre": "id", "tipo": "UUID", "pk": true, "descripcion": "Identificador unico" }}, {{ "nombre": "nombre", "tipo": "VARCHAR(255)", "descripcion": "Nombre del cliente" }}], "relaciones": [{{ "entidad_destino": "Proyecto", "tipo": "1:N", "descripcion": "Un cliente puede tener muchos proyectos" }}] }}
    ],
    "sql_ddl": "CREATE TABLE clientes (id UUID PRIMARY KEY, nombre VARCHAR(255) NOT NULL, ...);",
    "campos_clave": ["clientes.email", "proyectos.estado"]
}}
"""

PROMPT_GENERAR_API = """Eres un arquitecto de APIs senior. Basado en el siguiente diagnostico empresarial, genera las especificaciones de API REST que necesita el sistema.

Estado Deseado (TO BE):
{gemelo_tobe}

Procesos identificados:
{procesos}

Servicios a implementar:
{servicios}

Genera:
1. LISTA DE ENDPOINTS: Cada endpoint con metodo, ruta, descripcion, request/response
2. AUTENTICACION: Que endpoints requieren auth
3. INTEGRACIONES: Con que sistemas externos debe integrarse

Responde en JSON:
{{
    "endpoints": [
        {{ "metodo": "GET", "ruta": "/api/clientes", "descripcion": "Listar clientes", "auth": true, "response": {{ "type": "array", "items": {{ "$ref": "Cliente" }} }} }}
    ],
    "modelos_api": [{{ "nombre": "Cliente", "campos": [{{ "nombre": "id", "tipo": "string" }}] }}],
    "integraciones": [{{ "sistema": "Wompi", "tipo": "pagos", "descripcion": "Procesar pagos en linea" }}]
}}
"""

PROMPT_GENERAR_ARQUITECTURA = """Eres un arquitecto de software senior. Basado en el diagnostico empresarial, genera la arquitectura tecnologica recomendada.

Estado Deseado (TO BE):
{gemelo_tobe}

Modulos del plan:
{plan}

Genera:
1. DIAGRAMA DE ARQUITECTURA: Componentes, capas, flujo de datos
2. STACK TECNOLOGICO: Lenguajes, frameworks, bases de datos, servicios cloud
3. INTEGRACIONES: Sistemas externos, APIs de terceros
4. REQUISITOS NO FUNCIONALES: Seguridad, escalabilidad, performance
5. PATRONES: Arquitectura usada (microservicios, monolito, event-driven, etc.)

Responde en JSON:
{{
    "nombre": "Arquitectura Propuesta",
    "descripcion": "Descripcion general de la arquitectura",
    "stack": [{{ "capa": "frontend", "tecnologia": "React", "justificacion": "..." }}],
    "componentes": [{{ "nombre": "API Gateway", "descripcion": "Punto de entrada unico", "tecnologia": "Flask" }}],
    "patron": "monolito modular",
    "integraciones": [{{ "sistema": "OpenAI", "proposito": "IA conversacional" }}],
    "nfr": [{{ "nombre": "Tiempo de respuesta", "valor": "< 200ms", "prioridad": "alta" }}]
}}
"""

PROMPT_GENERAR_ROADMAP = """Eres un project manager senior. Basado en el diagnostico empresarial, genera un plan de implementacion por sprints.

Brechas priorizadas:
{brechas}

Modulos del plan:
{plan}

Arquitectura propuesta:
{arquitectura}

Genera:
1. SPRINTS: Cada sprint con duracion, objetivos, modulos a construir
2. DEPENDENCIAS: Que sprints dependen de otros
3. HITOS: Fechas clave y entregables
4. EQUIPO: Roles necesarios y dedicacion
5. RIESGOS: Posibles obstaculos y mitigaciones

Responde en JSON:
{{
    "sprints": [
        {{ "numero": 1, "nombre": "Fundacion", "duracion": "2 semanas", "objetivos": ["Setup del proyecto", "Modelo de datos"], "modulos": ["StoneCRM"], "dependencias": [] }}
    ],
    "hitos": [{{ "semana": 2, "evento": "MVP funcional", "entregable": "CRUD de clientes" }}],
    "equipo": [{{ "rol": "Backend Developer", "dedicacion": "Full-time", "semanas": 8 }}],
    "riesgos": [{{ "riesgo": "Cambio de alcance", "probabilidad": "media", "mitigacion": "Sprints cortos" }}]
}}
"""
```

### Task A2: Create constructor service

**Files:**
- Create: `modules/studio/constructor.py`

- [ ] **Step 1: Create constructor.py**

```python
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
```

### Task A3: Add constructor routes

**Files:**
- Modify: `modules/studio/routes.py` (add new routes)

- [ ] **Step 1: Add import and service init**

Add at top of routes.py:
```python
from modules.studio.constructor import ConstructorService
```

Add after other service inits:
```python
constructor_service = ConstructorService()
```

- [ ] **Step 2: Add constructor routes**

Add after the plan route:
```python
@studio_bp.route('/<consultoria_id>/constructor')
@login_required
def constructor(consultoria_id: str):
    consultoria = Consultoria.query.get_or_404(consultoria_id)
    twin_asis = twin_service.get_asis(consultoria_id)
    twin_tobe = twin_service.get_tobe(consultoria_id)
    brechas_list = brecha_service.get_brechas(consultoria_id)
    plan_data = plan_service.get_plan(consultoria_id)
    return render_template('studio/constructor.html', consultoria=consultoria,
                          twin_asis=twin_asis, twin_tobe=twin_tobe,
                          brechas=brechas_list, plan=plan_data, active_page='studio')


@studio_bp.route('/api/<consultoria_id>/generar-arquitectura', methods=['POST'])
@login_required
def generar_arquitectura(consultoria_id: str):
    try:
        twin_asis = twin_service.get_asis(consultoria_id)
        twin_tobe = twin_service.get_tobe(consultoria_id)
        brechas_list = brecha_service.get_brechas(consultoria_id)
        plan_data = plan_service.get_plan(consultoria_id)
        
        datos = constructor_service.generar_modelo_datos(twin_asis, twin_tobe, brechas_list)
        api = constructor_service.generar_api(twin_tobe, str(twin_asis.capas.get('procesos', {})), str(twin_asis.capas.get('servicios', {})))
        arquitectura = constructor_service.generar_arquitectura(twin_tobe, plan_data)
        roadmap = constructor_service.generar_roadmap(brechas_list, plan_data, arquitectura)
        
        return jsonify({'ok': True, 'datos': datos, 'api': api, 'arquitectura': arquitectura, 'roadmap': roadmap})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500
```

### Task A4: Create constructor template

**Files:**
- Create: `templates/studio/constructor.html`

- [ ] **Step 1: Create constructor.html**

```html
{% extends "base.html" %}
{% block title %}Constructor — {{ consultoria.cliente.company_name }}{% endblock %}
{% block extra_css %}<link rel="stylesheet" href="/static/css/admin.css"><link rel="stylesheet" href="/static/css/studio.css">{% endblock %}
{% block body %}
<div class="admin-layout">
  {% set active_page = 'studio' %}
  {% include "admin/_sidebar.html" %}
  <main class="admin-main">
    <header class="admin-header">
      <h1>Constructor Tecnico</h1>
      <button class="btn btn--primary btn--sm" onclick="generarArquitectura()" id="btn-generar">
        <i class="ti ti-code"></i> Generar Especificaciones
      </button>
    </header>
    <div class="admin-content">
      <div id="loading" style="display:none;text-align:center;padding:60px;">
        <p style="color:var(--text-muted);font-size:1.1rem;">Generando especificaciones tecnicas desde el Blueprint...</p>
        <div class="studio-chat__typing" style="display:flex;justify-content:center;margin-top:16px;">
          <span class="dot"></span><span class="dot"></span><span class="dot"></span>
        </div>
      </div>
      <div id="results">
        <div class="admin-card" style="margin-bottom:20px;">
          <div class="admin-card__body" style="text-align:center;padding:60px;">
            <i class="ti ti-code" style="font-size:2rem;color:var(--text-muted);"></i>
            <p style="color:var(--text-muted);margin-top:16px;">Haz clic en "Generar Especificaciones" para que SRIE analice el Blueprint y genere el modelo de datos, API specs, arquitectura y roadmap tecnico.</p>
          </div>
        </div>
      </div>
    </div>
  </main>
</div>
{% endblock %}
{% block scripts %}
{{ super() }}
<script>
const CID = '{{ consultoria.id }}';

async function generarArquitectura() {
    document.getElementById('btn-generar').disabled = true;
    document.getElementById('btn-generar').innerHTML = 'Generando...';
    document.getElementById('loading').style.display = 'block';
    document.getElementById('results').innerHTML = '';
    
    try {
        const resp = await fetch(`/studio/api/${CID}/generar-arquitectura`, { method: 'POST' });
        const data = await resp.json();
        document.getElementById('loading').style.display = 'none';
        
        if (data.ok) {
            let html = '';
            
            if (data.datos && data.datos.entidades) {
                html += '<div class="admin-card" style="margin-bottom:20px;"><div class="admin-card__header"><h3>Modelo de Datos</h3><span class="badge badge--success">' + data.datos.entidades.length + ' entidades</span></div><div class="admin-card__body">';
                html += '<pre style="font-size:0.8rem;max-height:400px;overflow-y:auto;">' + escapeHtml(JSON.stringify(data.datos, null, 2)) + '</pre>';
                html += '</div></div>';
            }
            
            if (data.api && data.api.endpoints) {
                html += '<div class="admin-card" style="margin-bottom:20px;"><div class="admin-card__header"><h3>API Specifications</h3><span class="badge badge--success">' + data.api.endpoints.length + ' endpoints</span></div><div class="admin-card__body">';
                html += '<pre style="font-size:0.8rem;max-height:400px;overflow-y:auto;">' + escapeHtml(JSON.stringify(data.api, null, 2)) + '</pre>';
                html += '</div></div>';
            }
            
            if (data.arquitectura) {
                html += '<div class="admin-card" style="margin-bottom:20px;"><div class="admin-card__header"><h3>Arquitectura</h3></div><div class="admin-card__body">';
                html += '<pre style="font-size:0.8rem;max-height:400px;overflow-y:auto;">' + escapeHtml(JSON.stringify(data.arquitectura, null, 2)) + '</pre>';
                html += '</div></div>';
            }
            
            if (data.roadmap && data.roadmap.sprints) {
                html += '<div class="admin-card" style="margin-bottom:20px;"><div class="admin-card__header"><h3>Roadmap Tecnico</h3><span class="badge badge--success">' + data.roadmap.sprints.length + ' sprints</span></div><div class="admin-card__body">';
                html += '<pre style="font-size:0.8rem;max-height:400px;overflow-y:auto;">' + escapeHtml(JSON.stringify(data.roadmap, null, 2)) + '</pre>';
                html += '</div></div>';
            }
            
            document.getElementById('results').innerHTML = html;
        } else {
            document.getElementById('results').innerHTML = '<div class="admin-card"><div class="admin-card__body" style="text-align:center;padding:40px;color:var(--red);">Error: ' + (data.error || 'Error generando') + '</div></div>';
        }
    } catch (e) {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('results').innerHTML = '<div class="admin-card"><div class="admin-card__body" style="text-align:center;padding:40px;color:var(--red);">Error de conexion</div></div>';
    }
    
    document.getElementById('btn-generar').disabled = false;
    document.getElementById('btn-generar').innerHTML = '<i class="ti ti-code"></i> Generar Especificaciones';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
</script>
{% endblock %}
```

---

### Task Group B: Portal Cliente

### Task B1: Create MagicLink model

**Files:**
- Create: `core/models/magic_link.py`
- Modify: `core/models/__init__.py`

- [ ] **Step 1: Create magic_link.py**

```python
from datetime import datetime, timezone, timedelta
import secrets
from core import db
from core.models.base import BaseModel


class MagicLink(BaseModel):
    __tablename__ = 'magic_links'

    email = db.Column(db.String(255), nullable=False, index=True)
    consultoria_id = db.Column(db.String(36), db.ForeignKey('consultorias.id'), nullable=True)
    token = db.Column(db.String(128), nullable=False, unique=True, index=True)
    usado = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)

    consultoria = db.relationship('Consultoria', backref='magic_links')

    @staticmethod
    def create(consultoria_id: str, email: str) -> 'MagicLink':
        token = secrets.token_urlsafe(48)
        link = MagicLink(
            email=email,
            consultoria_id=consultoria_id,
            token=token,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
        )
        db.session.add(link)
        db.session.commit()
        return link

    def is_valid(self) -> bool:
        return not self.usado and self.expires_at > datetime.now(timezone.utc)
```

- [ ] **Step 2: Update models/__init__.py**

Add import:
```python
from core.models.magic_link import MagicLink
```
Add to __all__.

### Task B2: Create portal blueprint

**Files:**
- Create: `modules/portal/__init__.py`
- Create: `modules/portal/routes.py`
- Modify: `app.py` (register blueprint)

- [ ] **Step 1: Create __init__.py**

```python
from modules.portal.routes import portal_bp
```

- [ ] **Step 2: Create routes.py**

```python
"""Portal Cliente — magic link auth + blueprint read-only view."""
from __future__ import annotations

from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from core import db
from core.models.consultoria import Consultoria
from core.models.magic_link import MagicLink
from modules.studio.services import TwinService, BrechaService, PlanService

portal_bp = Blueprint('portal', __name__, template_folder='templates')
twin_service = TwinService()
brecha_service = BrechaService()
plan_service = PlanService()


@portal_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        consultoria = Consultoria.query.join(Consultoria.cliente).filter(
            Consultoria.cliente.has(contact_email=email)
        ).order_by(Consultoria.created_at.desc()).first()
        
        if consultoria:
            link = MagicLink.create(consultoria.id, email)
            login_url = url_for('portal.magic_login', token=link.token, _external=True)
            flash(f'Link de acceso: {login_url}', 'success')
        else:
            flash('No encontramos una consultoria asociada a ese email.', 'error')
        
        return redirect(url_for('portal.login'))
    
    return render_template('portal/login.html')


@portal_bp.route('/magic/<token>')
def magic_login(token: str):
    link = MagicLink.query.filter_by(token=token).first()
    if not link or not link.is_valid():
        flash('Link invalido o expirado. Solicita uno nuevo.', 'error')
        return redirect(url_for('portal.login'))
    
    link.usado = True
    db.session.commit()
    session['portal_consultoria_id'] = link.consultoria_id
    session['portal_email'] = link.email
    return redirect(url_for('portal.dashboard'))


@portal_bp.route('/dashboard')
def dashboard():
    consultoria_id = session.get('portal_consultoria_id')
    if not consultoria_id:
        return redirect(url_for('portal.login'))
    
    consultoria = Consultoria.query.get(consultoria_id)
    if not consultoria:
        flash('Consultoria no encontrada', 'error')
        return redirect(url_for('portal.login'))
    
    twin_asis = twin_service.get_asis(consultoria_id)
    twin_tobe = twin_service.get_tobe(consultoria_id)
    brechas_list = brecha_service.get_brechas(consultoria_id)
    plan_data = plan_service.get_plan(consultoria_id)
    
    return render_template('portal/dashboard.html', consultoria=consultoria,
                          twin_asis=twin_asis, twin_tobe=twin_tobe,
                          brechas=brechas_list, plan=plan_data)


@portal_bp.route('/progreso')
def progreso():
    consultoria_id = session.get('portal_consultoria_id')
    if not consultoria_id:
        return redirect(url_for('portal.login'))
    
    consultoria = Consultoria.query.get(consultoria_id)
    if not consultoria:
        return redirect(url_for('portal.login'))
    
    return render_template('portal/progreso.html', consultoria=consultoria)


@portal_bp.route('/logout')
def logout():
    session.pop('portal_consultoria_id', None)
    session.pop('portal_email', None)
    return redirect(url_for('portal.login'))
```

- [ ] **Step 3: Register blueprint in app.py**

Add import:
```python
from modules.portal.routes import portal_bp
```

Add registration:
```python
app.register_blueprint(portal_bp, url_prefix='/portal')
```

### Task B3: Create portal templates

**Files:**
- Create: `templates/portal/login.html`
- Create: `templates/portal/dashboard.html`
- Create: `templates/portal/progreso.html`

- [ ] **Step 1: Create login.html**

```html
{% extends "base.html" %}
{% block title %}Portal Cliente — Stonelytics{% endblock %}
{% block extra_css %}<link rel="stylesheet" href="/static/css/admin.css">{% endblock %}
{% block body %}
<div class="admin-login">
  <div class="admin-login__bg">
    <div class="admin-login__shape admin-login__shape--1"></div>
    <div class="admin-login__shape admin-login__shape--2"></div>
    <div class="admin-login__shape admin-login__shape--3"></div>
  </div>
  <div class="admin-login__card">
    <div class="admin-login__hero">
      <img src="/static/img/Stonelytics_logo.jpeg" alt="Stonelytics" class="admin-login__logo">
      <h2>Portal Cliente</h2>
      <p>Ingresa tu email para acceder al diagnostico de tu empresa</p>
    </div>
    {% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
    {% for cat, msg in messages %}
    <div class="admin-login__alert admin-login__alert--{{ 'error' if cat == 'error' else 'success' }}">{{ msg }}</div>
    {% endfor %}
    {% endif %}
    {% endwith %}
    <form method="POST">
      <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
      <div class="form-group">
        <label>Tu correo electronico</label>
        <input type="email" name="email" placeholder="correo@empresa.com" required>
      </div>
      <button type="submit" class="btn btn--primary" style="width:100%;padding:14px;">Enviar Link de Acceso</button>
    </form>
    <div class="admin-login__footer">
      <a href="/">Volver a Stonelytics</a>
    </div>
  </div>
</div>
{% endblock %}
```

- [ ] **Step 2: Create dashboard.html**

```html
{% extends "base.html" %}
{% block title %}Mi Diagnostico — {{ consultoria.cliente.company_name }}{% endblock %}
{% block extra_css %}<link rel="stylesheet" href="/static/css/admin.css"><link rel="stylesheet" href="/static/css/studio.css">{% endblock %}
{% block body %}
<div class="admin-layout">
  <aside class="admin-sidebar">
    <div class="admin-sidebar__brand">
      <img src="/static/img/Stonelytics_logo.jpeg" alt="Stonelytics" style="width:32px;height:32px;object-fit:contain;border-radius:8px;">
      <span>Mi Empresa</span>
    </div>
    <nav class="admin-sidebar__nav">
      <a href="/portal/dashboard" class="active"><i class="ti ti-dashboard"></i> Diagnostico</a>
      <a href="/portal/progreso"><i class="ti ti-trending-up"></i> Progreso</a>
    </nav>
    <div class="admin-sidebar__footer">
      <a href="/portal/logout"><i class="ti ti-logout"></i> Cerrar sesion</a>
    </div>
  </aside>
  <main class="admin-main">
    <header class="admin-header">
      <h1>Diagnostico Empresarial — {{ consultoria.cliente.company_name }}</h1>
    </header>
    <div class="admin-content">
      <div class="admin-card" style="margin-bottom:20px;">
        <div class="admin-card__header">
          <h3>Estado de tu Proyecto</h3>
        </div>
        <div class="admin-card__body">
          <p><strong>Estado:</strong> <span class="badge badge--{{ 'success' if consultoria.estado == 'completada' else 'warning' }}">{{ consultoria.estado }}</span></p>
          <p><strong>Contacto:</strong> {{ consultoria.cliente.contact_name }} — {{ consultoria.cliente.contact_email }}</p>
          <p><strong>Inicio:</strong> {{ consultoria.created_at.strftime('%d/%m/%Y') if consultoria.created_at else '—' }}</p>
        </div>
      </div>

      {% set madurez = twin_asis.capas.get('madurez', {}) if twin_asis and twin_asis.capas else {} %}
      {% if madurez %}
      <div class="admin-card" style="margin-bottom:20px;">
        <div class="admin-card__header"><h3>Madurez Digital</h3><span style="font-size:1.5rem;font-weight:700;color:var(--accent-blue);">{{ madurez.get('general', 0) }}%</span></div>
        <div class="admin-card__body">
          {% set caps = {'proposito':'Proposito','clientes':'Clientes','servicios':'Servicios','procesos':'Procesos','personas':'Personas','informacion':'Informacion','tecnologia':'Tecnologia','inteligencia':'Inteligencia','gobierno':'Gobierno','evolucion':'Evolucion'} %}
          {% for cid, cl in caps.items() %}
          {% set sc = madurez.get('por_capa', {}).get(cid, 0) %}
          <div style="display:flex;align-items:center;gap:12px;margin-bottom:4px;">
            <span style="width:90px;font-size:0.8rem;color:var(--text-muted);">{{ cl }}</span>
            <div style="flex:1;height:8px;background:#e2e8f0;border-radius:4px;overflow:hidden;">
              <div style="width:{{ sc }}%;height:100%;background:{% if sc < 30 %}#dc2626{% elif sc < 60 %}#d97706{% else %}#16a34a{% endif %};border-radius:4px;"></div>
            </div>
            <span style="width:30px;font-size:0.75rem;text-align:right;">{{ sc }}%</span>
          </div>
          {% endfor %}
        </div>
      </div>
      {% endif %}

      {% if brechas %}
      <div class="admin-card">
        <div class="admin-card__header"><h3>Oportunidades de Mejora</h3></div>
        <div class="admin-card__body">
          <table class="admin-table">
            <thead><tr><th>Area</th><th>Oportunidad</th><th>Impacto</th></tr></thead>
            <tbody>
              {% for b in brechas %}
              <tr><td><strong>{{ b.capa }}</strong></td><td>{{ b.problema_actual[:80] }}</td><td><span class="impacto-{{ b.impacto }}">{{ b.impacto | upper }}</span></td></tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      </div>
      {% endif %}
    </div>
  </main>
</div>
{% endblock %}
```

- [ ] **Step 3: Create progreso.html**

```html
{% extends "base.html" %}
{% block title %}Progreso — {{ consultoria.cliente.company_name }}{% endblock %}
{% block extra_css %}<link rel="stylesheet" href="/static/css/admin.css">{% endblock %}
{% block body %}
<div class="admin-layout">
  <aside class="admin-sidebar">
    <div class="admin-sidebar__brand">
      <img src="/static/img/Stonelytics_logo.jpeg" style="width:32px;height:32px;object-fit:contain;border-radius:8px;">
      <span>Mi Empresa</span>
    </div>
    <nav class="admin-sidebar__nav">
      <a href="/portal/dashboard"><i class="ti ti-dashboard"></i> Diagnostico</a>
      <a href="/portal/progreso" class="active"><i class="ti ti-trending-up"></i> Progreso</a>
    </nav>
    <div class="admin-sidebar__footer">
      <a href="/portal/logout"><i class="ti ti-logout"></i> Cerrar sesion</a>
    </div>
  </aside>
  <main class="admin-main">
    <header class="admin-header">
      <h1>Progreso del Proyecto</h1>
    </header>
    <div class="admin-content">
      <div style="display:flex;gap:16px;margin-bottom:24px;">
        <div class="admin-stat" style="flex:1;">
          <div class="admin-stat__icon" style="background:rgba(37,99,235,0.1);color:var(--accent-blue);"><i class="ti ti-message-chatbot"></i></div>
          <div><span class="admin-stat__value">{% if consultoria.estado != 'borrador' %}100%{% else %}0%{% endif %}</span><span class="admin-stat__label">Diagnostico</span></div>
        </div>
        <div class="admin-stat" style="flex:1;">
          <div class="admin-stat__icon" style="background:rgba(217,119,6,0.1);color:var(--accent-amber);"><i class="ti ti-code"></i></div>
          <div><span class="admin-stat__value">0%</span><span class="admin-stat__label">Construccion</span></div>
        </div>
        <div class="admin-stat" style="flex:1;">
          <div class="admin-stat__icon" style="background:rgba(16,185,129,0.1);color:var(--accent-green);"><i class="ti ti-rocket"></i></div>
          <div><span class="admin-stat__value">0%</span><span class="admin-stat__label">Implementacion</span></div>
        </div>
      </div>

      <div class="admin-card">
        <div class="admin-card__header"><h3>Linea de Tiempo</h3></div>
        <div class="admin-card__body">
          <div style="padding:20px;text-align:center;color:var(--text-muted);">
            <p>El proyecto se encuentra en la fase de <strong>{{ consultoria.estado }}</strong>.</p>
            <p style="margin-top:8px;">El equipo de Stonelytics esta trabajando en el plan de implementacion.</p>
          </div>
        </div>
      </div>
    </div>
  </main>
</div>
{% endblock %}
```

---

### Task B4: Verify and test

- [ ] **Step 1: Import check**

```bash
cd /c/Users/Usuario/SRIE_Engine && source venv/Scripts/activate 2>/dev/null; DATABASE_URL=sqlite:///test_mvp2.db py -c "
import sys, os; sys.path.insert(0, '.')
os.environ['OPENAI_API_KEY'] = 'sk-...'
from app import create_app
app = create_app()
with app.app_context():
    from core import db; db.create_all()
    from core.models.magic_link import MagicLink
    from modules.portal import portal_bp
    from modules.studio.constructor import ConstructorService
    from modules.studio.constructor_prompts import PROMPT_GENERAR_MODELO_DATOS
    rules = [str(r.rule) for r in app.url_map.iter_rules() if '/portal' in str(r.rule) or '/constructor' in str(r.rule)]
    print(f'New routes: {rules}')
    print('OK')
    import os as _os
    try: _os.remove('test_mvp2.db')
    except: pass
"
```
