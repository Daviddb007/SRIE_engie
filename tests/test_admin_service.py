"""Tests for AdminService."""
import pytest
from core.services.admin_service import AdminService
from core.errors import ValidationError


def test_validate_and_parse_calculation_data(app):
    with app.app_context():
        data = {
            'items': [
                {'description': 'Item 1', 'unit_price': 100, 'quantity': 2},
            ],
            'discount_pct': 10,
        }
        result = AdminService.validate_and_parse_calculation_data(data)
        assert result['discount_pct'] == 10.0
        assert len(result['items']) == 1


def test_validate_and_parse_calculation_data_no_items(app):
    with app.app_context():
        with pytest.raises(ValidationError):
            AdminService.validate_and_parse_calculation_data({'items': []})


def test_validate_and_parse_calculation_data_invalid_discount(app):
    with app.app_context():
        with pytest.raises(ValidationError):
            AdminService.validate_and_parse_calculation_data({
                'items': [{'description': 'X', 'unit_price': 100, 'quantity': 1}],
                'discount_pct': 150,
            })


def test_generate_quotation_number(app):
    with app.app_context():
        num = AdminService.generate_quotation_number()
        assert num.startswith('QT-')
        assert len(num.split('-')) == 3


def test_validate_form_data(app):
    with app.app_context():
        errors = AdminService.validate_form_data(
            ['name', 'email'],
            {'name': 'Test', 'email': 'test@test.com'},
        )
        assert errors == []


def test_validate_form_data_missing(app):
    with app.app_context():
        errors = AdminService.validate_form_data(
            ['name', 'email'],
            {'name': 'Test'},
        )
        assert len(errors) == 1
        assert 'email' in errors[0]


def test_sanitize_string(app):
    with app.app_context():
        result = AdminService.sanitize_string('  <script>alert("xss")</script>  ')
        assert '<script>' not in result
        assert result.strip() != ''


def test_sanitize_string_non_string(app):
    with app.app_context():
        result = AdminService.sanitize_string(None)
        assert result == ''


def test_get_paginated_data(app):
    with app.app_context():
        from core.models.client import Client
        from core import db

        for i in range(15):
            db.session.add(Client(
                company_name=f'Client {i}',
                contact_name=f'Person {i}',
                contact_email=f'client{i}@test.com',
            ))
        db.session.commit()

        query = Client.query.order_by(Client.created_at.desc())
        items, total_pages = AdminService.get_paginated_data(query, page=1, per_page=5)
        assert len(items) == 5
        assert total_pages == 3
