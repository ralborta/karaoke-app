from app import create_app
from app.extensions import db
from app.models.user import User

def reset_admin_password():
    app = create_app()
    with app.app_context():
        try:
            # Buscar usuario admin
            admin = User.query.filter_by(username='admin').first()
            
            if not admin:
                print("Usuario 'admin' no encontrado. Creándolo...")
                admin = User(
                    username='admin',
                    email='admin@example.com',
                    is_admin=True
                )
                db.session.add(admin)
            else:
                print("Usuario 'admin' encontrado.")
            
            # Establecer contraseña
            new_password = 'admin'  # O la que prefieras
            admin.set_password(new_password)
            db.session.commit()
            
            print(f"Contraseña de 'admin' establecida exitosamente a: {new_password}")
            
            # Verificar
            if admin.check_password(new_password):
                print("Verificación de contraseña: OK")
            else:
                print("Verificación de contraseña: FALLÓ")
                
        except Exception as e:
            print(f"Error: {e}")
            db.session.rollback()

if __name__ == '__main__':
    reset_admin_password()
