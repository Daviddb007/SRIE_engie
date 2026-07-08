# Stonelytics Studio — MVP 02 Design Specification

**Date:** 2026-07-07
**Author:** David / Stonelytics

## Modules

MVP 02 adds three modules on top of the existing Blueprint:

```
MVP 01 (Blueprint) → MVP 02 (Build)
                       ├── Cotización Inteligente (C)
                       ├── Constructor Técnico (A)
                       └── Portal Cliente (B)
```

---

## C — Cotización Inteligente

**Flujo:** Blueprint → Plan → "Generar Cotización" → Quotation creada automáticamente → Propuesta.

**Cambios:**
- Ruta `/studio/<id>/cotizacion` cambia a acción directa POST
- Se elimina el formulario manual de items
- Plan.items se mapean al catálogo de Capabilities para precios
- QuotationService.create() se llama con los items del plan
- Redirige directamente a propuesta

**Archivos a modificar:**
- `modules/studio/routes.py` — Simplificar cotizacion route
- `templates/studio/plan.html` — Botón "Generar Cotización" directo

---

## A — Constructor Técnico

Genera specs técnicas desde el Blueprint usando IA.

**Componentes:**

| Componente | Input | Output |
|-----------|-------|--------|
| Modelo de Datos | Capa Información + TO BE | Entidades SQLAlchemy, relaciones, tipos |
| API Specs | Capas Procesos + Servicios | Endpoints REST con métodos y payloads |
| Arquitectura | Todas las capas | Diagrama de sistema, componentes, stack |
| Roadmap Técnico | Brechas + Plan | Sprints, estimaciones, dependencias |

**Nuevos archivos:**
- `modules/studio/constructor_prompts.py` — Prompts IA para generación técnica
- `modules/studio/constructor.py` — Lógica de generación
- `templates/studio/constructor.html` — Vista del constructor
- `templates/studio/constructor_datos.html` — Modelo de datos
- `templates/studio/constructor_api.html` — API specs
- `templates/studio/constructor_roadmap.html` — Roadmap técnico

**Nuevas rutas:**
- `GET /studio/<id>/constructor` — Página principal del constructor
- `POST /api/<id>/generar-arquitectura` — Genera specs vía IA
- `GET /studio/<id>/constructor/modelo-datos` — Ver modelo de datos
- `GET /studio/<id>/constructor/api` — Ver API specs
- `GET /studio/<id>/constructor/roadmap` — Ver plan de sprints

---

## B — Portal Cliente

Portal read-only para que el cliente vea su Blueprint y progreso.

**Auth:** Magic link por email (sin contraseñas). Patrón existente en Carolina Escalante.

**Flujo:**
1. Cliente ingresa email en `/portal/login`
2. Sistema busca Consultoría por email del cliente
3. Envía magic link al email
4. Cliente hace clic → accede a su portal
5. Ve su Blueprint (read-only): madurez, AS IS, TO BE, brechas, plan
6. Ve estado del proyecto: Borrador / En entrevista / Blueprint listo / En construcción

**Nuevos archivos:**
- `modules/portal/__init__.py` — Blueprint
- `modules/portal/routes.py` — Rutas de auth y dashboard
- `modules/portal/services.py` — Magic link + consulta de blueprint
- `templates/portal/login.html` — Formulario de email
- `templates/portal/dashboard.html` — Blueprint del cliente (read-only)
- `templates/portal/progreso.html` — Estado del proyecto

**Modelos nuevos:**
- `core/models/magic_link.py` — Tokens de acceso temporales (expiran en 24h)

---

## Stack

- Backend: Flask 3.1 + Jinja2 (sin cambios)
- Base de datos: SQLite / PostgreSQL (sin cambios)
- IA: OpenAI GPT-4o-mini (sin cambios)
- Frontend: Bootstrap 5 + Alpine.js (sin cambios)
- Auth portal: Magic link con tokens firmados (itsdangerous)
