"""Cotizador routes — thin handlers delegating to services."""
from __future__ import annotations

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required

from core.models import Client, Capability, Automation, Service
from core.services.quotation_service import QuotationService

cotizador_bp = Blueprint('cotizador', __name__, template_folder='templates')


@cotizador_bp.route('/')
@login_required
def cotizador_index():
    clients = Client.query.order_by(Client.company_name).all()
    capabilities = Capability.query.filter_by(is_active_=True).all()
    automations = Automation.query.filter_by(is_active_=True).all()
    services = Service.query.filter_by(is_active_=True).all()
    return render_template('cotizador/index.html', clients=clients,
                           capabilities=capabilities, automations=automations,
                           services=services)


@cotizador_bp.route('/api/calculate', methods=['POST'])
@login_required
def cotizador_calculate():
    try:
        data = request.get_json()
        items = data.get('items', [])
        discount_pct = float(data.get('discount_pct', 0))
        result = QuotationService.calculate(items, discount_pct)
        return jsonify({'ok': True, **result})
    except Exception:
        return jsonify({'ok': False, 'error': 'Error calculando'}), 500


@cotizador_bp.route('/api/save', methods=['POST'])
@login_required
def cotizador_save():
    try:
        from flask_login import current_user
        data = request.get_json()
        quotation = QuotationService.create(
            client_id=data.get('client_id'),
            title=data.get('title', 'Cotización'),
            items=data.get('items', []),
            scope=data.get('scope', ''),
            discount_pct=float(data.get('discount_pct', 0)),
            created_by=current_user.id,
        )
        return jsonify({
            'ok': True,
            'quotation_id': quotation.id,
            'number': quotation.quotation_number,
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500
