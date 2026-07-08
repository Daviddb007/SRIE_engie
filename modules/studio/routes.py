"""Stonelytics Studio routes."""
from __future__ import annotations

import json
from datetime import datetime, timezone

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required

from core import db, csrf
from core.models import Client
from core.models.consultoria import Consultoria
from core.models.quotation import Quotation
from core.services.quotation_service import QuotationService

from modules.studio.services import EntrevistaIAService, TwinService, BrechaService, PlanService
from modules.studio.industry_packs import list_industries
from modules.studio.constructor import ConstructorService
from modules.studio.code_generator import generate_models_py, generate_routes_py, generate_dockerfile, generate_requirements, generate_project_zip, generate_full_project, generate_docker_compose, generate_github_actions

studio_bp = Blueprint('studio', __name__, template_folder='templates')
csrf.exempt(studio_bp)

entrevista_service = EntrevistaIAService()
twin_service = TwinService()
brecha_service = BrechaService()
plan_service = PlanService()
constructor_service = ConstructorService()


@studio_bp.route('/')
@login_required
def dashboard():
    consultorias = Consultoria.query.order_by(Consultoria.created_at.desc()).all()
    stats = {
        'total': len(consultorias),
        'activas': sum(1 for c in consultorias if c.estado == 'activa'),
        'completadas': sum(1 for c in consultorias if c.estado == 'completada'),
        'borradores': sum(1 for c in consultorias if c.estado == 'borrador'),
    }
    return render_template('studio/dashboard.html', consultorias=consultorias, stats=stats, active_page='studio')


@studio_bp.route('/nueva', methods=['GET', 'POST'])
@login_required
def nueva_consultoria():
    if request.method == 'POST':
        client_id = request.form.get('client_id')
        industria = request.form.get('industria', 'general')
        if not client_id:
            flash('Selecciona un cliente', 'error')
            return redirect(url_for('studio.nueva_consultoria'))
        
        consultoria = Consultoria(
            cliente_id=client_id,
            industria=industria,
            estado='borrador',
            fecha_inicio=datetime.now(timezone.utc),
        )
        db.session.add(consultoria)
        db.session.commit()
        
        flash('Consultoria creada. Iniciemos la entrevista.', 'success')
        return redirect(url_for('studio.entrevista', consultoria_id=consultoria.id))
    
    clients = Client.query.order_by(Client.company_name).all()
    industries = list_industries()
    return render_template('studio/seleccionar_cliente.html', clients=clients, industries=industries, active_page='studio')


@studio_bp.route('/<consultoria_id>/entrevista')
@login_required
def entrevista(consultoria_id: str):
    consultoria = Consultoria.query.get_or_404(consultoria_id)
    return render_template('studio/entrevista.html', consultoria=consultoria, active_page='studio')


@studio_bp.route('/api/<consultoria_id>/mensaje', methods=['POST'])
@login_required
def enviar_mensaje(consultoria_id: str):
    consultoria = Consultoria.query.get_or_404(consultoria_id)
    data = request.get_json()
    mensaje = data.get('mensaje', '')
    
    try:
        resultado = entrevista_service.procesar_mensaje(consultoria_id, mensaje)
        return jsonify({'ok': True, **resultado})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@studio_bp.route('/api/<consultoria_id>/generar-blueprint', methods=['POST'])
@login_required
def generar_blueprint(consultoria_id: str):
    """Genera el Blueprint completo: AS IS + TO BE + brechas + plan en una sola llamada."""
    try:
        blueprint = entrevista_service.generar_blueprint(consultoria_id)
        return jsonify({'ok': True, **blueprint})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@studio_bp.route('/<consultoria_id>/gemelo-asis')
@login_required
def gemelo_asis(consultoria_id: str):
    consultoria = Consultoria.query.get_or_404(consultoria_id)
    twin = twin_service.get_asis(consultoria_id)
    twin_tobe = twin_service.get_tobe(consultoria_id)
    brechas_list = brecha_service.get_brechas(consultoria_id)
    plan_data = plan_service.get_plan(consultoria_id)
    return render_template('studio/gemelo_asis.html', consultoria=consultoria, twin=twin, twin_tobe=twin_tobe, brechas=brechas_list, plan=plan_data, active_page='studio')


