import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from app.config import Config

db = SQLAlchemy()
jwt = JWTManager()
socketio = SocketIO(cors_allowed_origins="*", async_mode='gevent', ping_timeout=60, ping_interval=25)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.config['MAX_CONTENT_LENGTH'] = app.config['MAX_CV_SIZE_MB'] * 1024 * 1024  # MB to bytes

    # Initialize extensions
    CORS(app, supports_credentials=True) # supports_credentials is required for cookies
    db.init_app(app)
    jwt.init_app(app)
    socketio.init_app(app)

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.templates import templates_bp
    from app.routes.interview import interview_bp
    from app.routes.reports import reports_bp
    from app.routes.progress import progress_bp
    from app.routes.subscriptions import subscriptions_bp
    from app.routes.payments import payments_bp
    from app.routes.tts import tts_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(templates_bp, url_prefix='/interview') # /interview/categories, etc.
    app.register_blueprint(interview_bp, url_prefix='/interview') # /interview/start, etc.
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(progress_bp, url_prefix='/progress')
    app.register_blueprint(subscriptions_bp, url_prefix='/subscription')
    app.register_blueprint(payments_bp, url_prefix='/payments')
    app.register_blueprint(tts_bp, url_prefix='/tts')

    # Register Socket events
    from app.sockets import events

    return app
