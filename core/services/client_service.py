"""Service layer for Client operations."""
from __future__ import annotations

from typing import Optional

from core import db
from core.errors import NotFoundError, ValidationError, ConflictError
from core.models.client import Client


class ClientService:
    """Handles all client business logic."""

    @staticmethod
    def get_all() -> list[Client]:
        return Client.query.order_by(Client.created_at.desc()).all()

    @staticmethod
    def get_by_id(client_id: str) -> Client:
        client = Client.query.get(client_id)
        if not client:
            raise NotFoundError(f'Client {client_id} not found')
        return client

    @staticmethod
    def create(**kwargs) -> Client:
        if Client.query.filter_by(contact_email=kwargs.get('contact_email')).first():
            raise ConflictError('A client with this email already exists')
        client = Client(**kwargs)
        db.session.add(client)
        db.session.commit()
        return client

    @staticmethod
    def update(client_id: str, **kwargs) -> Client:
        client = Client.query.get(client_id)
        if not client:
            raise NotFoundError(f'Client {client_id} not found')
        for key, value in kwargs.items():
            if hasattr(client, key):
                setattr(client, key, value)
        db.session.commit()
        return client

    @staticmethod
    def delete(client_id: str) -> None:
        client = Client.query.get(client_id)
        if not client:
            raise NotFoundError(f'Client {client_id} not found')
        db.session.delete(client)
        db.session.commit()
