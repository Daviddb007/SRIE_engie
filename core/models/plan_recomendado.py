from core import db
from core.models.base import BaseModel

class PlanRecomendado(BaseModel):
    __tablename__ = 'planes_recomendados'
    consultoria_id = db.Column(db.String(36), db.ForeignKey('consultorias.id'), unique=True, nullable=False)
    items = db.Column(db.JSON, default=list)
    total_estimado = db.Column(db.Numeric(12, 2), default=0)
    duracion_estimada = db.Column(db.String(50))
