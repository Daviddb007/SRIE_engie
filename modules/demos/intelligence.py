"""Intelligence demo routes — diagnostic + PDF report."""
from __future__ import annotations

from datetime import datetime

from flask import Blueprint, render_template, request, jsonify, send_file

demo_intelligence_bp = Blueprint('demo_intelligence', __name__, template_folder='templates')

DIAGNOSTIC_QUESTIONS = [
    {
        "id": 1,
        "question": "¿Cuántos empleados tiene tu empresa?",
        "options": [
            {"label": "1-5", "value": "small"},
            {"label": "6-20", "value": "medium"},
            {"label": "21-50", "value": "large"},
            {"label": "Más de 50", "value": "enterprise"},
        ],
    },
    {
        "id": 2,
        "question": "¿Cuánto inviertes mensualmente en marketing digital?",
        "options": [
            {"label": "Nada", "value": "none"},
            {"label": "Menos de $500", "value": "low"},
            {"label": "$500 - $2,000", "value": "medium"},
            {"label": "Más de $2,000", "value": "high"},
        ],
    },
    {
        "id": 3,
        "question": "¿Qué herramientas digitales usas actualmente?",
        "options": [
            {"label": "Ninguna", "value": "none"},
            {"label": "Solo redes sociales", "value": "social"},
            {"label": "Sitio web básico", "value": "website"},
            {"label": "CRM + automatización", "value": "advanced"},
        ],
    },
    {
        "id": 4,
        "question": "¿Cuántos leads recibes al mes?",
        "options": [
            {"label": "Menos de 10", "value": "few"},
            {"label": "10-50", "value": "some"},
            {"label": "50-200", "value": "many"},
            {"label": "Más de 200", "value": "lots"},
        ],
    },
]

RECOMMENDATIONS = {
    'small': {
        'readiness': 'Emergente',
        'score': 25,
        'summary': 'Tu empresa está en una etapa temprana de madurez digital. Hay una oportunidad significativa de crecimiento con inversiones estratégicas.',
        'actions': [
            'Implementar una presencia digital profesional',
            'Establecer canales de captación de leads',
            'Automatizar respuestas iniciales',
        ],
        'system': 'Start',
    },
    'medium': {
        'readiness': 'En desarrollo',
        'score': 50,
        'summary': 'Tu empresa tiene bases digitales pero hay gaps importantes que están dejando dinero sobre la mesa.',
        'actions': [
            'Optimizar el embudo de conversión',
            'Implementar automatización de seguimiento',
            'Agregar analytics para tomar decisiones',
        ],
        'system': 'Growth',
    },
    'large': {
        'readiness': 'Avanzada',
        'score': 75,
        'summary': 'Tu empresa tiene una buena base digital. Con las herramientas correctas puede escalar significativamente.',
        'actions': [
            'Integrar IA para calificar leads',
            'Implementar dashboards con KPIs en tiempo real',
            'Automatizar procesos comerciales repetitivos',
        ],
        'system': 'Intelligence',
    },
    'enterprise': {
        'readiness': 'Líder',
        'score': 90,
        'summary': 'Tu empresa está posicionada como líder digital en su sector. El siguiente nivel es inteligencia operativa.',
        'actions': [
            'Implementar IA predictiva para ventas',
            'Automatizar flujos de trabajo complejos',
            'Crear experiencias personalizadas a escala',
        ],
        'system': 'Intelligence',
    },
}


def _get_recommendation(answers: list[dict]) -> dict:
    """Extract company size from answers and return recommendation."""
    company_size = next((a['value'] for a in answers if a['step'] == 1), 'small')
    return RECOMMENDATIONS.get(company_size, RECOMMENDATIONS['small'])


@demo_intelligence_bp.route('/demo/intelligence')
def demo_intelligence():
    return render_template('demos/intelligence.html', questions=DIAGNOSTIC_QUESTIONS)


@demo_intelligence_bp.route('/demo/intelligence/diagnose', methods=['POST'])
def demo_intelligence_diagnose():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'ok': False, 'error': 'No data received'}), 400

        answers = data.get('answers', [])
        if not answers:
            return jsonify({'ok': False, 'error': 'Se necesitan respuestas'}), 400

        recommendation = _get_recommendation(answers)
        return jsonify({'ok': True, 'diagnosis': recommendation})
    except Exception:
        return jsonify({'ok': False, 'error': 'Error del servidor'}), 500


@demo_intelligence_bp.route('/demo/intelligence/report.pdf', methods=['POST'])
def demo_intelligence_report_pdf():
    try:
        from core.services.pdf_service import generate_intelligence_report_pdf

        data = request.get_json()
        if not data:
            return jsonify({'ok': False, 'error': 'No data'}), 400

        answers = data.get('answers', [])
        company_name = data.get('company_name', 'Tu Empresa')
        contact_name = data.get('contact_name', '')

        recommendation = _get_recommendation(answers)
        pdf_buffer = generate_intelligence_report_pdf(
            company_name=company_name,
            contact_name=contact_name,
            diagnosis=recommendation,
        )

        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='informe-diagnostico-stonelytics.pdf',
        )
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500
