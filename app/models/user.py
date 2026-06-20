from app import db
import uuid
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False) # Added for JWT auth
    profile_image = db.Column(db.String(512), nullable=True)
    credits_remaining = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    subscriptions = db.relationship('Subscription', backref='user', lazy=True)
    sessions = db.relationship('InterviewSession', backref='user', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'profile_image': self.profile_image,
            'credits_remaining': self.credits_remaining,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
