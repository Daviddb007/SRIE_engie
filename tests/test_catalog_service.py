"""Tests for CatalogService."""
import pytest
from core import db
from core.models.capability import Capability
from core.models.automation import Automation
from core.models.service import Service
from core.services.catalog_service import CatalogService
from core.errors import NotFoundError, ConflictError


def test_get_all(app):
    with app.app_context():
        data = CatalogService.get_all()
        assert 'capabilities' in data
        assert 'automations' in data
        assert 'services' in data


def test_create_capability(app):
    with app.app_context():
        cap = CatalogService.create_capability(
            slug='test-feature',
            name='Test Feature',
            description='A test feature',
            category='test',
            base_price=250,
        )
        assert cap.id is not None
        assert cap.slug == 'test-feature'


def test_create_capability_duplicate(app):
    with app.app_context():
        CatalogService.create_capability(slug='dup', name='Dup')
        with pytest.raises(ConflictError):
            CatalogService.create_capability(slug='dup', name='Dup 2')


def test_update_capability(app):
    with app.app_context():
        cap = CatalogService.create_capability(slug='upd', name='Old')
        updated = CatalogService.update_capability(cap.id, name='New')
        assert updated.name == 'New'


def test_update_capability_not_found(app):
    with app.app_context():
        with pytest.raises(NotFoundError):
            CatalogService.update_capability('nonexistent', name='X')


def test_create_automation(app):
    with app.app_context():
        auto = CatalogService.create_automation(
            slug='test-auto',
            name='Test Auto',
            trigger_type='form_submission',
            action_type='send_email',
            base_price=100,
        )
        assert auto.id is not None
        assert auto.slug == 'test-auto'


def test_create_automation_duplicate(app):
    with app.app_context():
        CatalogService.create_automation(
            slug='dup-auto',
            name='Dup',
            trigger_type='x',
            action_type='y',
        )
        with pytest.raises(ConflictError):
            CatalogService.create_automation(
                slug='dup-auto',
                name='Dup 2',
                trigger_type='x',
                action_type='y',
            )


def test_update_automation(app):
    with app.app_context():
        auto = CatalogService.create_automation(
            slug='upd-auto',
            name='Old',
            trigger_type='x',
            action_type='y',
        )
        updated = CatalogService.update_automation(auto.id, name='New')
        assert updated.name == 'New'


def test_create_service(app):
    with app.app_context():
        svc = CatalogService.create_service(
            slug='test-svc',
            name='Test Service',
            category='infra',
            base_price=50,
            is_recurring=True,
            billing_interval='monthly',
        )
        assert svc.id is not None
        assert svc.is_recurring is True


def test_create_service_duplicate(app):
    with app.app_context():
        CatalogService.create_service(slug='dup-svc', name='Dup')
        with pytest.raises(ConflictError):
            CatalogService.create_service(slug='dup-svc', name='Dup 2')


def test_update_service(app):
    with app.app_context():
        svc = CatalogService.create_service(slug='upd-svc', name='Old')
        updated = CatalogService.update_service(svc.id, name='New')
        assert updated.name == 'New'
