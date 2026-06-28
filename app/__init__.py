from flask import Flask
from app.extensions import db, bcrypt, migrate, login_manager as flask_login_manager
from app.routes import(
    auth_bp,
    home_bp
)

import app.login_manager  # noqa: F401

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    # Initialize database
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    flask_login_manager.init_app(app)

    flask_login_manager.login_view = 'auth.login'

    # Register to App
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(home_bp, url_prefix='/home')

    return app