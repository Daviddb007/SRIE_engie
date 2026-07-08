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
    recomendaciones = []
    slugs_vistos = set()
    
    for brecha in brechas:
        texto = f"{brecha.problema_actual} {brecha.solucion or ''}".lower()
        for rule in MAPPING_RULES:
            for kw in rule["keywords"]:
                if kw in texto:
                    if rule["slug_capacidad"] not in slugs_vistos:
                        slugs_vistos.add(rule["slug_capacidad"])
                        
                        precio = 0
                        if capabilities_query is not None:
                            try:
                                capability = capabilities_query.filter_by(slug=rule["slug_capacidad"]).first()
                                if capability and hasattr(capability, 'price'):
                                    precio = float(capability.price)
                            except Exception:
                                pass
                        
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
