"""Custom exceptions and centralized error handlers."""
from __future__ import annotations

from flask import jsonify, render_template, Flask, request
from werkzeug.exceptions import HTTPException


class AppError(Exception):
    """Base application error."""

    status_code: int = 500
    message: str = 'Internal server error'

    def __init__(self, message: str | None = None, status_code: int | None = None):
        super().__init__()
        if message is not None:
            self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self) -> dict:
        return {'error': self.message}


class NotFoundError(AppError):
    status_code = 404
    message = 'Resource not found'


class ValidationError(AppError):
    status_code = 400
    message = 'Validation failed'


class AuthenticationError(AppError):
    status_code = 401
    message = 'Authentication required'


class ConflictError(AppError):
    status_code = 409
    message = 'Resource already exists'


def register_error_handlers(app: Flask) -> None:
    """Register centralized error handlers."""

    from flask_wtf.csrf import CSRFError

    @app.errorhandler(CSRFError)
    def handle_csrf_error(error: CSRFError):
        app.logger.warning(f'CSRF validation failed: {error.description}')
        if request.path.startswith('/api/') or request.content_type == 'application/json':
            return jsonify({'error': 'CSRF token missing or invalid'}), 400
        from flask import flash, redirect
        flash('Sesión expirada o token de seguridad inválido. Intenta de nuevo.', 'error')
        return redirect(request.full_path if request.method == 'GET' else request.path), 302

    @app.errorhandler(AppError)
    def handle_app_error(error: AppError):
        if request.path.startswith('/api/') or request.content_type == 'application/json':
            response = jsonify(error.to_dict())
            response.status_code = error.status_code
            return response
        return render_template('errors/500.html', error=error), error.status_code

    @app.errorhandler(404)
    def handle_404(error: HTTPException):
        if request.path.startswith('/api/') or request.content_type == 'application/json':
            return jsonify({'error': 'Not found'}), 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def handle_500(error: HTTPException):
        app.logger.error(f'Server error: {error}')
        if request.path.startswith('/api/') or request.content_type == 'application/json':
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('errors/500.html'), 500

    @app.errorhandler(Exception)
    def handle_exception(error: Exception):
        app.logger.exception('Unhandled exception')
        if request.path.startswith('/api/') or request.content_type == 'application/json':
            return jsonify({'error': 'An unexpected error occurred'}), 500
        return render_template('errors/500.html'), 500
