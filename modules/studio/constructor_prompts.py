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
