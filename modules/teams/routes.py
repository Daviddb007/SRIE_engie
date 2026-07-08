"""Team management routes — create teams, invite members, share consultorias."""
from __future__ import annotations

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user

from core import db
from core.models.team import Team, TeamMember, ConsultoriaShare
from core.models.consultoria import Consultoria

teams_bp = Blueprint('teams', __name__, template_folder='templates')


@teams_bp.route('/')
@login_required
def index():
    owned = Team.query.filter_by(created_by=current_user.id).all()
    member_of = TeamMember.query.filter_by(user_id=current_user.id).all()
    member_teams = [m.team for m in member_of]
    return render_template('teams/index.html', owned=owned, member_teams=member_teams, active_page='teams')


@teams_bp.route('/crear', methods=['POST'])
@login_required
def crear():
    name = request.form.get('name', '').strip()
    desc = request.form.get('description', '').strip()
    if not name:
        flash('El nombre del equipo es requerido', 'error')
        return redirect(url_for('teams.index'))

    team = Team(name=name, description=desc, created_by=current_user.id)
    db.session.add(team)
    db.session.flush()

    member = TeamMember(team_id=team.id, user_id=current_user.id, role='admin')
    db.session.add(member)
    db.session.commit()

    flash(f'Equipo "{name}" creado', 'success')
    return redirect(url_for('teams.index'))


@teams_bp.route('/<team_id>/invitar', methods=['POST'])
@login_required
def invitar(team_id: str):
    team = Team.query.get_or_404(team_id)
    if team.created_by != current_user.id:
        flash('Solo el creador del equipo puede invitar', 'error')
        return redirect(url_for('teams.index'))

    from core.models.admin_user import AdminUser
    email = request.form.get('email', '').strip().lower()
    role = request.form.get('role', 'viewer')
    user = AdminUser.query.filter_by(email=email).first()

    if not user:
        flash(f'No existe un usuario con email {email}', 'error')
        return redirect(url_for('teams.index'))

    existing = TeamMember.query.filter_by(team_id=team_id, user_id=user.id).first()
    if existing:
        flash(f'{email} ya es miembro del equipo', 'warning')
        return redirect(url_for('teams.index'))

    member = TeamMember(team_id=team_id, user_id=user.id, role=role)
    db.session.add(member)
    db.session.commit()
    flash(f'{email} agregado como {role}', 'success')
    return redirect(url_for('teams.index'))


@teams_bp.route('/<team_id>/compartir', methods=['POST'])
@login_required
def compartir(team_id: str):
    team = Team.query.get_or_404(team_id)
    if team.created_by != current_user.id:
        flash('Solo el creador puede compartir consultorias', 'error')
        return redirect(url_for('teams.index'))

    consultoria_id = request.form.get('consultoria_id', '')
    permission = request.form.get('permission', 'view')
    consultoria = Consultoria.query.get(consultoria_id)

    if not consultoria:
        flash('Consultoria no encontrada', 'error')
        return redirect(url_for('teams.index'))

    existing = ConsultoriaShare.query.filter_by(consultoria_id=consultoria_id, team_id=team_id).first()
    if existing:
        flash('Ya compartida con este equipo', 'warning')
        return redirect(url_for('teams.index'))

    share = ConsultoriaShare(consultoria_id=consultoria_id, team_id=team_id, permission=permission)
    db.session.add(share)
    db.session.commit()
    flash(f'Consultoria compartida con {team.name}', 'success')
    return redirect(url_for('teams.index'))


@teams_bp.route('/api/consultorias-disponibles')
@login_required
def consultorias_disponibles():
    consultorias = Consultoria.query.order_by(Consultoria.created_at.desc()).all()
    return jsonify([{
        'id': c.id,
        'nombre': c.cliente.company_name if c.cliente else 'Sin cliente',
        'estado': c.estado,
    } for c in consultorias])