@studio_bp.route('/<consultoria_id>/plan')
@login_required
def plan(consultoria_id: str):
    consultoria = Consultoria.query.get_or_404(consultoria_id)
    plan_data = plan_service.get_plan(consultoria_id)
    twin_tobe = twin_service.get_tobe(consultoria_id)
    brechas_list = brecha_service.get_brechas(consultoria_id)
    return render_template('studio/plan.html', consultoria=consultoria, plan=plan_data, twin_tobe=twin_tobe, brechas=brechas_list, active_page='studio')


@studio_bp.route('/<consultoria_id>/constructor')
@login_required
def constructor(consultoria_id: str):
    consultoria = Consultoria.query.get_or_404(consultoria_id)
    twin_asis = twin_service.get_asis(consultoria_id)
    twin_tobe = twin_service.get_tobe(consultoria_id)
    brechas_list = brecha_service.get_brechas(consultoria_id)
    plan_data = plan_service.get_plan(consultoria_id)
    return render_template('studio/constructor.html', consultoria=consultoria,
                          twin_asis=twin_asis, twin_tobe=twin_tobe,
                          brechas=brechas_list, plan=plan_data, active_page='studio')


@studio_bp.route('/api/<consultoria_id>/generar-arquitectura', methods=['POST'])
@login_required
def generar_arquitectura(consultoria_id: str):
    try:
        twin_asis = twin_service.get_asis(consultoria_id)
        twin_tobe = twin_service.get_tobe(consultoria_id)
        brechas_list = brecha_service.get_brechas(consultoria_id)
        plan_data = plan_service.get_plan(consultoria_id)
        
        datos = constructor_service.generar_modelo_datos(twin_asis, twin_tobe, brechas_list)
        api_especs = constructor_service.generar_api(twin_tobe, str(twin_asis.get('capas', {}).get('procesos', {})), str(twin_asis.get('capas', {}).get('servicios', {})))
        arquitectura = constructor_service.generar_arquitectura(twin_tobe, plan_data)
        roadmap = constructor_service.generar_roadmap(brechas_list, plan_data, arquitectura)
        
        return jsonify({'ok': True, 'datos': datos, 'api': api_especs, 'arquitectura': arquitectura, 'roadmap': roadmap})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@studio_bp.route('/api/<consultoria_id>/descargar-codigo', methods=['POST'])
@login_required
def descargar_codigo(consultoria_id: str):
    from flask import send_file
    data = request.get_json()
    consultoria = Consultoria.query.get_or_404(consultoria_id)
    buffer = generate_project_zip(
        data.get('datos', {}),
        data.get('api', {}),
        data.get('arquitectura', {}),
        f'srie-{consultoria.cliente.company_name}'.replace(' ', '-')
    )
    return send_file(buffer, mimetype='application/zip', as_attachment=True, download_name=f'srie-{consultoria.cliente.company_name}.zip'.replace(' ', '-'))


@studio_bp.route('/api/<consultoria_id>/generar-deploy', methods=['POST'])
@login_required
def generar_deploy(consultoria_id: str):
    from flask import send_file
    try:
        data = request.get_json()
        consultoria = Consultoria.query.get_or_404(consultoria_id)
        project_name = f'srie-{consultoria.cliente.company_name}'.replace(' ', '-').lower()
        buffer = generate_full_project(data.get('datos', {}), data.get('api', {}), data.get('arquitectura', {}), project_name)
        return send_file(buffer, mimetype='application/zip', as_attachment=True, download_name=f'{project_name}-deploy.zip')
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@studio_bp.route('/api/<consultoria_id>/generar-codigo', methods=['POST'])
@login_required
def generar_codigo(consultoria_id: str):
    try:
        data = request.get_json()
        modelo_datos = data.get('datos', {})
        api_especs = data.get('api', {})
        arquitectura = data.get('arquitectura', {})
        
        codigo = {
            'modelos_py': generate_models_py(modelo_datos),
            'rutas_py': generate_routes_py(api_especs),
            'dockerfile': generate_dockerfile(arquitectura),
            'requirements_txt': generate_requirements(api_especs),
        }
        return jsonify({'ok': True, 'codigo': codigo})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@studio_bp.route('/<consultoria_id>/cotizacion', methods=['POST'])
