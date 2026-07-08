# Stonelytics Studio — MVP 01 Design Specification

- **Date:** 2026-07-07
- **Author:** David / Stonelytics
- **Status:** Draft — pending user review

---

## 1. Mission

> Transformar una reunión comercial en un "Blueprint Empresarial" completo y una propuesta comercial lista para enviar.

El MVP 01 no genera código, ni backend, ni frontend, ni infraestructura. Produce un **diagnóstico empresarial estructurado** y una **propuesta comercial** (PDF) que Stonelytics vende como servicio de Ingeniería Empresarial.

---

## 2. Stack

| Capa | Tecnología | Estado |
|------|-----------|--------|
| Backend | Flask 3.1 + Jinja2 | Existente en Stonelytics |
| Base de datos | PostgreSQL | Existente |
| IA | OpenAI / Gemini (vía adaptador StoneDocs) | Existente en backend/ |
| PDF | WeasyPrint | Existente |
| Frontend | Bootstrap 5 + Alpine.js + vanilla JS | Existente en Stonelytics |
| Autenticación | Flask-Login | Existente |

**No se usa React, StoneDocs frontend, ni SRIE Workflow Engine en este MVP.**

---

## 3. Objetos del Sistema (Core Domain)

```
Cliente ──1:N──> Consultoría ──1:1──> Twin AS IS
                            ──1:1──> Twin TO BE
                            ──1:N──> Brecha
                            ──1:1──> Plan Recomendado
                            ──1:1──> Cotización
                            ──1:N──> Documento (Propuesta PDF)
```

### 3.1 Nuevos modelos (a crear)

| Modelo | Atributos clave |
|--------|----------------|
| `Consultoria` | id (UUID), cliente_id (FK), estado (borrador/activa/completada/cerrada), fecha_inicio, notas, created_at, updated_at |
| `ConsultoriaMensaje` | id, consultoria_id (FK), rol (ia/usuario), contenido (Text), capa (string opcional), timestamp |
| `TwinASIS` | id, consultoria_id (FK, unique), capas (JSONB — 10 capas), problemas (JSONB), created_at, updated_at |
| `TwinTOBE` | id, consultoria_id (FK, unique), capas (JSONB — 10 capas), objetivos (JSONB), created_at, updated_at |
| `Brecha` | id, consultoria_id (FK), capa (string), problema_actual (Text), estado_deseado (Text), impacto (alta/media/baja), prioridad (alta/media/baja), solucion (Text), sort_order (int) |
| `PlanRecomendado` | id, consultoria_id (FK), items (JSONB [{modulo, descripcion, valor_estimado, tiempo_estimado, brecha_id}]), total_estimado, duracion_estimada, created_at |

### 3.2 Modelos existentes (reutilizar)

| Modelo | Uso |
|--------|-----|
| `Client` | Datos del cliente/organización |
| `Quotation` | Cotización final con items, totales, estado |
| `QuotationItem` | Items individuales de la cotización (capacidades, automatizaciones, servicios) |
| `Capability` | Catálogo de soluciones Stonelytics (StoneDocs, StoneCRM, etc.) |
| `Automation` | Catálogo de automatizaciones |
| `Service` | Servicios adicionales (capacitación, soporte, etc.) |

---

## 4. Flujo de Pantallas (User Journey)

### Pantalla 1: Dashboard de Consultorías
- Ruta: `/studio/`
- Lista de consultorías activas con estado, cliente, fecha
- Botón "Nueva Consultoría"
- Estadísticas: consultorías este mes, tasa de conversión, ingresos estimados
- Reutiliza layout `base_admin.html`

### Pantalla 2: Selección / Creación de Cliente
- Ruta: `/studio/nueva`
- Buscador de clientes existentes (autocomplete)
- Botón "Crear nuevo cliente" si no existe
- Formulario mínimo: nombre, empresa, email, teléfono
- Al seleccionar/crear → crea `Consultoria` con estado=borrador → redirige a entrevista

### Pantalla 3: Entrevista IA
- Ruta: `/studio/<consultoria_id>/entrevista`
- Interfaz tipo chat con Alpine.js
  - Burbujas de mensajes (IA izquierda, usuario derecha)
  - Input de texto con Enter para enviar
  - Indicador "escribiendo..." mientras la IA procesa
  - Barra de progreso: "Capa 3 de 10: Clientes"
- La IA guía la conversación cubriendo las 10 capas universales:
  1. Propósito  2. Clientes  3. Servicios  4. Procesos  5. Personas
  6. Información  7. Tecnología  8. Inteligencia  9. Gobierno  10. Evolución
- Cada capa tiene un checklist de preguntas predefinidas
- La IA profundiza cuando detecta respuestas superficiales
- Al completar → genera `TwinASIS` (JSON de 10 capas) → redirige a gemelo

### Pantalla 4: Gemelo Digital AS IS
- Ruta: `/studio/<consultoria_id>/gemelo-asis`
- 10 tarjetas expandibles (una por capa)
- Cada tarjeta: título, indicador de completitud, problemas resaltados
- Expandible: contenido completo estructurado
- Botón "Editar" → modal con campos editables

