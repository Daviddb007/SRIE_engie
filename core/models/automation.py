from core import db
from core.models.base import BaseModel


class Automation(BaseModel):
    __tablename__ = 'automations'

    slug = db.Column(db.String(100), nullable=False, unique=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    trigger_type = db.Column(db.String(100), nullable=False)
    action_type = db.Column(db.String(100), nullable=False)
    base_price = db.Column(db.Numeric(10, 2), default=0)
    is_active_ = db.Column('is_active', db.Boolean, nullable=False, default=True)
    config_schema = db.Column(db.JSON, default=dict)

    def __repr__(self):
        return f'<Automation {self.name}>'


class ProjectAutomation(BaseModel):
    __tablename__ = 'project_automations'

    project_id = db.Column(db.String(36), db.ForeignKey('projects.id'), nullable=False)
    automation_id = db.Column(db.String(36), db.ForeignKey('automations.id'), nullable=False)
    config = db.Column(db.JSON, default=dict)
    price = db.Column(db.Numeric(10, 2))
    is_active_ = db.Column('is_active', db.Boolean, nullable=False, default=True)
    added_at = db.Column(db.DateTime(timezone=True))

    automation = db.relationship('Automation', backref='project_links')
