import os
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()

class Config:
    # Configuración básica
    SECRET_KEY = os.environ.get('SECRET_KEY') or '7MEYd7EyHLB-9OjdojhrM0IlwFoP'
    
    # Configuración de la base de datos
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'karaoke.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de la sesión
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)
    
    # Configuración de YouTube API
    YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
    
    # Configuración de logging
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    
    # Configuración de la aplicación
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max-limit
    
    # Configuración del modo fiesta
    PARTY_MODE_ENABLED = True
    STREAM_URL = ''
    
    # Configuración de seguridad
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    
    # Configuración de desarrollo
    DEBUG = True
    TESTING = False
    
    # Configuración de host y puerto
    HOST = '0.0.0.0'
    PORT = 5001

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
