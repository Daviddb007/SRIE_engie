"""Shared test fixtures."""
import sys
import os
import pytest

os.environ['FLASK_TESTING'] = '1'

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 25
    MAIL_USERNAME = None
    MAIL_PASSWORD = None


@pytest.fixture(scope='session')
def app():
    from app import create_app
    app = create_app(TestConfig)
    with app.app_context():
        from core import db
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture(autouse=True)
def _reset_db(app):
    """Roll back each test so unique constraints don't leak."""
    with app.app_context():
        from core import db
        yield
        db.session.rollback()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
