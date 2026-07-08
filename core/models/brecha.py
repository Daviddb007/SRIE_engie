from core import db
from core.models.base import BaseModel

class Brecha(BaseModel):
    __tablename__ = 'brechas'
    consultoria_id = db.Column(db.String(36), db.ForeignKey('consultorias.id'), nullable=False)
    capa = db.Column(db.String(50), nullable=False)
    problema_actual = db.Column(db.Text, nullable=False)
    estado_deseado = db.Column(db.Text, nullable=False)
    impacto = db.Column(db.String(10), default='media')
    prioridad = db.Column(db.String(10), default='media')
    solucion = db.Column(db.Text)
    sort_order = db.Column(db.Integer, default=0)
