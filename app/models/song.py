from app import db
from datetime import datetime

class Song(db.Model):
    __tablename__ = 'songs'
    
    id = db.Column(db.Integer, primary_key=True)
    youtube_id = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    artist = db.Column(db.String(100), nullable=False, default='Desconocido')
    added_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    adder = db.relationship('User', foreign_keys=[added_by], backref='added_songs', lazy=True)
    performances = db.relationship('Performance', backref='song', lazy=True)
    playlist_entries = db.relationship('PartyPlaylist', backref='song', lazy=True)
    
    def __repr__(self):
        return f'<Song {self.title}>'

class Performance(db.Model):
    __tablename__ = 'performances'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)
    score = db.Column(db.Float)
    pitch_score = db.Column(db.Float, default=0.0)
    rhythm_score = db.Column(db.Float, default=0.0)
    energy_score = db.Column(db.Float, default=0.0)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Performance {self.user_id} - {self.song_id}>'

class PartyPlaylist(db.Model):
    __tablename__ = 'party_playlist'
    
    id = db.Column(db.Integer, primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    position = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, playing, completed
    
    def __repr__(self):
        return f'<PartyPlaylist {self.song_id} - Position {self.position}>'
