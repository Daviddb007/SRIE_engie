from core import db
from core.models.base import BaseModel


class Capability(BaseModel):
    __tablename__ = 'capabilities'

    slug = db.Column(db.String(100), nullable=False, unique=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    base_price = db.Column(db.Numeric(10, 2), default=0)
    is_active_ = db.Column('is_active', db.Boolean, nullable=False, default=True)
    config_schema = db.Column(db.JSON, default=dict)

    def __repr__(self):
        return f'<Capability {self.name}>'


class ProjectCapability(BaseModel):
    __tablename__ = 'project_capabilities'

    project_id = db.Column(db.String(36), db.ForeignKey('projects.id'), nullable=False)
    capability_id = db.Column(db.String(36), db.ForeignKey('capabilities.id'), nullable=False)
    config = db.Column(db.JSON, default=dict)
    price = db.Column(db.Numeric(10, 2))
    is_active_ = db.Column('is_active', db.Boolean, nullable=False, default=True)
    added_at = db.Column(db.DateTime(timezone=True))

    capability = db.relationship('Capability', backref='project_links')
