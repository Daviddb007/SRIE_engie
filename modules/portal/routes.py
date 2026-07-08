"""Portal Cliente — magic link auth + blueprint read-only view."""
from __future__ import annotations

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from core import db
from core.models.consultoria import Consultoria
from core.models.magic_link import MagicLink
from modules.studio.services import TwinService, BrechaService, PlanService

portal_bp = Blueprint('portal', __name__, template_folder='templates')
twin_service = TwinService()
brecha_service = BrechaService()
plan_service = PlanService()


@portal_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        consultoria = Consultoria.query.join(Consultoria.cliente).filter(
            Consultoria.cliente.has(contact_email=email)
        ).order_by(Consultoria.created_at.desc()).first()
        
        if consultoria:
            link = MagicLink.create(consultoria.id, email)
            login_url = url_for('portal.magic_login', token=link.token, _external=True)
            flash(f'Link de acceso: {login_url}', 'success')
        else:
            flash('No encontramos una consultoria asociada a ese email.', 'error')
        
        return redirect(url_for('portal.login'))
    
    return render_template('portal/login.html')


@portal_bp.route('/magic/<token>')
def magic_login(token: str):
    link = MagicLink.query.filter_by(token=token).first()
    if not link or not link.is_valid():
        flash('Link invalido o expirado. Solicita uno nuevo.', 'error')
        return redirect(url_for('portal.login'))
    
    link.usado = True
    db.session.commit()
    session['portal_consultoria_id'] = link.consultoria_id
    session['portal_email'] = link.email
    return redirect(url_for('portal.dashboard'))


@portal_bp.route('/dashboard')
def dashboard():
    consultoria_id = session.get('portal_consultoria_id')
    if not consultoria_id:
        return redirect(url_for('portal.login'))
    
    consultoria = Consultoria.query.get(consultoria_id)
    if not consultoria:
        flash('Consultoria no encontrada', 'error')
        return redirect(url_for('portal.login'))
    
    twin_asis = twin_service.get_asis(consultoria_id)
    twin_tobe = twin_service.get_tobe(consultoria_id)
    brechas_list = brecha_service.get_brechas(consultoria_id)
    plan_data = plan_service.get_plan(consultoria_id)
    
    return render_template('portal/dashboard.html', consultoria=consultoria,
                          twin_asis=twin_asis, twin_tobe=twin_tobe,
                          brechas=brechas_list, plan=plan_data)


@portal_bp.route('/progreso')
def progreso():
    consultoria_id = session.get('portal_consultoria_id')
    if not consultoria_id:
        return redirect(url_for('portal.login'))
    
    consultoria = Consultoria.query.get(consultoria_id)
    if not consultoria:
        return redirect(url_for('portal.login'))
    
    return render_template('portal/progreso.html', consultoria=consultoria)


@portal_bp.route('/logout')
def logout():
    session.pop('portal_consultoria_id', None)
    session.pop('portal_email', None)
    return redirect(url_for('portal.login'))
