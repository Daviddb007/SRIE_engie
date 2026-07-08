"""Admin catalog routes."""
from __future__ import annotations

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required

from core.services import CatalogService
from core.models.capability import Capability
from core.models.automation import Automation
from core.models.service import Service

admin_catalog_bp = Blueprint('admin_catalog', __name__, template_folder='templates')


@admin_catalog_bp.route('/catalog')
@login_required
def list_catalog():
    """List all catalog items."""
    data = CatalogService.get_all()
    return render_template('admin/catalog.html', **data)


@admin_catalog_bp.route('/catalog/capability/new', methods=['GET', 'POST'])
@login_required
def create_capability():
    """Create a new capability."""
    if request.method == 'POST':
        CatalogService.create_capability(
            slug=request.form['slug'],
            name=request.form['name'],
            description=request.form.get('description', ''),
            category=request.form.get('category', ''),
            base_price=float(request.form.get('base_price', 0)),
            is_active_='is_active' in request.form,
        )
        flash('Capacidad creada', 'success')
        return redirect(url_for('admin_catalog.list_catalog'))
    return render_template('admin/catalog_form.html', item_type='capability', item=None)


@admin_catalog_bp.route('/catalog/capability/<item_id>/edit', methods=['GET', 'POST'])
@login_required
def update_capability(item_id):
    """Update a capability."""
    cap = Capability.query.get_or_404(item_id)
    if request.method == 'POST':
        CatalogService.update_capability(
            item_id,
            slug=request.form['slug'],
            name=request.form['name'],
            description=request.form.get('description', ''),
            category=request.form.get('category', ''),
            base_price=float(request.form.get('base_price', 0)),
            is_active_='is_active' in request.form,
        )
        flash('Capacidad actualizada', 'success')
        return redirect(url_for('admin_catalog.list_catalog'))
    return render_template('admin/catalog_form.html', item_type='capability', item=cap)


@admin_catalog_bp.route('/catalog/automation/new', methods=['GET', 'POST'])
@login_required
def create_automation():
    """Create a new automation."""
    if request.method == 'POST':
        CatalogService.create_automation(
            slug=request.form['slug'],
            name=request.form['name'],
            description=request.form.get('description', ''),
            trigger_type=request.form['trigger_type'],
            action_type=request.form['action_type'],
            base_price=float(request.form.get('base_price', 0)),
            is_active_='is_active' in request.form,
        )
        flash('Automatización creada', 'success')
        return redirect(url_for('admin_catalog.list_catalog'))
    return render_template('admin/catalog_form.html', item_type='automation', item=None)


@admin_catalog_bp.route('/catalog/automation/<item_id>/edit', methods=['GET', 'POST'])
@login_required
def update_automation(item_id):
    """Update an automation."""
    auto = Automation.query.get_or_404(item_id)
    if request.method == 'POST':
        CatalogService.update_automation(
            item_id,
            slug=request.form['slug'],
            name=request.form['name'],
            description=request.form.get('description', ''),
            trigger_type=request.form['trigger_type'],
            action_type=request.form['action_type'],
            base_price=float(request.form.get('base_price', 0)),
            is_active_='is_active' in request.form,
        )
        flash('Automatización actualizada', 'success')
        return redirect(url_for('admin_catalog.list_catalog'))
    return render_template('admin/catalog_form.html', item_type='automation', item=auto)


@admin_catalog_bp.route('/catalog/service/new', methods=['GET', 'POST'])
@login_required
def create_service():
    """Create a new service."""
    if request.method == 'POST':
        CatalogService.create_service(
            slug=request.form['slug'],
            name=request.form['name'],
            description=request.form.get('description', ''),
            category=request.form.get('category', ''),
            base_price=float(request.form.get('base_price', 0)),
            is_recurring='is_recurring' in request.form,
            billing_interval=request.form.get('billing_interval', ''),
            is_active_='is_active' in request.form,
        )
        flash('Servicio creado', 'success')
        return redirect(url_for('admin_catalog.list_catalog'))
    return render_template('admin/catalog_form.html', item_type='service', item=None)


@admin_catalog_bp.route('/catalog/service/<item_id>/edit', methods=['GET', 'POST'])
@login_required
def update_service(item_id):
    """Update a service."""
    svc = Service.query.get_or_404(item_id)
    if request.method == 'POST':
        CatalogService.update_service(
            item_id,
            slug=request.form['slug'],
            name=request.form['name'],
            description=request.form.get('description', ''),
            category=request.form.get('category', ''),
            base_price=float(request.form.get('base_price', 0)),
            is_recurring='is_recurring' in request.form,
            billing_interval=request.form.get('billing_interval', ''),
            is_active_='is_active' in request.form,
        )
        flash('Servicio actualizado', 'success')
        return redirect(url_for('admin_catalog.list_catalog'))
    return render_template('admin/catalog_form.html', item_type='service', item=svc)
