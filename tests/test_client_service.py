"""Tests for ClientService."""
import pytest
from core import db
from core.models.client import Client
from core.services.client_service import ClientService
from core.errors import NotFoundError, ConflictError


def test_get_all(app):
    with app.app_context():
        client = Client(
            company_name='Test Corp',
            contact_name='John Doe',
            contact_email='getall@test.com',
        )
        db.session.add(client)
        db.session.commit()

        clients = ClientService.get_all()
        assert len(clients) >= 1
        assert any(c.company_name == 'Test Corp' for c in clients)


def test_get_by_id(app):
    with app.app_context():
        client = Client(
            company_name='Test Corp 2',
            contact_name='John Doe',
            contact_email='getbyid@test.com',
        )
        db.session.add(client)
        db.session.commit()

        found = ClientService.get_by_id(client.id)
        assert found.company_name == 'Test Corp 2'
        assert found.contact_email == 'getbyid@test.com'


def test_get_by_id_not_found(app):
    with app.app_context():
        with pytest.raises(NotFoundError):
            ClientService.get_by_id('nonexistent-id')


def test_create(app):
    with app.app_context():
        client = ClientService.create(
            company_name='New Corp',
            contact_name='Jane Doe',
            contact_email='create@test.com',
            contact_phone='+573001234567',
        )
        assert client.id is not None
        assert client.company_name == 'New Corp'

        found = Client.query.get(client.id)
        assert found is not None


def test_create_duplicate_email(app):
    with app.app_context():
        ClientService.create(
            company_name='First Corp',
            contact_name='John',
            contact_email='dup@test.com',
        )
        with pytest.raises(ConflictError):
            ClientService.create(
                company_name='Second Corp',
                contact_name='Jane',
                contact_email='dup@test.com',
            )


def test_update(app):
    with app.app_context():
        client = Client(
            company_name='Old Name',
            contact_name='John',
            contact_email='update@test.com',
        )
        db.session.add(client)
        db.session.commit()

        updated = ClientService.update(client.id, company_name='New Name')
        assert updated.company_name == 'New Name'

        found = Client.query.get(client.id)
        assert found.company_name == 'New Name'


def test_update_not_found(app):
    with app.app_context():
        with pytest.raises(NotFoundError):
            ClientService.update('nonexistent-id', company_name='X')


def test_delete(app):
    with app.app_context():
        client = Client(
            company_name='To Delete',
            contact_name='John',
            contact_email='delete@test.com',
        )
        db.session.add(client)
        db.session.commit()
        client_id = client.id

        ClientService.delete(client_id)
        assert Client.query.get(client_id) is None


def test_delete_not_found(app):
    with app.app_context():
        with pytest.raises(NotFoundError):
            ClientService.delete('nonexistent-id')
