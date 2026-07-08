from datetime import datetime, timezone, timedelta
import secrets
from core import db
from core.models.base import BaseModel


class MagicLink(BaseModel):
    __tablename__ = 'magic_links'

    email = db.Column(db.String(255), nullable=False, index=True)
    consultoria_id = db.Column(db.String(36), db.ForeignKey('consultorias.id'), nullable=True)
    token = db.Column(db.String(128), nullable=False, unique=True, index=True)
    usado = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)

    consultoria = db.relationship('Consultoria', backref='magic_links')

    @staticmethod
    def create(consultoria_id: str, email: str) -> 'MagicLink':
        token = secrets.token_urlsafe(48)
        link = MagicLink(
            email=email,
            consultoria_id=consultoria_id,
            token=token,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
        )
        db.session.add(link)
        db.session.commit()
        return link

    def is_valid(self) -> bool:
        now = datetime.now(timezone.utc)
        if self.expires_at.tzinfo is None:
            from datetime import timedelta
            expires = self.expires_at.replace(tzinfo=timezone.utc)
        else:
            expires = self.expires_at
        return not self.usado and expires > now