@login_required
def cotizacion(consultoria_id: str):
    consultoria = Consultoria.query.get_or_404(consultoria_id)
    plan_data = plan_service.get_plan(consultoria_id)
    
    try:
        items = []
        for item in plan_data.get('items', []):
            items.append({
                'item_type': 'capability',
                'description': f"{item.get('modulo', 'Modulo')}: {item.get('descripcion', item.get('justificacion', ''))}",
                'unit_price': float(item.get('precio', 0)),
                'quantity': 1,
            })
        
        quotation = QuotationService.create(
            client_id=consultoria.cliente_id,
            title=f'Plan Empresarial - {consultoria.cliente.company_name}',
            items=items,
            scope='Implementacion del plan basado en el Blueprint Empresarial generado por SRIE Engine.',
            created_by=str(consultoria.id),
        )
        flash(f'Cotizacion {quotation.quotation_number} creada', 'success')
        return redirect(url_for('studio.propuesta', consultoria_id=consultoria_id))
    except Exception as e:
        flash(f'Error generando cotizacion: {str(e)}', 'error')
        return redirect(url_for('studio.plan', consultoria_id=consultoria_id))


@studio_bp.route('/<consultoria_id>/propuesta')
@login_required
def propuesta(consultoria_id: str):
    consultoria = Consultoria.query.get_or_404(consultoria_id)
    quotation = Quotation.query.filter_by(created_by=str(consultoria_id)).order_by(Quotation.created_at.desc()).first()
    
    twin_asis = twin_service.get_asis(consultoria_id)
    twin_tobe = twin_service.get_tobe(consultoria_id)
    brechas_list = brecha_service.get_brechas(consultoria_id)
    plan_data = plan_service.get_plan(consultoria_id)
    
    return render_template('studio/propuesta.html', consultoria=consultoria, quotation=quotation,
                          twin_asis=twin_asis, twin_tobe=twin_tobe, brechas=brechas_list,
                          plan=plan_data, active_page='studio')


@studio_bp.route('/<consultoria_id>/pdf')
@login_required
def descargar_pdf(consultoria_id: str):
    from flask import send_file
    
    consultoria = Consultoria.query.get_or_404(consultoria_id)
    quotation = Quotation.query.filter_by(created_by=str(consultoria_id)).order_by(Quotation.created_at.desc()).first()
    
    try:
        from core.services.pdf_service import generate_quotation_pdf
        pdf_buffer = generate_quotation_pdf(quotation)
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'propuesta-{quotation.quotation_number}.pdf',
        )
    except Exception as e:
        flash(f'Error generando PDF: {str(e)}', 'error')
        return redirect(url_for('studio.propuesta', consultoria_id=consultoria_id))


@studio_bp.route('/<consultoria_id>/blueprint-pdf')
@login_required
def descargar_blueprint_pdf(consultoria_id: str):
    """Genera PDF del Blueprint Empresarial completo."""
    from flask import send_file, render_template
    from weasyprint import HTML
    import tempfile, io, os as _os
    
    consultoria = Consultoria.query.get_or_404(consultoria_id)
    twin_asis = twin_service.get_asis(consultoria_id)
    twin_tobe = twin_service.get_tobe(consultoria_id)
    brechas_list = brecha_service.get_brechas(consultoria_id)
    plan_data = plan_service.get_plan(consultoria_id)
    
    html_string = render_template(
        'pdfs/blueprint_report.html',
        consultoria=consultoria,
        twin_asis=twin_asis,
        twin_tobe=twin_tobe,
        brechas=brechas_list,
        plan=plan_data,
    )
    
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        tmp_path = tmp.name
    try:
        HTML(string=html_string).write_pdf(tmp_path)
        with open(tmp_path, 'rb') as f:
            buffer = io.BytesIO(f.read())
        buffer.seek(0)
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'blueprint-{consultoria.cliente.company_name}.pdf'.replace(' ', '-'),
        )
    finally:
        _os.unlink(tmp_path)


@studio_bp.route('/api/clientes/search')
@login_required
def clientes_search():
    q = request.args.get('q', '')
    clients = Client.query.filter(
        Client.company_name.ilike(f'%{q}%') | Client.contact_name.ilike(f'%{q}%')
    ).limit(10).all()
    return jsonify([{'id': c.id, 'text': f'{c.company_name} - {c.contact_name}'} for c in clients])
