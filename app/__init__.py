from flask import Flask
from app.extensions import db, login_manager, migrate
from config import config
import os
import logging
from logging.handlers import RotatingFileHandler

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Cargar configuración
    app.config.from_object(config[config_name])
    
    # Asegurar que exista el directorio de logs si no estamos en Vercel
    if not os.environ.get('VERCEL'):
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        # Configurar log handler
        if not app.debug and not app.testing:
            file_handler = RotatingFileHandler('logs/karaoke.log', 
                                             maxBytes=10240, 
                                             backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
    else:
        import sys
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)
    
    app.logger.setLevel(logging.INFO)
    app.logger.info('Karaoke App startup')
    
    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Registrar blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    
    # Manejadores de error
    from app.errors import not_found_error, internal_error
    app.register_error_handler(404, not_found_error)
    app.register_error_handler(500, internal_error)
    
    # Inicializar Base de Datos en Memoria Temporal para Vercel
    if os.environ.get('VERCEL'):
        with app.app_context():
            from app.models.user import User
            from app.models.song import Song, Performance
            from app.models.setting import Setting
            from app.models.vote import Vote
            db.create_all()
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(username='admin', email='admin@example.com', is_admin=True)
                admin.set_password('admin')
                db.session.add(admin)
                db.session.commit()
                app.logger.info("Admin user created for Vercel instance")
                
    return app
