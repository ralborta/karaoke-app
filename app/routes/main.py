from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app.models.user import User
from app.models.song import Song, Performance
from app.extensions import db
import logging
from datetime import datetime
import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import random

main_bp = Blueprint('main', __name__)
logger = logging.getLogger(__name__)

@main_bp.route('/')
def index():
    """Ruta principal, redirige a la página de fiesta"""
    return redirect(url_for('main.party'))

@main_bp.route('/party')
def party():
    """Página principal de la fiesta de karaoke"""
    try:
        songs = Song.query.order_by(Song.id.desc()).all()
        return render_template('main/party.html', songs=songs)
    except Exception as e:
        logger.error(f"Error en party: {str(e)}")
        flash('Error al cargar la lista de canciones', 'danger')
        return render_template('main/party.html', songs=[])

@main_bp.route('/party/control')
@login_required
def party_control():
    """Panel de control para administradores"""
    if not current_user.is_admin:
        flash('No tienes permisos para acceder al panel de control', 'danger')
        return redirect(url_for('main.party'))
    
    try:
        songs = Song.query.order_by(Song.id.desc()).all()
        return render_template('main/control.html', songs=songs)
    except Exception as e:
        logger.error(f"Error en party_control: {str(e)}")
        flash('Error al cargar el panel de control', 'danger')
        return redirect(url_for('main.party'))

@main_bp.route('/karaoke/<int:song_id>')
@login_required
def karaoke(song_id):
    """Página de karaoke individual para una canción"""
    song = Song.query.get_or_404(song_id)
    return render_template('main/karaoke.html', song=song)

@main_bp.route('/search', methods=['POST'])
def search():
    """Búsqueda de canciones en YouTube"""
    query = request.form.get('query', '')
    if not query:
        return jsonify({'error': 'Query vacío'}), 400

    try:
        youtube = build('youtube', 'v3', 
                       developerKey=os.environ.get('YOUTUBE_API_KEY'))
        
        search_response = youtube.search().list(
            q=query + ' karaoke',
            part='snippet',
            maxResults=5,
            type='video'
        ).execute()

        results = []
        for item in search_response.get('items', []):
            results.append({
                'title': item['snippet']['title'],
                'videoId': item['id']['videoId'],
                'thumbnail': item['snippet']['thumbnails']['default']['url']
            })

        return jsonify({'results': results})
    except HttpError as e:
        logger.error(f"Error en búsqueda de YouTube: {str(e)}")
        return jsonify({'error': 'Error en la búsqueda de YouTube'}), 500
    except Exception as e:
        logger.error(f"Error en búsqueda: {str(e)}")
        return jsonify({'error': 'Error en la búsqueda'}), 500

@main_bp.route('/add_song', methods=['POST'])
@login_required
def add_song():
    """Agregar una canción a la lista"""
    try:
        title = request.form.get('title')
        artist = request.form.get('artist', 'Desconocido')
        youtube_id = request.form.get('youtube_id')
        
        if not all([title, youtube_id]):
            flash('Faltan datos de la canción', 'danger')
            return redirect(url_for('main.party'))

        song = Song(
            title=title,
            artist=artist,
            youtube_id=youtube_id,
            added_by=current_user.id,
            added_at=datetime.utcnow()
        )
        
        db.session.add(song)
        db.session.commit()
        
        flash('Canción agregada exitosamente', 'success')
        return redirect(url_for('main.party'))
        
    except Exception as e:
        logger.error(f"Error agregando canción: {str(e)}")
        db.session.rollback()
        flash('Error al agregar la canción', 'danger')
        return redirect(url_for('main.party'))

@main_bp.route('/remove_song/<int:song_id>', methods=['POST'])
@login_required
def remove_song(song_id):
    """Eliminar una canción de la lista"""
    if not current_user.is_admin:
        return jsonify({'error': 'No autorizado'}), 403
    
    try:
        song = Song.query.get_or_404(song_id)
        db.session.delete(song)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error eliminando canción: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@main_bp.route('/next_song', methods=['POST'])
@login_required
def next_song():
    """Pasar a la siguiente canción"""
    if not current_user.is_admin:
        return jsonify({'error': 'No autorizado'}), 403
    
    try:
        # Obtener la primera canción de la lista
        current_song = Song.query.order_by(Song.id).first()
        
        if current_song:
            # Eliminar la canción actual
            db.session.delete(current_song)
            db.session.commit()
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'No hay más canciones'}), 404
            
    except Exception as e:
        logger.error(f"Error pasando a siguiente canción: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@main_bp.route('/performance/analyze', methods=['POST'])
@login_required
def performance_analyze():
    """Mock que analiza el audio y devuelve scores aleatorios"""
    return jsonify({
        'score': random.randint(60, 100),
        'pitch_score': random.randint(60, 100),
        'rhythm_score': random.randint(60, 100),
        'energy_score': random.randint(60, 100),
        'feedback': random.choice(['¡Excelente!', 'Muy bien', 'Sigue practicando', '¡Eres una estrella!'])
    })

@main_bp.route('/performance/save', methods=['POST'])
@login_required
def performance_save():
    """Guardar el resultado de la canción completada usando JSON API"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Faltan datos'}), 400
            
        performance = Performance(
            user_id=current_user.id,
            song_id=data.get('song_id'),
            score=data.get('score', 0),
            pitch_score=data.get('pitch_score', 0),
            rhythm_score=data.get('rhythm_score', 0),
            energy_score=data.get('energy_score', 0),
            date=datetime.utcnow()
        )
        
        db.session.add(performance)
        db.session.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Error guardando performance: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@main_bp.route('/user_stats')
@login_required
def user_stats():
    """Obtener estadísticas del usuario"""
    try:
        stats = current_user.get_performance_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {str(e)}")
        return jsonify({'error': str(e)}), 500
