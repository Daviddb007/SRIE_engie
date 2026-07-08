"""Landing page route."""
from __future__ import annotations

from flask import Blueprint, render_template, current_app

landing_bp = Blueprint('landing', __name__, template_folder='templates')


@landing_bp.route('/')
def index():
    whatsapp = current_app.config.get('WHATSAPP_NUMBER', '573057708315')
    return render_template('index.html', whatsapp_number=whatsapp)
