"""Service layer for Catalog (Capability, Automation, Service) operations."""
from __future__ import annotations

from core import db
from core.errors import NotFoundError, ConflictError
from core.models.capability import Capability
from core.models.automation import Automation
from core.models.service import Service


class CatalogService:
    """Handles catalog CRUD for capabilities, automations, services."""

    @staticmethod
    def get_all() -> dict:
        return {
            'capabilities': Capability.query.all(),
            'automations': Automation.query.all(),
            'services': Service.query.all(),
        }

    @staticmethod
    def create_capability(**kwargs) -> Capability:
        if Capability.query.filter_by(slug=kwargs.get('slug')).first():
            raise ConflictError(f'Capability with slug "{kwargs["slug"]}" already exists')
        cap = Capability(**kwargs)
        db.session.add(cap)
        db.session.commit()
        return cap

    @staticmethod
    def update_capability(item_id: str, **kwargs) -> Capability:
        cap = Capability.query.get(item_id)
        if not cap:
            raise NotFoundError(f'Capability {item_id} not found')
        for key, value in kwargs.items():
            if hasattr(cap, key):
                setattr(cap, key, value)
        db.session.commit()
        return cap

    @staticmethod
    def create_automation(**kwargs) -> Automation:
        if Automation.query.filter_by(slug=kwargs.get('slug')).first():
            raise ConflictError(f'Automation with slug "{kwargs["slug"]}" already exists')
        auto = Automation(**kwargs)
        db.session.add(auto)
        db.session.commit()
        return auto

    @staticmethod
    def update_automation(item_id: str, **kwargs) -> Automation:
        auto = Automation.query.get(item_id)
        if not auto:
            raise NotFoundError(f'Automation {item_id} not found')
        for key, value in kwargs.items():
            if hasattr(auto, key):
                setattr(auto, key, value)
        db.session.commit()
        return auto

    @staticmethod
    def create_service(**kwargs) -> Service:
        if Service.query.filter_by(slug=kwargs.get('slug')).first():
            raise ConflictError(f'Service with slug "{kwargs["slug"]}" already exists')
        svc = Service(**kwargs)
        db.session.add(svc)
        db.session.commit()
        return svc

    @staticmethod
    def update_service(item_id: str, **kwargs) -> Service:
        svc = Service.query.get(item_id)
        if not svc:
            raise NotFoundError(f'Service {item_id} not found')
        for key, value in kwargs.items():
            if hasattr(svc, key):
                setattr(svc, key, value)
        db.session.commit()
        return svc
