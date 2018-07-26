from flask import Flask
from flask_cors import CORS
from flask_jwt import JWT
from flask_sqlalchemy import SQLAlchemy

# Flask extensions
cors = CORS()
db = SQLAlchemy()


def create_app(config):
    app = Flask(__name__)

    # Config app
    app.config.from_object(config)

    # Flask-Cors
    cors.init_app(app)

    # Initialize database connection
    db.init_app(app)

    # JWT
    from sso_service.app_setup import Auth
    JWT(app, Auth.authenticate, Auth.identity)

    # Register blueprints
    from sso_service.handlers.sso import sso_bp

    # Register blueprints
    app.register_blueprint(sso_bp)

    return app
