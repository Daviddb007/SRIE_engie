"""Admin quotations routes."""
from __future__ import annotations

from flask import Blueprint, render_template, redirect, url_for, flash, send_file
from flask_login import login_required

from core.services import QuotationService, generate_quotation_pdf

admin_quotations_bp = Blueprint('admin_quotations', __name__, template_folder='templates')


@admin_quotations_bp.route('/quotations')
@login_required
def list_quotations():
    """List all quotations."""
    quotations = QuotationService.get_all()
    return render_template('admin/quotations.html', quotations=quotations)


@admin_quotations_bp.route('/quotations/<quotation_id>')
@login_required
def detail_quotation(quotation_id):
    """View quotation details."""
    quotation = QuotationService.get_by_id(quotation_id)
    return render_template('admin/quotation_detail.html', quotation=quotation)


@admin_quotations_bp.route('/quotations/<quotation_id>/pdf')
@login_required
def quotation_pdf(quotation_id):
    """Download quotation as PDF."""
    quotation = QuotationService.get_by_id(quotation_id)
    pdf_buffer = generate_quotation_pdf(quotation)
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'cotizacion-{quotation.quotation_number}.pdf',
    )
