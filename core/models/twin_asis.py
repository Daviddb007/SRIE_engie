from core import db
from core.models.base import BaseModel

class TwinASIS(BaseModel):
    __tablename__ = 'twin_asis'
    consultoria_id = db.Column(db.String(36), db.ForeignKey('consultorias.id'), unique=True, nullable=False)
    capas = db.Column(db.JSON, default=dict)
    problemas = db.Column(db.JSON, default=list)
