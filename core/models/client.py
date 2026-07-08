from core import db
from core.models.base import BaseModel


class Client(BaseModel):
    __tablename__ = 'clients'

    company_name = db.Column(db.String(255), nullable=False)
    contact_name = db.Column(db.String(255), nullable=False)
    contact_email = db.Column(db.String(255), nullable=False, unique=True)
    contact_phone = db.Column(db.String(50))
    contact_whatsapp = db.Column(db.String(50))
    industry = db.Column(db.String(100))
    website = db.Column(db.String(500))
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    country = db.Column(db.String(100), default='Colombia')
    notes = db.Column(db.Text)
    metadata_ = db.Column('metadata', db.JSON, default=dict)

    projects = db.relationship('Project', backref='client', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Client {self.company_name}>'
