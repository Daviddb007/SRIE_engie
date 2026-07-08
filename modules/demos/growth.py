"""Growth demo routes — quiz + lead capture."""
from __future__ import annotations

from flask import Blueprint, render_template, request, jsonify, current_app

from core.services.notification_service import send_telegram_async

demo_growth_bp = Blueprint('demo_growth', __name__, template_folder='templates')

QUIZ_STEPS = [
    {
        "id": 1,
        "question": "¿Qué tipo de negocio tienes?",
        "options": [
            {"label": "Restaurante / Café", "value": "restaurante", "points": 0},
            {"label": "Clínica / Salud", "value": "clinica", "points": 0},
            {"label": "Tienda / E-commerce", "value": "tienda", "points": 0},
            {"label": "Servicios profesionales", "value": "servicios", "points": 0},
            {"label": "Otro", "value": "otro", "points": 0},
        ],
    },
    {
        "id": 2,
        "question": "¿Cuál es tu objetivo principal?",
        "options": [
            {"label": "Tener presencia online profesional", "value": "presencia", "points": 3},
            {"label": "Captar más clientes", "value": "captar", "points": 7},
            {"label": "Automatizar procesos", "value": "automatizar", "points": 10},
        ],
    },
    {
        "id": 3,
        "question": "¿Necesitas sistema de agenda / citas?",
        "options": [
            {"label": "No", "value": "no", "points": 0},
            {"label": "Sí, básico", "value": "basico", "points": 4},
        ],
    },
    {
        "id": 4,
        "question": "¿Qué tipo de formulario de contacto necesitas?",
        "options": [
            {"label": "Básico (nombre, email, mensaje)", "value": "basico", "points": 1},
            {"label": "Con lógica (campos condicionales)", "value": "logica", "points": 3},
            {"label": "Con CRM integrado", "value": "crm", "points": 6},
        ],
    },
    {
        "id": 5,
        "question": "¿Necesitas panel administrativo?",
        "options": [
            {"label": "No", "value": "no", "points": 0},
            {"label": "Básico (ver leads, editar contenido)", "value": "basico", "points": 5},
            {"label": "Avanzado (roles, reportes, dashboard)", "value": "avanzado", "points": 8},
        ],
    },
    {
        "id": 6,
        "question": "¿Cuántas integraciones necesitas?",
        "options": [
            {"label": "Ninguna", "value": "ninguna", "points": 0},
            {"label": "1-3 (WhatsApp, Maps, Analytics)", "value": "pocas", "points": 5},
            {"label": "Más de 5 (APIs, pagos, CRM...)", "value": "muchas", "points": 10},
        ],
    },
    {
        "id": 7,
        "question": "¿Necesitas IA o automatización?",
        "options": [
            {"label": "No", "value": "no", "points": 0},
            {"label": "Chatbot básico", "value": "chatbot", "points": 6},
            {"label": "IA completa (personalizada, flujos)", "value": "ia_completa", "points": 10},
        ],
    },
]


def classify_plan(total_points: int) -> dict:
    """Classify quiz score into a system tier."""
    if total_points <= 15:
        return {"name": "Start", "description": "Presencia profesional digital."}
    elif total_points <= 35:
        return {"name": "Growth", "description": "Captación y gestión comercial."}
    else:
        return {"name": "Intelligence", "description": "Plataforma inteligente a medida."}


def _score_answers(answers: list[dict]) -> tuple[int, list[str]]:
    """Score quiz answers and return (total_points, answer_summary)."""
    total_points = 0
    answer_summary = []
    for answer in answers:
        step_id = answer.get('step')
        option_value = answer.get('value')
        for step in QUIZ_STEPS:
            if step['id'] == step_id:
                for opt in step['options']:
                    if opt['value'] == option_value:
                        total_points += opt['points']
                        answer_summary.append(f"{step['question']}: {opt['label']}")
    return total_points, answer_summary


def _save_lead_and_notify(
    app, name: str, email: str, phone: str,
    total_points: int, plan: dict, answer_summary: list[str],
) -> None:
    """Save lead to DB and send Telegram notification (background)."""
    def _worker():
        with app.app_context():
            _save_lead_to_db(app, name, email, phone, total_points, plan, answer_summary)
            _send_telegram_lead(app, name, email, phone, total_points, plan, answer_summary)

    import threading
    threading.Thread(target=_worker, daemon=True).start()


def _save_lead_to_db(app, name, email, phone, total_points, plan, answer_summary):
    try:
        from core import db
        from core.models import Client
        client = Client(
            company_name=f'Lead: {name}',
            contact_name=name,
            contact_email=email,
            contact_phone=phone,
            industry='Growth Demo',
            notes=f'Quiz Score: {total_points}pts → Plan {plan["name"]}\n' + '\n'.join(answer_summary),
        )
        db.session.add(client)
        db.session.commit()
        app.logger.info(f'Growth demo lead saved: {name} ({email})')
    except Exception as e:
        app.logger.error(f'Growth demo DB save failed: {e}')


def _send_telegram_lead(app, name, email, phone, total_points, plan, answer_summary):
    try:
        msg = (
            f"🎯 *Lead Growth Demo*\n\n"
            f"👤 {name}\n"
            f"📧 {email}\n"
            f"📱 {phone}\n\n"
            f"📊 Score: {total_points}pts → *Plan {plan['name']}*\n\n"
            f"Respuestas:\n" + '\n'.join(f"• {a}" for a in answer_summary)
        )
        send_telegram_async(msg, app)
    except Exception as e:
        app.logger.error(f'Growth demo Telegram failed: {e}')


@demo_growth_bp.route('/demo/growth')
def demo_growth():
    return render_template('demos/growth.html', steps=QUIZ_STEPS)


@demo_growth_bp.route('/demo/growth/submit', methods=['POST'])
def demo_growth_submit():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'ok': False, 'error': 'No data received'}), 400

        answers = data.get('answers', [])
        contact = data.get('contact', {})
        name = contact.get('name', '').strip()
        email = contact.get('email', '').strip()
        phone = contact.get('phone', '').strip()

        if not name or not email:
            return jsonify({'ok': False, 'error': 'Nombre y email son obligatorios'}), 400

        total_points, answer_summary = _score_answers(answers)
        plan = classify_plan(total_points)

        _save_lead_and_notify(
            current_app._get_current_object(), name, email, phone,
            total_points, plan, answer_summary,
        )

        return jsonify({'ok': True, 'plan': plan, 'points': total_points, 'answers': answer_summary})
    except Exception:
        return jsonify({'ok': False, 'error': 'Error del servidor'}), 500
