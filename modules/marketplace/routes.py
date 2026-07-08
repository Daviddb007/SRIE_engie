"""Marketplace routes — browse and apply industry packs, plugins, and templates."""
from __future__ import annotations

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required

from core import db
from core.models.consultoria import Consultoria
from modules.studio.industry_packs import INDUSTRY_PACKS, list_industries, get_industry_pack
from modules.studio.srie_mapper import get_all_soluciones

marketplace_bp = Blueprint('marketplace', __name__, template_folder='templates')


@marketplace_bp.route('/')
@login_required
def index():
    industries = list_industries()
    plugins = get_all_soluciones()
    total_items = len(industries) + len(plugins)
    return render_template('marketplace/index.html', industries=industries, plugins=plugins, total_items=total_items, active_page='marketplace')


@marketplace_bp.route('/industria/<industry_id>')
@login_required
def industria_detail(industry_id: str):
    pack = get_industry_pack(industry_id)
    if not pack:
        flash('Industry pack no encontrado', 'error')
        return redirect(url_for('marketplace.index'))
    
    consultorias = Consultoria.query.filter_by(industria=industry_id).order_by(Consultoria.created_at.desc()).all()
    return render_template('marketplace/industria.html', pack=pack, consultorias=consultorias, active_page='marketplace')


@marketplace_bp.route('/api/aplicar-industria', methods=['POST'])
@login_required
def aplicar_industria():
    data = request.get_json()
    consultoria_id = data.get('consultoria_id')
    industry_id = data.get('industry_id')
    
    consultoria = Consultoria.query.get(consultoria_id)
    if not consultoria:
        return jsonify({'ok': False, 'error': 'Consultoria no encontrada'}), 404
    
    pack = get_industry_pack(industry_id)
    if not pack:
        return jsonify({'ok': False, 'error': 'Industry pack no encontrado'}), 404
    
    consultoria.industria = industry_id
    db.session.commit()
    
    return jsonify({
        'ok': True,
        'industria': pack['nombre'],
        'mensaje': f'Industry pack "{pack["nombre"]}" aplicado a la consultoria',
    })
