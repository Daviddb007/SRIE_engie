"""Service layer for PDF generation."""
from __future__ import annotations

import io
import tempfile
import os
from datetime import datetime

from flask import render_template
from weasyprint import HTML


def generate_quotation_pdf(quotation) -> io.BytesIO:
    """Generate a professional PDF for a quotation."""
    html_string = render_template('pdfs/quotation.html', quotation=quotation)
    return _html_to_pdf(html_string, f'cotizacion-{quotation.quotation_number}.pdf')


def generate_intelligence_report_pdf(
    company_name: str,
    contact_name: str,
    diagnosis: dict,
    generated_at: str | None = None,
) -> io.BytesIO:
    """Generate an Intelligence diagnostic report PDF."""
    if generated_at is None:
        generated_at = datetime.now().strftime('%d/%m/%Y %H:%M')

    html_string = render_template(
        'pdfs/intelligence_report.html',
        company_name=company_name,
        contact_name=contact_name,
        diagnosis=diagnosis,
        generated_at=generated_at,
    )
    return _html_to_pdf(html_string, 'informe-diagnostico-stonelytics.pdf')


def _html_to_pdf(html_string: str, filename: str) -> io.BytesIO:
    """Convert HTML string to PDF BytesIO buffer."""
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        tmp_path = tmp.name
    try:
        HTML(string=html_string).write_pdf(tmp_path)
        with open(tmp_path, 'rb') as f:
            buffer = io.BytesIO(f.read())
        buffer.seek(0)
        return buffer
    finally:
        os.unlink(tmp_path)
