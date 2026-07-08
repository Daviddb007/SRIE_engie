from core import db
from core.models.base import BaseModel

class Consultoria(BaseModel):
    __tablename__ = 'consultorias'
    cliente_id = db.Column(db.String(36), db.ForeignKey('clients.id'), nullable=False)
    estado = db.Column(db.String(20), nullable=False, default='borrador')
    industria = db.Column(db.String(50), default='general')
    fecha_inicio = db.Column(db.DateTime(timezone=True))
    notas = db.Column(db.Text)

    cliente = db.relationship('Client', backref=db.backref('consultorias', lazy=True))


class ConsultoriaMensaje(BaseModel):
    __tablename__ = 'consultoria_mensajes'
    consultoria_id = db.Column(db.String(36), db.ForeignKey('consultorias.id'), nullable=False)
    rol = db.Column(db.String(10), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    capa = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime(timezone=True), default=db.func.now())

    consultoria = db.relationship('Consultoria', backref=db.backref('mensajes', lazy=True, cascade='all, delete-orphan'))
