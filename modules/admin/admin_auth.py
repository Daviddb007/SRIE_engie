"""Admin authentication routes."""
from __future__ import annotations

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps

from core.services.admin_auth_service import AdminAuthService

admin_auth_bp = Blueprint('admin_auth', __name__, template_folder='templates')


def redirect_authenticated(func):
    """Decorator to redirect if user is already authenticated."""
    @wraps(func)
    def decorated(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for('admin_dashboard.dashboard'))
        return func(*args, **kwargs)
    return decorated


@admin_auth_bp.route('/login', methods=['GET', 'POST'])
@redirect_authenticated
def login():
    """Handle login form display and submission."""
    return AdminAuthService.handle_login_form()


@admin_auth_bp.route('/logout')
@login_required
def logout():
    """Log out the current user."""
    from flask_login import logout_user
    logout_user()
    flash('Sesión cerrada exitosamente', 'success')
    return redirect(url_for('admin_auth.login'))
