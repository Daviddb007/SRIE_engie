from core import db
from core.models.base import BaseModel

class TwinTOBE(BaseModel):
    __tablename__ = 'twin_tobe'
    consultoria_id = db.Column(db.String(36), db.ForeignKey('consultorias.id'), unique=True, nullable=False)
    capas = db.Column(db.JSON, default=dict)
    objetivos = db.Column(db.JSON, default=list)
