from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app.extensions import db
from datetime import datetime
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    logger.info("Accediendo a la ruta /login")
    
    if current_user.is_authenticated:
        logger.info(f"Usuario {current_user.username} ya está autenticado")
        return redirect(url_for('main.party'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        logger.info(f"Intento de login para usuario: {username}")
        
        try:
            user = User.query.filter_by(username=username).first()
            logger.info(f"Usuario encontrado: {user is not None}")
            
            if user and user.check_password(password):
                # Login exitoso
                login_user(user)
                logger.info(f"Login exitoso para usuario: {username}")
                
                # Actualizar último acceso
                user.last_seen = datetime.utcnow()
                db.session.commit()
                
                # Redirección después del login
                next_page = request.args.get('next')
                if next_page and next_page.startswith('/'):
                    logger.info(f"Redirigiendo a: {next_page}")
                    return redirect(next_page)
                
                logger.info("Redirigiendo a party")
                return redirect(url_for('main.party'))
            else:
                logger.warning(f"Login fallido para usuario: {username}")
                if not user:
                    logger.warning("Usuario no encontrado")
                else:
                    logger.warning("Contraseña incorrecta")
                flash('Usuario o contraseña incorrectos', 'danger')
                
        except Exception as e:
            logger.error(f"Error durante el login: {str(e)}")
            db.session.rollback()
            flash('Error en el servidor. Por favor, intenta más tarde.', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    username = current_user.username
    logout_user()
    logger.info(f"Usuario {username} ha cerrado sesión")
    flash('Has cerrado sesión exitosamente.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        try:
            # Actualizar email
            new_email = request.form.get('email')
            if new_email and new_email != current_user.email:
                if User.query.filter_by(email=new_email).first():
                    flash('Este email ya está en uso.', 'danger')
                    return redirect(url_for('auth.profile'))
                current_user.email = new_email
            
            # Actualizar contraseña
            new_password = request.form.get('new_password')
            if new_password:
                current_user.set_password(new_password)
            
            db.session.commit()
            flash('Perfil actualizado correctamente.', 'success')
            logger.info(f"Perfil actualizado para usuario: {current_user.username}")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error actualizando perfil: {str(e)}")
            flash('Error actualizando el perfil.', 'danger')
            
    return render_template('auth/profile.html')

@auth_bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        try:
            db.session.commit()
        except Exception as e:
            logger.error(f"Error actualizando last_seen: {str(e)}")
            db.session.rollback()
