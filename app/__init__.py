import os
from flask import Flask


def create_app(config_class=None):
    app = Flask(__name__)

    if config_class is None:
        env = os.environ.get('FLASK_ENV', 'production')
        if env == 'development':
            from config import DevelopmentConfig
            config_class = DevelopmentConfig
        elif env == 'testing':
            from config import TestingConfig
            config_class = TestingConfig
        else:
            from config import ProductionConfig
            config_class = ProductionConfig

    app.config.from_object(config_class)

    if not app.config.get('SECRET_KEY'):
        raise RuntimeError('SECRET_KEY environment variable is required')
    if not app.config.get('FERNET_KEY'):
        raise RuntimeError('FERNET_KEY environment variable is required')

    # Initialize extensions
    from app.extensions import db, migrate, login_manager, csrf
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # User loader
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, user_id)

    # Register blueprints
    from app.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import main_bp
    app.register_blueprint(main_bp)

    from app.cloud import cloud_bp
    app.register_blueprint(cloud_bp, url_prefix='/cloud')

    from app.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from app.export import export_bp
    app.register_blueprint(export_bp, url_prefix='/export')

    _register_error_handlers(app)

    return app


def _register_error_handlers(app):
    from flask import render_template

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template('errors/500.html'), 500
