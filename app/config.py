import os
import urllib.parse
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key')
    
    # Database
    db_user = os.environ.get('DB_USER', 'postgres')
    db_password = os.environ.get('DB_PASSWORD', 'postgres')
    encoded_password = urllib.parse.quote_plus(db_password)
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_port = os.environ.get('DB_PORT', '5432')
    db_name = os.environ.get('DB_NAME', 'vivasaarthi')
    SQLALCHEMY_DATABASE_URI = f'postgresql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'default-jwt-secret-key')
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_COOKIE_SECURE = False  # Set to True in production (HTTPS)
    JWT_COOKIE_CSRF_PROTECT = False  # Set to True for added security against CSRF
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # CV Upload Settings
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'uploads')
    MAX_CV_SIZE_MB = 5
    ALLOWED_CV_EXTENSIONS = {'.pdf', '.docx'}

    # Third Party APIs
    SMALLEST_API_KEY = os.environ.get('SMALLEST_API_KEY')
