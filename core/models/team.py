"""Team and collaboration models for multi-tenant support."""
from core import db
from core.models.base import BaseModel


class Team(BaseModel):
    __tablename__ = 'teams'

    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    created_by = db.Column(db.String(36), db.ForeignKey('admin_users.id'))

    creator = db.relationship('AdminUser', backref='owned_teams')
    members = db.relationship('TeamMember', backref='team', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Team {self.name}>'


class TeamMember(BaseModel):
    __tablename__ = 'team_members'

    team_id = db.Column(db.String(36), db.ForeignKey('teams.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('admin_users.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='viewer')

    user = db.relationship('AdminUser', backref='team_memberships')


class ConsultoriaShare(BaseModel):
    __tablename__ = 'consultoria_shares'

    consultoria_id = db.Column(db.String(36), db.ForeignKey('consultorias.id'), nullable=False)
    team_id = db.Column(db.String(36), db.ForeignKey('teams.id'), nullable=False)
    permission = db.Column(db.String(20), nullable=False, default='view')

    consultoria = db.relationship('Consultoria', backref='shares')
    team = db.relationship('Team', backref='shared_consultorias')
