"""Service layer for Project operations."""
from __future__ import annotations

from core import db
from core.errors import NotFoundError, ConflictError
from core.models.project import Project
from core.models.capability import Capability, ProjectCapability
from core.models.automation import Automation, ProjectAutomation
from core.models.service import Service, ProjectService as ProjectServiceModel


class ProjectService:
    """Handles all project business logic."""

    @staticmethod
    def get_all() -> list[Project]:
        return Project.query.order_by(Project.created_at.desc()).all()

    @staticmethod
    def get_by_id(project_id: str) -> Project:
        project = Project.query.get(project_id)
        if not project:
            raise NotFoundError(f'Project {project_id} not found')
        return project

    @staticmethod
    def create(**kwargs) -> Project:
        project = Project(**kwargs)
        db.session.add(project)
        db.session.commit()
        return project

    @staticmethod
    def update(project_id: str, **kwargs) -> Project:
        project = Project.query.get(project_id)
        if not project:
            raise NotFoundError(f'Project {project_id} not found')
        for key, value in kwargs.items():
            if hasattr(project, key):
                setattr(project, key, value)
        db.session.commit()
        return project

    @staticmethod
    def add_capability(project_id: str, capability_id: str) -> ProjectCapability:
        exists = ProjectCapability.query.filter_by(
            project_id=project_id, capability_id=capability_id
        ).first()
        if exists:
            raise ConflictError('Capability already linked to this project')
        cap = Capability.query.get(capability_id)
        if not cap:
            raise NotFoundError(f'Capability {capability_id} not found')
        pc = ProjectCapability(project_id=project_id, capability_id=capability_id, price=cap.base_price)
        db.session.add(pc)
        db.session.commit()
        return pc

    @staticmethod
    def remove_capability(pc_id: str) -> None:
        pc = ProjectCapability.query.get(pc_id)
        if not pc:
            raise NotFoundError(f'Project capability {pc_id} not found')
        db.session.delete(pc)
        db.session.commit()

    @staticmethod
    def add_automation(project_id: str, automation_id: str) -> ProjectAutomation:
        exists = ProjectAutomation.query.filter_by(
            project_id=project_id, automation_id=automation_id
        ).first()
        if exists:
            raise ConflictError('Automation already linked to this project')
        auto = Automation.query.get(automation_id)
        if not auto:
            raise NotFoundError(f'Automation {automation_id} not found')
        pa = ProjectAutomation(project_id=project_id, automation_id=automation_id, price=auto.base_price)
        db.session.add(pa)
        db.session.commit()
        return pa

    @staticmethod
    def remove_automation(pa_id: str) -> None:
        pa = ProjectAutomation.query.get(pa_id)
        if not pa:
            raise NotFoundError(f'Project automation {pa_id} not found')
        db.session.delete(pa)
        db.session.commit()

    @staticmethod
    def add_service(project_id: str, service_id: str) -> ProjectServiceModel:
        exists = ProjectServiceModel.query.filter_by(
            project_id=project_id, service_id=service_id
        ).first()
        if exists:
            raise ConflictError('Service already linked to this project')
        svc = Service.query.get(service_id)
        if not svc:
            raise NotFoundError(f'Service {service_id} not found')
        ps = ProjectServiceModel(project_id=project_id, service_id=service_id, price=svc.base_price)
        db.session.add(ps)
        db.session.commit()
        return ps

    @staticmethod
    def remove_service(ps_id: str) -> None:
        ps = ProjectServiceModel.query.get(ps_id)
        if not ps:
            raise NotFoundError(f'Project service {ps_id} not found')
        db.session.delete(ps)
        db.session.commit()

    @staticmethod
    def get_catalog_items() -> dict:
        return {
            'capabilities': Capability.query.filter_by(is_active_=True).all(),
            'automations': Automation.query.filter_by(is_active_=True).all(),
            'services': Service.query.filter_by(is_active_=True).all(),
        }
