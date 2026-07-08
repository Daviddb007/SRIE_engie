from core import db
from core.models.base import BaseModel


class Service(BaseModel):
    __tablename__ = 'services'

    slug = db.Column(db.String(100), nullable=False, unique=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    base_price = db.Column(db.Numeric(10, 2), default=0)
    is_recurring = db.Column(db.Boolean, nullable=False, default=False)
    billing_interval = db.Column(db.String(50))
    is_active_ = db.Column('is_active', db.Boolean, nullable=False, default=True)

    def __repr__(self):
        return f'<Service {self.name}>'


class ProjectService(BaseModel):
    __tablename__ = 'project_services'

    project_id = db.Column(db.String(36), db.ForeignKey('projects.id'), nullable=False)
    service_id = db.Column(db.String(36), db.ForeignKey('services.id'), nullable=False)
    config = db.Column(db.JSON, default=dict)
    price = db.Column(db.Numeric(10, 2))
    is_active_ = db.Column('is_active', db.Boolean, nullable=False, default=True)
    added_at = db.Column(db.DateTime(timezone=True))

    service = db.relationship('Service', backref='project_links')
