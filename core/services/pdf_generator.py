import io
import tempfile
from weasyprint import HTML
from flask import render_template


def generate_quotation_pdf(quotation):
    """Generate a PDF for a quotation and return as BytesIO."""
    html_string = render_template('pdfs/quotation.html', quotation=quotation)
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        tmp_path = tmp.name
    HTML(string=html_string).write_pdf(tmp_path)
    with open(tmp_path, 'rb') as f:
        pdf_buffer = io.BytesIO(f.read())
    import os
    os.unlink(tmp_path)
    pdf_buffer.seek(0)
    return pdf_buffer
