from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.song import Song, Performance
import os
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Crear la aplicación
app = create_app()

def create_database():
    """Crear la base de datos SQLite si no existe"""
    if not os.path.exists('instance'):
        # En Vercel no podemos crear carpetas, así que omitimos
        if not os.environ.get('VERCEL'):
            os.makedirs('instance') # Re-added os.makedirs based on original intent and corrected instruction's comment
            logger.info("Directorio instance creado")
    
    # The original logic for creating the .db file is removed, as db.create_all() handles it.
    # The new logic from the instruction seems to be a refactor of init_db into create_database.
    # Let's assume the instruction intended to move the db creation/dropping logic here.
    with app.app_context():
        # Import models (already imported globally, but keeping this for consistency with instruction's snippet)
        from app.models.user import User
        from app.models.song import Song, Performance
        from app.models.setting import Setting
        from app.models.vote import Vote # Ensure Setting is imported here too if needed locally
        
        try:
            # Borrar las tablas antiguas y aplicar el nuevo esquema
            db.drop_all()
            # Crear todas las tablas
            db.create_all()
            logger.info("Tablas de la base de datos creadas correctamente")
            
            # Verificar si existe el usuario admin
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                # Crear usuario admin
                admin = User(
                    username='admin',
                    email='admin@example.com',
                    is_admin=True
                )
                # Establecer contraseña de forma segura
                admin.set_password('admin')
                db.session.add(admin)
                db.session.commit()
                logger.info("Usuario admin creado exitosamente")
                logger.info("Username: admin")
                logger.info("Password: admin")
            else:
                # Si el admin ya existe, asegurar que tenga la contraseña correcta
                admin.set_password('admin')
                db.session.commit()
                logger.info("Contraseña de admin actualizada")
                
        except Exception as e:
            logger.error(f"Error en la inicialización de la base de datos: {str(e)}")
            db.session.rollback()
            raise

def verify_directories():
    """Verificar y crear los directorios necesarios"""
    directories = [
        'instance',
        'logs',
        'app/static/uploads',
        'app/templates/errors',
        'app/templates/auth',
        'app/templates/main'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Directorio creado: {directory}")

def verify_config():
    """Verificar la configuración necesaria"""
    required_env = ['YOUTUBE_API_KEY']
    missing_env = []
    
    for env in required_env:
        if not os.getenv(env):
            missing_env.append(env)
            logger.warning(f"Variable de entorno no encontrada: {env}")
    
    if missing_env:
        logger.warning("Algunas variables de entorno necesarias no están configuradas")

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Song': Song,
        'Performance': Performance
    }

if __name__ == '__main__':
    try:
        logger.info("=== Karaoke App ===")
        
        # Verificar directorios
        verify_directories()
        logger.info("Directorios verificados")
        
        # Verificar configuración
        verify_config()
        logger.info("Configuración verificada")
        
        # Crear base de datos si no existe
        create_database()
        logger.info("Base de datos verificada")
        
        # Inicializar la base de datos y crear admin
        init_db()
        logger.info("Base de datos inicializada")
        
        logger.info("Servidor iniciado en: http://192.168.1.87:5001")
        logger.info("Usuario admin creado:")
        logger.info("  Username: admin")
        logger.info("  Password: admin")
        
        # Ejecutar la aplicación
        app.run(
            host='0.0.0.0',
            port=5001,
            debug=True
        )
    except Exception as e:
        logger.error(f"Error al iniciar la aplicación: {str(e)}")
        logger.error("Deteniendo la aplicación...")
        exit(1)
