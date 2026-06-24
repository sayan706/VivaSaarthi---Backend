from app import db
from datetime import datetime

class InterviewMessage(db.Model):
    __tablename__ = 'interview_messages'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    session_id = db.Column(db.String(36), db.ForeignKey('interview_sessions.id', ondelete='CASCADE'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_human = db.Column(db.Boolean, nullable=False)
    
    credits_used = db.Column(db.Numeric(10, 6), default=0)
    prompt_tokens = db.Column(db.Integer, default=0)
    completion_tokens = db.Column(db.Integer, default=0)
    total_tokens = db.Column(db.Integer, default=0)
    model_name = db.Column(db.String(100), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'message': self.message,
            'is_human': self.is_human,
            'credits_used': str(self.credits_used) if self.credits_used else 0,
            'prompt_tokens': self.prompt_tokens,
            'completion_tokens': self.completion_tokens,
            'total_tokens': self.total_tokens,
            'model_name': self.model_name,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
