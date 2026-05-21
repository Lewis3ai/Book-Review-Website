import os
from flask import Flask, redirect, url_for
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta
from .models import db


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-please-change-in-production')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-dev-secret-please-change-in-production')

    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'instance', 'app.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token'
    app.config['JWT_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=12)

    db.init_app(app)

    jwt = JWTManager(app)
    CORS(app, supports_credentials=True)

    from .models import User

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data['sub']
        return db.session.get(User, identity)

    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        return redirect(url_for('main.login'))

    @jwt.expired_token_loader
    def expired_token_callback(_jwt_header, _jwt_data):
        return redirect(url_for('main.login'))

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return redirect(url_for('main.login'))

    from .main import main_bp
    app.register_blueprint(main_bp)

    return app
