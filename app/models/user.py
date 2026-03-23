from app.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    performances = db.relationship('Performance', backref='user', lazy='dynamic')

    def __init__(self, username, email, is_admin=False):
        self.username = username
        self.email = email
        self.is_admin = is_admin
        self.date_joined = datetime.utcnow()
        self.last_seen = datetime.utcnow()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f'<User {self.username}>'

    def update_last_seen(self):
        self.last_seen = datetime.utcnow()
        db.session.commit()

    def get_performance_stats(self):
        performances = self.performances.all()
        if not performances:
            return {
                'total_songs': 0,
                'average_score': 0,
                'best_score': 0
            }
        
        scores = [p.score for p in performances if p.score is not None]
        return {
            'total_songs': len(performances),
            'average_score': sum(scores) / len(scores) if scores else 0,
            'best_score': max(scores) if scores else 0
        }
