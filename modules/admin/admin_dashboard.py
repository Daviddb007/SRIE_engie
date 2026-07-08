"""Admin dashboard routes."""
from __future__ import annotations

from flask import Blueprint, render_template
from flask_login import login_required

from core.models import Client, Project, Quotation
from core.models.consultoria import Consultoria
from core.services import ClientService, ProjectService, QuotationService
from core.utils import build_statistics, get_sorted_recent_items

admin_dashboard_bp = Blueprint('admin_dashboard', __name__, template_folder='templates')


@admin_dashboard_bp.route('/')
@login_required
def dashboard():
    """Display admin dashboard with statistics."""
    clients = ClientService.get_all()
    projects = ProjectService.get_all()
    quotations = QuotationService.get_all()
    consultorias = Consultoria.query.order_by(Consultoria.created_at.desc()).all()
    
    studio_stats = {
        'total': len(consultorias),
        'completadas': sum(1 for c in consultorias if c.estado == 'completada'),
        'activas': sum(1 for c in consultorias if c.estado in ('activa', 'borrador')),
        'industrias': {},
    }
    for c in consultorias:
        ind = c.industria or 'general'
        studio_stats['industrias'][ind] = studio_stats['industrias'].get(ind, 0) + 1
    
    stats = build_statistics({
        'clients': clients,
        'projects': projects,
        'quotations': quotations,
    })
    
    context = {
        'stats': stats,
        'studio_stats': studio_stats,
        'clients': clients,
        'projects': projects,
        'quotations': quotations,
        'consultorias': consultorias,
    }
    
    recent_items = {
        'projects': get_sorted_recent_items(Project.query.order_by(Project.created_at.desc()), 5),
        'quotations': get_sorted_recent_items(Quotation.query.order_by(Quotation.created_at.desc()), 5),
    }
    
    context.update(recent_items)
    return render_template('admin/dashboard.html', **context)
