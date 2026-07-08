"""Tests for ProjectService."""
import pytest
from core import db
from core.models.client import Client
from core.models.project import Project
from core.models.capability import Capability
from core.models.automation import Automation
from core.models.service import Service
from core.services.project_service import ProjectService
from core.errors import NotFoundError, ConflictError


def _create_client(app, suffix=''):
    client = Client(
        company_name=f'Test Corp {suffix}',
        contact_name='John',
        contact_email=f'john{suffix}@test.com',
    )
    db.session.add(client)
    db.session.commit()
    return client


def test_get_all(app):
    with app.app_context():
        client = _create_client(app, 'getall')
        project = Project(
            client_id=client.id,
            name='Test Project',
            system_type='start',
            status='draft',
        )
        db.session.add(project)
        db.session.commit()

        projects = ProjectService.get_all()
        assert len(projects) >= 1


def test_get_by_id(app):
    with app.app_context():
        client = _create_client(app, 'getbyid')
        project = Project(
            client_id=client.id,
            name='My Project',
            system_type='growth',
            status='active',
        )
        db.session.add(project)
        db.session.commit()

        found = ProjectService.get_by_id(project.id)
        assert found.name == 'My Project'
        assert found.system_type == 'growth'


def test_get_by_id_not_found(app):
    with app.app_context():
        with pytest.raises(NotFoundError):
            ProjectService.get_by_id('nonexistent-id')


def test_create(app):
    with app.app_context():
        client = _create_client(app, 'create')
        project = ProjectService.create(
            client_id=client.id,
            name='New Project',
            system_type='intelligence',
            status='draft',
        )
        assert project.id is not None
        assert project.name == 'New Project'


def test_update(app):
    with app.app_context():
        client = _create_client(app, 'update')
        project = Project(
            client_id=client.id,
            name='Old Name',
            system_type='start',
            status='draft',
        )
        db.session.add(project)
        db.session.commit()

        updated = ProjectService.update(project.id, name='New Name', status='active')
        assert updated.name == 'New Name'
        assert updated.status == 'active'


def test_add_capability(app):
    with app.app_context():
        client = _create_client(app, 'addcap')
        project = Project(
            client_id=client.id,
            name='Cap Test',
            system_type='start',
            status='draft',
        )
        cap = Capability(slug='test-cap', name='Test Cap', base_price=100)
        db.session.add_all([project, cap])
        db.session.commit()

        pc = ProjectService.add_capability(project.id, cap.id)
        assert pc.project_id == project.id
        assert pc.capability_id == cap.id


def test_add_capability_duplicate(app):
    with app.app_context():
        client = _create_client(app, 'dupcap')
        project = Project(
            client_id=client.id,
            name='Dup Test',
            system_type='start',
            status='draft',
        )
        cap = Capability(slug='dup-cap', name='Dup Cap', base_price=100)
        db.session.add_all([project, cap])
        db.session.commit()

        ProjectService.add_capability(project.id, cap.id)
        with pytest.raises(ConflictError):
            ProjectService.add_capability(project.id, cap.id)


def test_add_automation(app):
    with app.app_context():
        client = _create_client(app, 'addauto')
        project = Project(
            client_id=client.id,
            name='Auto Test',
            system_type='growth',
            status='draft',
        )
        auto = Automation(
            slug='test-auto-addauto',
            name='Test Auto',
            trigger_type='form_submission',
            action_type='send_email',
            base_price=50,
        )
        db.session.add_all([project, auto])
        db.session.commit()

        pa = ProjectService.add_automation(project.id, auto.id)
        assert pa.project_id == project.id


def test_add_service(app):
    with app.app_context():
        client = _create_client(app, 'addsvc')
        project = Project(
            client_id=client.id,
            name='Svc Test',
            system_type='start',
            status='draft',
        )
        svc = Service(slug='test-svc-addsvc', name='Test Svc', base_price=200)
        db.session.add_all([project, svc])
        db.session.commit()

        ps = ProjectService.add_service(project.id, svc.id)
        assert ps.project_id == project.id
