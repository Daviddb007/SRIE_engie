from datetime import datetime, timezone
from core import db
from core.models.base import BaseModel


class Quotation(BaseModel):
    __tablename__ = 'quotations'

    project_id = db.Column(db.String(36), db.ForeignKey('projects.id'), nullable=True)
    client_id = db.Column(db.String(36), db.ForeignKey('clients.id'), nullable=False)
    created_by = db.Column(db.String(36), db.ForeignKey('admin_users.id'))
    quotation_number = db.Column(db.String(50), nullable=False, unique=True)
    status = db.Column(db.String(20), nullable=False, default='draft')
    title = db.Column(db.String(255), nullable=False)
    scope = db.Column(db.Text)
    timeline_weeks = db.Column(db.Integer)
    total_price = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    currency = db.Column(db.String(3), default='USD')
    discount_pct = db.Column(db.Numeric(5, 2), default=0)
    final_price = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    conditions = db.Column(db.Text)
    valid_until = db.Column(db.Date)
    sent_at = db.Column(db.DateTime(timezone=True))
    viewed_at = db.Column(db.DateTime(timezone=True))
    accepted_at = db.Column(db.DateTime(timezone=True))
    rejected_at = db.Column(db.DateTime(timezone=True))
    rejection_reason = db.Column(db.Text)
    notes = db.Column(db.Text)
    metadata_ = db.Column('metadata', db.JSON, default=dict)

    client = db.relationship('Client', backref='quotations')
    items = db.relationship('QuotationItem', backref='quotation', lazy=True, cascade='all, delete-orphan')
    creator = db.relationship('AdminUser', backref='created_quotations')

    def __repr__(self):
        return f'<Quotation {self.quotation_number}>'

    @staticmethod
    def generate_number():
        from sqlalchemy import func
        now = datetime.now(timezone.utc)
        year = now.year
        prefix = f'QT-{year}-'
        last = db.session.query(Quotation.quotation_number)\
            .filter(Quotation.quotation_number.like(f'{prefix}%'))\
            .order_by(Quotation.quotation_number.desc())\
            .first()
        if last and last[0]:
            num = int(last[0].split('-')[-1]) + 1
            return f'{prefix}{num:04d}'
        return f'{prefix}0001'


class QuotationItem(BaseModel):
    __tablename__ = 'quotation_items'

    quotation_id = db.Column(db.String(36), db.ForeignKey('quotations.id'), nullable=False)
    item_type = db.Column(db.String(50), nullable=False)
    item_id = db.Column(db.String(36))
    description = db.Column(db.String(500), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    total_price = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    sort_order = db.Column(db.Integer, default=0)
