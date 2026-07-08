import uuid
from datetime import datetime, timezone
from core import db


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        result = {}
        for c in self.__table__.columns:
            val = getattr(self, c.name)
            if isinstance(val, uuid.UUID):
                val = str(val)
            result[c.name] = val
        return result
