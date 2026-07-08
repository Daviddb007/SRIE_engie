import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://stonelytics:stonelytics@localhost:5432/stonelytics'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.hostinger.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')

    # Business
    WHATSAPP_NUMBER = os.getenv('WHATSAPP_NUMBER', '573057708315')
    CONTACT_EMAIL = os.getenv('CONTACT_EMAIL', 'daviddb@stonelytics.tech')

    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

    # Admin
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'daviddb@stonelytics.tech')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'StonelyticsAdmin2026!')
