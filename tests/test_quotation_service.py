"""Tests for QuotationService."""
import pytest
from core import db
from core.models.client import Client
from core.services.quotation_service import QuotationService
from core.errors import NotFoundError, ValidationError


def _create_client(app, suffix=''):
    client = Client(
        company_name=f'Quote Corp {suffix}',
        contact_name='John',
        contact_email=f'quote{suffix}@test.com',
    )
    db.session.add(client)
    db.session.commit()
    return client


def test_calculate(app):
    with app.app_context():
        items = [
            {'description': 'Item 1', 'unit_price': 100, 'quantity': 2},
            {'description': 'Item 2', 'unit_price': 50, 'quantity': 1},
        ]
        result = QuotationService.calculate(items, discount_pct=10)
        assert result['total'] == 250.0
        assert result['discount'] == 25.0
        assert result['final'] == 225.0


def test_calculate_no_discount(app):
    with app.app_context():
        items = [
            {'description': 'Item 1', 'unit_price': 200, 'quantity': 1},
        ]
        result = QuotationService.calculate(items)
        assert result['total'] == 200.0
        assert result['discount'] == 0.0
        assert result['final'] == 200.0


def test_create(app):
    with app.app_context():
        client = _create_client(app, 'create')
        items = [
            {'description': 'Landing Page', 'unit_price': 500, 'quantity': 1},
            {'description': 'Quiz Module', 'unit_price': 300, 'quantity': 1},
        ]
        q = QuotationService.create(
            client_id=client.id,
            title='Test Quotation',
            items=items,
            discount_pct=0,
        )
        assert q.id is not None
        assert q.quotation_number.startswith('QT-')
        assert float(q.total_price) == 800.0
        assert float(q.final_price) == 800.0


def test_create_with_discount(app):
    with app.app_context():
        client = _create_client(app, 'discount')
        items = [
            {'description': 'Service', 'unit_price': 1000, 'quantity': 1},
        ]
        q = QuotationService.create(
            client_id=client.id,
            title='Discounted Quote',
            items=items,
            discount_pct=15,
        )
        assert float(q.total_price) == 1000.0
        assert float(q.final_price) == 850.0


def test_create_no_client(app):
    with app.app_context():
        with pytest.raises(ValidationError):
            QuotationService.create(
                client_id='',
                title='No Client',
                items=[{'description': 'X', 'unit_price': 100, 'quantity': 1}],
            )


def test_create_invalid_client(app):
    with app.app_context():
        with pytest.raises(NotFoundError):
            QuotationService.create(
                client_id='nonexistent',
                title='Bad Client',
                items=[{'description': 'X', 'unit_price': 100, 'quantity': 1}],
            )


def test_get_all(app):
    with app.app_context():
        client = _create_client(app, 'getall')
        QuotationService.create(
            client_id=client.id,
            title='Quote 1',
            items=[{'description': 'A', 'unit_price': 100, 'quantity': 1}],
        )
        quotations = QuotationService.get_all()
        assert len(quotations) >= 1


def test_get_by_id(app):
    with app.app_context():
        client = _create_client(app, 'getbyid')
        q = QuotationService.create(
            client_id=client.id,
            title='Find Me',
            items=[{'description': 'A', 'unit_price': 100, 'quantity': 1}],
        )
        found = QuotationService.get_by_id(q.id)
        assert found.title == 'Find Me'


def test_get_by_id_not_found(app):
    with app.app_context():
        with pytest.raises(NotFoundError):
            QuotationService.get_by_id('nonexistent')
