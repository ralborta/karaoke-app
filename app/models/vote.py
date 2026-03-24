from app.extensions import db
from datetime import datetime

class Vote(db.Model):
    __tablename__ = 'votes'
    
    id = db.Column(db.Integer, primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)
    voter_name = db.Column(db.String(100), nullable=True)
    score = db.Column(db.Integer, nullable=False) # 1 to 5
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    song = db.relationship('Song', backref=db.backref('votes', lazy=True, cascade="all, delete-orphan"))
