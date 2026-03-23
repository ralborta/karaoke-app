from flask import render_template
from app.extensions import db

def not_found_error(error):
    """Manejador para errores 404"""
    return render_template('errors/404.html'), 404

def internal_error(error):
    """Manejador para errores 500"""
    db.session.rollback()
    return render_template('errors/500.html'), 500