### Pantalla 5: Gemelo Digital TO BE
- Ruta: `/studio/<consultoria_id>/gemelo-tobe`
- Mismo layout que AS IS
- Cada capa: contenido actual + campo "Objetivo a futuro"
- Mini-chat por capa para definir objetivo
- Botón "Calcular brechas" → genera objetos `Brecha`

### Pantalla 6: Matriz de Brechas
- Ruta: `/studio/<consultoria_id>/brechas`
- Tabla: Capa | Estado Actual | Estado Deseado | Brecha | Impacto | Prioridad | Solución
- Cada fila editable
- IA sugiere prioridades automáticamente
- Botón "Generar Plan"

### Pantalla 7: Plan Recomendado
- Ruta: `/studio/<consultoria_id>/plan`
- SRIE mapea brechas a soluciones del catálogo
- Lista de módulos recomendados con precio
- Total estimado
- Botones "Personalizar" y "Generar Cotización"

### Pantalla 8: Cotización
- Ruta: `/studio/<consultoria_id>/cotizacion`
- Reutiliza el cotizador existente (`/cotizador/`)
- Items precargados del Plan
- Descuento, vigencia, condiciones
- Guardar → redirige a propuesta

### Pantalla 9: Propuesta (PDF)
- Ruta: `/studio/<consultoria_id>/propuesta`
- PDF con: portada, resumen diagnóstico, gemelo vs deseado, brechas, plan, cotización, términos
- Botones: "Descargar PDF", "Enviar por correo", "Marcar como enviado"
- Estados: Borrador / Enviado / Aprobado / Rechazado / Cerrado

---

## 5. Diseño de la Entrevista IA

### 5.1 Estrategia de prompting

La IA recibe un system prompt con:
- Rol: "consultor empresarial experto"
- Checklist de preguntas para la capa actual
- Instrucciones para detectar superficialidad y profundizar
- Formato de respuesta estructurado (acción + mensaje + hallazgos)

### 5.2 Flujo de conversación

1. IA saluda y pregunta sobre el propósito/negocio
2. Avanza capa por capa preguntando el checklist
3. Al final de cada capa: resumen de lo entendido
4. "¿Hay algo más que agregar sobre [capa]?"
5. Al finalizar 10 capas: resumen completo → usuario confirma → guarda TwinASIS

### 5.3 Deep-dive automático

Si usuario responde "No sé", "Funciona bien", "Está bien" → IA pide concretar con ejemplos, tiempos, o escenarios de fallo.

---

## 6. Mapeo SRIE (Brecha → Solución)

Reglas del motor para MVP 01:

| Brecha | Solución sugerida |
|--------|------------------|
| Sin CRM / gestión clientes | StoneCRM |
| Procesos manuales / sin automatización | StoneFlow |
| Sin dashboard / reporting | StoneData |
| Documentación manual | StoneDocs |
| Sin presencia digital | StoneLanding |
| Sin atención IA / chatbot | StoneAI |
| Sin base documental | StoneRAG |
| Sin contratos digitales | StoneLegal |
| Gestión financiera manual | StoneFinance |
| Sin portal empleados | StonePeople |

Reglas: coincidencia de keywords en la descripción de la brecha.

---

## 7. Estructura de Directorios (dentro de Stonelytics)

```
modules/studio/
  __init__.py        # Blueprint: studio_bp
  routes.py          # Todas las rutas del flujo
  services.py        # EntrevistaIA, Twin, Brecha, Plan services
  ai_prompts.py      # Prompts por capa

core/models/
  consultoria.py     # Consultoria + ConsultoriaMensaje
  twin_asis.py       # TwinASIS
  twin_tobe.py       # TwinTOBE
  brecha.py          # Brecha
  plan_recomendado.py

templates/studio/
  dashboard.html
  seleccionar_cliente.html
  entrevista.html
  gemelo_asis.html
  gemelo_tobe.html
  brechas.html
  plan.html
  propuesta.html

static/studio/
  entrevista.js
  gemelo.js
```

---

## 8. Lo que NO se construye (MVP 01)

- ❌ Generación de backend / APIs
- ❌ Generación de frontend / React
- ❌ Docker / Kubernetes / infraestructura
- ❌ DevOps / CI/CD
- ❌ Código de aplicación (Flask, modelos, etc.)
- ❌ SRIE Workflow Engine
- ❌ StoneDocs frontend (React)
- ❌ Marketplace
- ❌ Industry Packs

---

## 9. Criterios de éxito

1. Usuario crea cliente y realiza entrevista completa (10 capas)
2. IA genera Twin AS IS estructurado desde la conversación
3. Usuario define estado deseado (TO BE)
4. Sistema calcula brechas automáticamente
5. SRIE sugiere plan con módulos y precios
6. Se genera cotización con items precargados
7. Se descarga PDF profesional con diagnóstico + propuesta
8. Todo el flujo toma < 1 hora
