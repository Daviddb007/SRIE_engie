"""Admin projects management routes (add/remove relationships)."""
from __future__ import annotations

from flask import Blueprint, redirect, url_for, flash, request
from flask_login import login_required

from core.services.project_service import ProjectService

admin_projects_management_bp = Blueprint('admin_projects_management', __name__, template_folder='templates')


@admin_projects_management_bp.route('/projects/<project_id>/add-capability', methods=['POST'])
@login_required
def add_capability(project_id):
    """Add capability to project."""
    cap_id = request.form.get('capability_id')
    if cap_id:
        try:
            ProjectService.add_capability(project_id, cap_id)
            flash('Capacidad agregada', 'success')
        except Exception as e:
            flash(str(e), 'error')
    return redirect(url_for('admin_projects.detail_project', project_id=project_id))


@admin_projects_management_bp.route('/projects/<project_id>/remove-capability/<pc_id>', methods=['POST'])
@login_required
def remove_capability(project_id, pc_id):
    """Remove capability from project."""
    ProjectService.remove_capability(pc_id)
    flash('Capacidad removida', 'success')
    return redirect(url_for('admin_projects.detail_project', project_id=project_id))


@admin_projects_management_bp.route('/projects/<project_id>/add-automation', methods=['POST'])
@login_required
def add_automation(project_id):
    """Add automation to project."""
    auto_id = request.form.get('automation_id')
    if auto_id:
        try:
            ProjectService.add_automation(project_id, auto_id)
            flash('Automatización agregada', 'success')
        except Exception as e:
            flash(str(e), 'error')
    return redirect(url_for('admin_projects.detail_project', project_id=project_id))


@admin_projects_management_bp.route('/projects/<project_id>/remove-automation/<pa_id>', methods=['POST'])
@login_required
def remove_automation(project_id, pa_id):
    """Remove automation from project."""
    ProjectService.remove_automation(pa_id)
    flash('Automatización removida', 'success')
    return redirect(url_for('admin_projects.detail_project', project_id=project_id))


@admin_projects_management_bp.route('/projects/<project_id>/add-service', methods=['POST'])
@login_required
def add_service(project_id):
    """Add service to project."""
    svc_id = request.form.get('service_id')
    if svc_id:
        try:
            ProjectService.add_service(project_id, svc_id)
            flash('Servicio agregado', 'success')
        except Exception as e:
            flash(str(e), 'error')
    return redirect(url_for('admin_projects.detail_project', project_id=project_id))


@admin_projects_management_bp.route('/projects/<project_id>/remove-service/<ps_id>', methods=['POST'])
@login_required
def remove_service(project_id, ps_id):
    """Remove service from project."""
    ProjectService.remove_service(ps_id)
    flash('Servicio removido', 'success')
    return redirect(url_for('admin_projects.detail_project', project_id=project_id))
