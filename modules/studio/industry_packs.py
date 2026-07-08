"""Industry Packs for SRIE Engine — pre-configured knowledge for vertical industries."""

INDUSTRY_PACKS = {
    "transporte": {
        "id": "transporte",
        "nombre": "Transporte y Logistica",
        "icono": "truck",
        "descripcion": "Empresas de transporte de carga, pasajeros, logistica y distribucion",
        "preguntas_clave": [
            "Flota propia o de terceros? Cuantos vehiculos?",
            "Que tipo de carga transportan? (seco, refrigerado, peligroso, etc.)",
            "Tienen sistema de tracking/GPS en tiempo real?",
            "Como gestionan rutas y despachos?",
            "Manejan clientes fijos o viajes spot?",
            "Como facturan y cobran? Tienen integracion con plataformas de pago?",
            "Cumplen con normativa de transporte (RETEN, RUNT, etc.)?",
        ],
        "kpi_industria": [
            "Utilizacion de flota (%)",
            "Tiempo promedio de entrega",
            "Costo por kilometro",
            "Incidentes de seguridad por mes",
            "Rotacion de conductores",
        ],
        "madurez_tipica": {
            "proposito": 60, "clientes": 45, "servicios": 55,
            "procesos": 35, "personas": 40, "informacion": 30,
            "tecnologia": 25, "inteligencia": 20, "gobierno": 35, "evolucion": 40,
        },
        "soluciones_prioritarias": [
            {"modulo": "StoneCRM", "justificacion": "Clientes frecuentes con contratos y tarifas especiales"},
            {"modulo": "StoneFlow", "justificacion": "Automatizacion de despacho, rutas y documentacion"},
            {"modulo": "StoneData", "justificacion": "Dashboard de flota, rutas, costos y rentabilidad"},
            {"modulo": "StoneRAG", "justificacion": "Manuales de operacion, normativa y procedimientos"},
        ],
    },
    "psicologia": {
        "id": "psicologia",
        "nombre": "Psicologia y Salud Mental",
        "icono": "heart",
        "descripcion": "Consultorios psicologicos, clinicas de salud mental, centros de bienestar",
        "preguntas_clave": [
            "Manejan historia clinica digital o en papel?",
            "Como gestionan agenda de citas? Tienen sistema de recordatorios?",
            "Manejan consentimientos informados y documentacion legal?",
            "Facturan a pacientes particulares, EPS o ambos?",
            "Tienen portal para que pacientes agenden virtualmente?",
            "Como manejan la confidencialidad de datos (Habeas Data)?",
            "Generan informes, certificados o historias clinicas automaticamente?",
        ],
        "kpi_industria": [
            "Tasa de no-show en citas (%)",
            "Pacientes nuevos por mes",
            "Tiempo promedio entre agendamiento y cita",
            "Satisfaccion del paciente (NPS)",
            "Ingreso por profesional",
        ],
        "madurez_tipica": {
            "proposito": 65, "clientes": 50, "servicios": 55,
            "procesos": 30, "personas": 35, "informacion": 20,
            "tecnologia": 20, "inteligencia": 15, "gobierno": 40, "evolucion": 30,
        },
        "soluciones_prioritarias": [
            {"modulo": "StoneCRM", "justificacion": "Gestion de pacientes, historia clinica y seguimiento"},
            {"modulo": "StoneFlow", "justificacion": "Agendamiento automatico, recordatorios y facturacion"},
            {"modulo": "StoneDocs", "justificacion": "Generacion de historias clinicas, consentimientos y certificados"},
            {"modulo": "StoneAI", "justificacion": "Chatbot para agendamiento y preguntas frecuentes"},
        ],
    },
    "construccion": {
        "id": "construccion",
        "nombre": "Construccion e Ingenieria",
        "icono": "building",
        "descripcion": "Constructoras, ingenieria civil, desarrollos inmobiliarios, contratistas",
        "preguntas_clave": [
            "Manejan presupuestos de obra y control de costos?",
            "Como gestionan compras a proveedores y materiales?",
            "Tienen control de avance de obra en tiempo real?",
            "Manejan cronogramas y programacion de proyectos?",
            "Como gestionan la documentacion tecnica (planos, especificaciones)?",
            "Facturan por avance de obra o por hitos?",
            "Cumplen con normativa de seguridad industrial y ARL?",
        ],
        "kpi_industria": [
            "Cumplimiento de cronograma (%)",
            "Desviacion de presupuesto (%)",
            "Indice de accidentabilidad",
            "Rotacion de personal en obra",
            "Margen por proyecto",
        ],
        "madurez_tipica": {
            "proposito": 60, "clientes": 40, "servicios": 50,
            "procesos": 30, "personas": 35, "informacion": 25,
            "tecnologia": 20, "inteligencia": 15, "gobierno": 30, "evolucion": 35,
        },
        "soluciones_prioritarias": [
            {"modulo": "StoneCRM", "justificacion": "Gestion de clientes, prospectos y proyectos de construccion"},
            {"modulo": "StoneFlow", "justificacion": "Flujo de compras, aprobaciones y control de obra"},
            {"modulo": "StoneFinance", "justificacion": "Presupuestos, costos de obra y facturacion por avance"},
            {"modulo": "StoneData", "justificacion": "Dashboard de proyectos, rentabilidad y avance"},
            {"modulo": "StoneDocs", "justificacion": "Documentacion tecnica, contratos y actas de obra"},
        ],
    },
    "sector_publico": {
        "id": "sector_publico",
        "nombre": "Sector Publico y Gobierno",
        "icono": "shield-check",
        "descripcion": "Alcaldias, entidades publicas, organismos de gobierno, instituciones estatales",
        "preguntas_clave": [
            "Cumplen con MIPG (Modelo Integrado de Planeacion y Gestion)?",
            "Manejan PQRSD de forma digital o papel?",
            "Como gestionan contratacion publica y proveedores (SECOP)?",
            "Tienen control de indicadores de gestion y planes de desarrollo?",
            "Manejan presupuesto por areas y ejecucion presupuestal?",
            "Tienen un sistema de gestion documental implementado?",
            "Como gestionan riesgos institucionales y de corrupcion?",
            "Tienen portal de transparencia y datos abiertos?",
        ],
        "kpi_industria": [
            "Tiempo de respuesta a PQRSD (dias)",
            "Ejecucion presupuestal (%)",
            "Indice de desempeno institucional",
            "Cobertura de servicios a la ciudadania",
            "Indice de transparencia",
        ],
        "madurez_tipica": {
            "proposito": 70, "clientes": 45, "servicios": 50,
            "procesos": 35, "personas": 40, "informacion": 30,
            "tecnologia": 30, "inteligencia": 25, "gobierno": 50, "evolucion": 35,
        },
        "soluciones_prioritarias": [
            {"modulo": "StoneCRM", "justificacion": "Gestion de ciudadania, PQRSD y comunicaciones"},
            {"modulo": "StoneFlow", "justificacion": "Automatizacion de procesos, contratacion y aprobaciones"},
            {"modulo": "StoneData", "justificacion": "Dashboard de indicadores, planes de desarrollo y transparencia"},
            {"modulo": "StoneRAG", "justificacion": "Gestion documental, normativa y memoria institucional"},
            {"modulo": "StoneLegal", "justificacion": "Contratacion publica, convenios y actos administrativos"},
        ],
    },
}


def get_industry_pack(industry_id: str) -> dict | None:
    return INDUSTRY_PACKS.get(industry_id)


def list_industries() -> list[dict]:
    return [
        {"id": k, "nombre": v["nombre"], "icono": v["icono"], "descripcion": v["descripcion"]}
        for k, v in INDUSTRY_PACKS.items()
    ]


def get_industry_prompt_extension(industry_id: str) -> str:
    """Get industry-specific prompt additions for the interview."""
    pack = INDUSTRY_PACKS.get(industry_id)
    if not pack:
        return ""
    preguntas = "\n".join(f"- {p}" for p in pack["preguntas_clave"])
    kpis = ", ".join(pack["kpi_industria"])
    return (
        f"\n\nINDUSTRIA DETECTADA: {pack['nombre']}\n"
        f"Preguntas clave para esta industria:\n{preguntas}\n"
        f"KPIs tipicos de esta industria: {kpis}\n"
        f"Adapta tus preguntas al contexto de esta industria."
    )
