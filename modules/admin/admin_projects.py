"""Admin projects routes."""
from __future__ import annotations

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from flask_login import current_user

from core.models.project import Project
from core.models.client import Client
from core.services import ProjectService

admin_projects_bp = Blueprint('admin_projects', __name__, template_folder='templates')


@admin_projects_bp.route('/projects')
@login_required
def list_projects():
    """List all projects."""
    projects = ProjectService.get_all()
    return render_template('admin/projects.html', projects=projects)


@admin_projects_bp.route('/projects/new', methods=['GET', 'POST'])
@login_required
def create_project():
    """Create a new project."""
    clients = Client.query.order_by(Client.company_name).all()
    if request.method == 'POST':
        ProjectService.create(
            client_id=request.form['client_id'],
            name=request.form['name'],
            system_type=request.form.get('system_type', 'start'),
            status=request.form.get('status', 'draft'),
            description=request.form.get('description', ''),
            domain=request.form.get('domain', ''),
            hosting_provider=request.form.get('hosting_provider', ''),
            notes=request.form.get('notes', ''),
            created_by=current_user.id,
        )
        flash('Proyecto creado exitosamente', 'success')
        return redirect(url_for('admin_projects.list_projects'))
    return render_template('admin/project_form.html', project=None, clients=clients)


@admin_projects_bp.route('/projects/<project_id>/edit', methods=['GET', 'POST'])
@login_required
def update_project(project_id):
    """Update a project."""
    project = ProjectService.get_by_id(project_id)
    clients = Client.query.order_by(Client.company_name).all()
    if request.method == 'POST':
        ProjectService.update(
            project_id,
            client_id=request.form['client_id'],
            name=request.form['name'],
            system_type=request.form.get('system_type', 'start'),
            status=request.form.get('status', 'draft'),
            description=request.form.get('description', ''),
            domain=request.form.get('domain', ''),
            hosting_provider=request.form.get('hosting_provider', ''),
            notes=request.form.get('notes', ''),
        )
        flash('Proyecto actualizado', 'success')
        return redirect(url_for('admin_projects.detail_project', project_id=project_id))
    return render_template('admin/project_form.html', project=project, clients=clients)


@admin_projects_bp.route('/projects/<project_id>')
@login_required
def detail_project(project_id):
    """View project details."""
    project = ProjectService.get_by_id(project_id)
    return render_template('admin/project_detail.html', project=project)
