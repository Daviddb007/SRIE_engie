"""Admin clients routes."""
from __future__ import annotations

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required

from core.models.client import Client
from core.models.project import Project
from core.services import ClientService

admin_clients_bp = Blueprint('admin_clients', __name__, template_folder='templates')


@admin_clients_bp.route('/clients')
@login_required
def list_clients():
    """List all clients."""
    clients = ClientService.get_all()
    return render_template('admin/clients.html', clients=clients)


@admin_clients_bp.route('/clients/new', methods=['GET', 'POST'])
@login_required
def create_client():
    """Create a new client."""
    if request.method == 'POST':
        ClientService.create(
            company_name=request.form['company_name'],
            contact_name=request.form['contact_name'],
            contact_email=request.form['contact_email'],
            contact_phone=request.form.get('contact_phone', ''),
            contact_whatsapp=request.form.get('contact_whatsapp', ''),
            industry=request.form.get('industry', ''),
            website=request.form.get('website', ''),
            city=request.form.get('city', ''),
            country=request.form.get('country', 'Colombia'),
            notes=request.form.get('notes', ''),
        )
        flash('Cliente creado exitosamente', 'success')
        return redirect(url_for('admin_clients.list_clients'))
    return render_template('admin/client_form.html', client=None)


@admin_clients_bp.route('/clients/<client_id>')
@login_required
def detail_client(client_id):
    """View client details."""
    client = ClientService.get_by_id(client_id)
    projects = Project.query.filter_by(client_id=client_id).all() if client else []
    return render_template('admin/client_detail.html', client=client, projects=projects)


@admin_clients_bp.route('/clients/<client_id>/edit', methods=['GET', 'POST'])
@login_required
def update_client(client_id):
    """Update a client."""
    client = ClientService.get_by_id(client_id)
    if request.method == 'POST':
        ClientService.update(
            client_id,
            company_name=request.form['company_name'],
            contact_name=request.form['contact_name'],
            contact_email=request.form['contact_email'],
            contact_phone=request.form.get('contact_phone', ''),
            contact_whatsapp=request.form.get('contact_whatsapp', ''),
            industry=request.form.get('industry', ''),
            website=request.form.get('website', ''),
            city=request.form.get('city', ''),
            country=request.form.get('country', 'Colombia'),
            notes=request.form.get('notes', ''),
        )
        flash('Cliente actualizado', 'success')
        return redirect(url_for('admin_clients.detail_client', client_id=client_id))
    return render_template('admin/client_form.html', client=client)