import uuid
from datetime import datetime, timezone
from sqlalchemy import TypeDecorator, String
from core import db


class UUIDType(TypeDecorator):
    """UUID type that stores as string on SQLite and UUID on PostgreSQL."""
    impl = String(36)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            from sqlalchemy.dialects.postgresql import UUID
            return dialect.type_descriptor(UUID())
        return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(str(value))

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return str(value)
        return str(value)


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(UUIDType(), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {c.name: str(getattr(self, c.name)) if isinstance(getattr(self, c.name), uuid.UUID) else getattr(self, c.name) for c in self.__table__.columns}
