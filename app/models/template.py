from app import db
import uuid
from datetime import datetime

class InterviewTemplate(db.Model):
    __tablename__ = 'interview_templates'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    category = db.Column(db.String(255))
    name = db.Column(db.String(255))
    company_name = db.Column(db.String(255), nullable=True)
    
    requires_cv = db.Column(db.Boolean, default=False)
    voice_gender = db.Column(db.String(50), default='neutral')
    difficulty_level = db.Column(db.String(50), default='medium')
    
    description = db.Column(db.Text)
    system_prompt = db.Column(db.Text)
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sessions = db.relationship('InterviewSession', backref='template', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'category': self.category,
            'name': self.name,
            'company_name': self.company_name,
            'requires_cv': self.requires_cv,
            'voice_gender': self.voice_gender,
            'difficulty_level': self.difficulty_level,
            'description': self.description,
            'system_prompt': self.system_prompt,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
