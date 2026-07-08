"""Analytics routes — cross-client metrics, industry benchmarking, trends."""
from __future__ import annotations

from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from sqlalchemy import func

from core import db
from core.models.consultoria import Consultoria, ConsultoriaMensaje
from core.models.quotation import Quotation
from core.models.brecha import Brecha
from core.models.twin_asis import TwinASIS

analytics_bp = Blueprint('analytics', __name__, template_folder='templates')


@analytics_bp.route('/')
@login_required
def index():
    return render_template('analytics/index.html', active_page='analytics')


@analytics_bp.route('/api/datos')
@login_required
def datos():
    consultorias = Consultoria.query.all()
    total = len(consultorias)
    
    by_industry = {}
    for c in consultorias:
        ind = c.industria or 'general'
        by_industry[ind] = by_industry.get(ind, 0) + 1
    
    by_status = {}
    for c in consultorias:
        by_status[c.estado] = by_status.get(c.estado, 0) + 1
    
    twins = TwinASIS.query.all()
    maturity_scores = {}
    for t in twins:
        madurez = t.capas.get('madurez', {}) if t.capas else {}
        general = madurez.get('general', 0)
        if general:
            consultoria = Consultoria.query.get(t.consultoria_id)
            ind = consultoria.industria if consultoria else 'general'
            if ind not in maturity_scores:
                maturity_scores[ind] = []
            maturity_scores[ind].append(float(general))
    
    avg_maturity = {}
    for ind, scores in maturity_scores.items():
        avg_maturity[ind] = round(sum(scores) / len(scores), 1) if scores else 0
    
    brechas = Brecha.query.all()
    breach_by_layer = {}
    for b in brechas:
        breach_by_layer[b.capa] = breach_by_layer.get(b.capa, 0) + 1
    
    breach_by_impact = {}
    for b in brechas:
        breach_by_impact[b.impacto] = breach_by_impact.get(b.impacto, 0) + 1
    
    quotations = Quotation.query.all()
    total_q = len(quotations)
    sent = sum(1 for q in quotations if q.status == 'sent')
    accepted = sum(1 for q in quotations if q.status == 'accepted')
    
    return jsonify({
        'total_consultorias': total,
        'por_industria': by_industry,
        'por_estado': by_status,
        'madurez_promedio': avg_maturity,
        'brechas_por_capa': breach_by_layer,
        'brechas_por_impacto': breach_by_impact,
        'cotizaciones': {
            'total': total_q,
            'enviadas': sent,
            'aceptadas': accepted,
            'tasa_conversion': round(accepted / total_q * 100, 1) if total_q > 0 else 0,
        },
    })


@analytics_bp.route('/api/consultorias-tiempo')
@login_required
def consultorias_tiempo():
    from sqlalchemy import extract
    consultorias = Consultoria.query.all()
    months = {}
    for c in consultorias:
        if c.created_at:
            key = c.created_at.strftime('%Y-%m')
            months[key] = months.get(key, 0) + 1
    return jsonify({'meses': [{'fecha': k, 'total': v} for k, v in sorted(months.items())]})
