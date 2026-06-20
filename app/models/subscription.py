from app import db
import uuid
from datetime import datetime

class Subscription(db.Model):
    __tablename__ = 'subscriptions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    plan_id = db.Column(db.String(36), db.ForeignKey('plans.id'), nullable=False)
    
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    
    credits_allocated = db.Column(db.Integer, nullable=False)
    credits_used = db.Column(db.Integer, default=0)
    
    status = db.Column(db.String(50), default='active') # e.g., active, expired, cancelled
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan_id': self.plan_id,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'credits_allocated': self.credits_allocated,
            'credits_used': self.credits_used,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
