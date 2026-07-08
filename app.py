"""Application factory for Stonelytics."""
from __future__ import annotations

from flask import Flask, send_from_directory

from config import Config
from core import db, login_manager, mail, csrf, limiter
from core.errors import register_error_handlers


def create_app(config_class: type | None = None) -> Flask:
    """Create and configure the Flask application.
    
    Args:
        config_class: Configuration class. Defaults to Config from config.py
        
    Returns:
        Configured Flask application instance
    """
    config = config_class or Config
    app = Flask(__name__)
    app.config.from_object(config)

    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'admin_auth.login'

    # Register blueprints
    _register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    # Seed admin user on first run
    _seed_admin(app)

    # Static file routes
    _register_static_routes(app)

    # Cache headers for static assets
    @app.after_request
    def add_cache_headers(response):
        from flask import request
        if request.path.startswith('/static/'):
            response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
        return response

    return app


def _register_blueprints(app: Flask) -> None:
    """Register all application blueprints."""
    from modules.landing.routes import landing_bp
    from modules.contact.routes import contact_bp
    from modules.demos.start import demo_start_bp
    from modules.demos.growth import demo_growth_bp
    from modules.demos.intelligence import demo_intelligence_bp
    from modules.admin.admin_auth import admin_auth_bp
    from modules.admin.admin_dashboard import admin_dashboard_bp
    from modules.admin.admin_clients import admin_clients_bp
    from modules.admin.admin_projects import admin_projects_bp
    from modules.admin.admin_projects_management import admin_projects_management_bp
    from modules.admin.admin_quotations import admin_quotations_bp
    from modules.admin.admin_catalog import admin_catalog_bp
    from modules.cotizador.routes import cotizador_bp
    from modules.studio.routes import studio_bp
    from modules.portal.routes import portal_bp
    from modules.marketplace.routes import marketplace_bp
    from modules.teams.routes import teams_bp
    from modules.analytics.routes import analytics_bp

    app.register_blueprint(landing_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(demo_start_bp)
    app.register_blueprint(demo_growth_bp)
    app.register_blueprint(demo_intelligence_bp)
    app.register_blueprint(admin_auth_bp, url_prefix='/admin')
    app.register_blueprint(admin_dashboard_bp, url_prefix='/admin')
    app.register_blueprint(admin_clients_bp, url_prefix='/admin')
    app.register_blueprint(admin_projects_bp, url_prefix='/admin')
    app.register_blueprint(admin_projects_management_bp, url_prefix='/admin')
    app.register_blueprint(admin_quotations_bp, url_prefix='/admin')
    app.register_blueprint(admin_catalog_bp, url_prefix='/admin')
    app.register_blueprint(cotizador_bp, url_prefix='/cotizador')
    app.register_blueprint(studio_bp, url_prefix='/studio')
    app.register_blueprint(portal_bp, url_prefix='/portal')
    app.register_blueprint(marketplace_bp, url_prefix='/marketplace')
    app.register_blueprint(teams_bp, url_prefix='/teams')
    app.register_blueprint(analytics_bp, url_prefix='/analytics')


def _seed_admin(app: Flask) -> None:
    """Create default admin user if none exists."""
    from core.models.admin_user import AdminUser

    admin_email = app.config.get('ADMIN_EMAIL', 'daviddb@stonelytics.tech')
    with app.app_context():
        db.create_all()
        if not AdminUser.query.filter_by(email=admin_email).first():
            user = AdminUser(
                email=admin_email,
                full_name='David DB',
                role='super_admin',
            )
            user.set_password(app.config.get('ADMIN_PASSWORD', 'StonelyticsAdmin2026!'))
            db.session.add(user)
            db.session.commit()
            app.logger.info(f'Admin user created: {admin_email}')


def _register_static_routes(app: Flask) -> None:
    """Register static file serving routes."""

    @app.route('/robots.txt')
    def robots():
        return send_from_directory('static', 'robots.txt')

    @app.route('/sitemap.xml')
    def sitemap():
        return send_from_directory('static', 'sitemap.xml')


import os as _os

if _os.environ.get('FLASK_TESTING') != '1':
    app = create_app()

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=10000)
