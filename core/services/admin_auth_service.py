from __future__ import annotations

from datetime import datetime, timezone

from flask import request, redirect, url_for, flash, request as current_request
from flask_login import login_user
from werkzeug.security import check_password_hash

from core import db
from core.errors import ConflictError, ValidationError
from core.models.admin_user import AdminUser


class AdminAuthService:
    """Handles authentication logic for admin users."""

    @staticmethod
    def handle_login_form():
        """Handle login form display and submission.
        
        Returns:
            None if POST successful and redirect needed
            else rendered template
        """
        from flask import render_template
        from flask_login import current_user

        if current_user.is_authenticated:
            return redirect(url_for('admin_dashboard.dashboard'))

        if request.method == 'POST':
            return AdminAuthService._process_login()

        return render_template('admin/login.html')

    @staticmethod
    def _process_login():
        """Process login form submission.
        
        Returns:
            Redirect response on successful login
            None on failure (caller handles template render)
        """
        email = current_request.form.get('email', '').strip()
        password = current_request.form.get('password', '')

        user = AdminUser.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash('Email o contraseña incorrectos', 'error')
            return None

        if not user.is_active:
            flash('Cuenta desactivada. Contacte al administrador.', 'error')
            return None

        AdminAuthService._authenticate_user(user)
        return redirect(url_for('admin_dashboard.dashboard'))

    @staticmethod
    def _authenticate_user(user: AdminUser) -> None:
        """Authenticate user and update last login timestamp.
        
        Args:
            user: The admin user to authenticate
        """
        login_user(user)
        user.last_login_at = datetime.now(timezone.utc)
        db.session.commit()
        flash('Inicio de sesión exitoso', 'success')

    @staticmethod
    def validate_email(email: str) -> tuple[bool, str | None]:
        """Validate email format and existence.
        
        Args:
            email: Email address to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not email or '@' not in email:
            return False, 'El correo electrónico es requerido'

        email = email.strip()
        if not AdminUser.query.filter_by(email=email).first():
            return False, 'Correo electrónico no encontrado'

        return True, None

    @staticmethod
    def validate_password(password: str) -> tuple[bool, str | None]:
        """Validate password.
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not password:
            return False, 'La contraseña es requerida'

        return True, None

    @staticmethod
    def get_active_admins() -> list[AdminUser]:
        """Get all active admin users.
        
        Returns:
            List of active admin users
        """
        return AdminUser.query.filter_by(is_active=True).all()

    @staticmethod
    def can_access_admin(email: str) -> bool:
        """Check if user can access admin area.
        
        Args:
            email: User's email
            
        Returns:
            True if user can access admin
        """
        user = AdminUser.query.filter_by(email=email).first()
        return user is not None and user.is_active