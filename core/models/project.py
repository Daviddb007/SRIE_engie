from core import db
from core.models.base import BaseModel


class Project(BaseModel):
    __tablename__ = 'projects'

    client_id = db.Column(db.String(36), db.ForeignKey('clients.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    system_type = db.Column(db.String(20), nullable=False, default='start')
    status = db.Column(db.String(20), nullable=False, default='draft')
    description = db.Column(db.Text)
    config = db.Column(db.JSON, default=dict)
    domain = db.Column(db.String(255))
    hosting_provider = db.Column(db.String(100))
    launch_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_by = db.Column(db.String(36), db.ForeignKey('admin_users.id'))

    capabilities = db.relationship('ProjectCapability', backref='project', lazy=True, cascade='all, delete-orphan')
    automations = db.relationship('ProjectAutomation', backref='project', lazy=True, cascade='all, delete-orphan')
    services = db.relationship('ProjectService', backref='project', lazy=True, cascade='all, delete-orphan')
    quotations = db.relationship('Quotation', backref='project', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Project {self.name}>'
