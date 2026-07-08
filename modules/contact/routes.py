"""Contact form routes — thin handlers."""
from __future__ import annotations

from flask import Blueprint, request, jsonify, current_app

from core.services.notification_service import send_contact_email_async

contact_bp = Blueprint('contact', __name__)


@contact_bp.route('/contacto', methods=['POST'])
def contacto():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'ok': False, 'error': 'No data received'}), 400

        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        business = data.get('business_type', data.get('business', '')).strip()

        if not name or not email or not business:
            return jsonify({'ok': False, 'error': 'Required fields missing'}), 400

        send_contact_email_async(data, current_app._get_current_object())
        return jsonify({'ok': True, 'message': 'Message sent successfully'})
    except Exception as e:
        current_app.logger.error(f"Contact form error: {e}")
        return jsonify({'ok': False, 'error': 'Server error. Please try again.'}), 500
