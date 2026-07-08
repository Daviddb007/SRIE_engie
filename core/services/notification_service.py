"""Service layer for notifications (Telegram, Email)."""
from __future__ import annotations

import threading
from flask import current_app, Flask
from flask_mail import Message
import requests as http_requests


def send_telegram_async(message: str, app: Flask) -> None:
    """Send a Telegram message in a background thread."""
    def _send():
        with app.app_context():
            try:
                bot_token = app.config.get('TELEGRAM_BOT_TOKEN', '')
                chat_id = app.config.get('TELEGRAM_CHAT_ID', '')
                if bot_token and chat_id:
                    http_requests.post(
                        f'https://api.telegram.org/bot{bot_token}/sendMessage',
                        json={'chat_id': chat_id, 'text': message, 'parse_mode': 'Markdown'},
                        timeout=10,
                    )
                    app.logger.info(f'Telegram sent: {message[:50]}...')
            except Exception as e:
                app.logger.error(f'Telegram failed: {e}')

    threading.Thread(target=_send, daemon=True).start()


def send_contact_email_async(data: dict, app: Flask) -> None:
    """Send contact form email in a background thread."""
    def _send():
        with app.app_context():
            try:
                business = data.get('business_type', data.get('business', ''))
                body = (
                    f"New contact from Stonelytics website\n\n"
                    f"Name: {data['name']}\n"
                    f"Email: {data['email']}\n"
                    f"WhatsApp: {data.get('whatsapp', '')}\n"
                    f"Business Type: {business}\n"
                    f"Team Size: {data.get('team_size', '')}\n"
                    f"Challenge: {data.get('challenge', '')}\n"
                    f"Acquisition: {data.get('acquisition', '')}\n"
                    f"Process: {data.get('process', '')}\n"
                    f"Message: {data.get('message', '')}\n"
                )
                msg = Message(
                    subject=f"New contact: {data['name']} - {business}",
                    sender=app.config['MAIL_USERNAME'],
                    recipients=[app.config['CONTACT_EMAIL']],
                    body=body,
                )
                mail = app.extensions.get('mail')
                if mail:
                    mail.send(msg)
            except Exception as e:
                app.logger.error(f'Contact email failed: {e}')

    threading.Thread(target=_send, daemon=True).start()
