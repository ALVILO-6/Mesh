from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    # Initialize database
    db.init_app(app)

    # Register routes
    from app.routes.auth import auth_bp

    # Register to App
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app