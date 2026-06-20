from app import db
import uuid
from datetime import datetime

class InterviewSession(db.Model):
    __tablename__ = 'interview_sessions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    template_id = db.Column(db.String(36), db.ForeignKey('interview_templates.id'), nullable=False)

    started_at = db.Column(db.DateTime, nullable=True)
    ended_at = db.Column(db.DateTime, nullable=True)
    duration_minutes = db.Column(db.Integer, nullable=True)

    overall_score = db.Column(db.Numeric(5, 2), nullable=True)
    
    communication_score = db.Column(db.Numeric(5, 2), nullable=True)
    technical_score = db.Column(db.Numeric(5, 2), nullable=True)
    confidence_score = db.Column(db.Numeric(5, 2), nullable=True)
    problem_solving_score = db.Column(db.Numeric(5, 2), nullable=True)
    security_score = db.Column(db.Numeric(5, 2), nullable=True)

    behavioral_analysis = db.Column(db.Text, nullable=True)
    performance_summary = db.Column(db.Text, nullable=True)
    strengths = db.Column(db.Text, nullable=True)
    weaknesses = db.Column(db.Text, nullable=True)
    preparation_plan = db.Column(db.Text, nullable=True)
    final_remarks = db.Column(db.Text, nullable=True)
    
    verdict = db.Column(db.String(100), nullable=True)

    frames_analyzed = db.Column(db.Integer, default=0)
    tab_switch_count = db.Column(db.Integer, default=0)
    fullscreen_exit_count = db.Column(db.Integer, default=0)
    face_missing_count = db.Column(db.Integer, default=0)

    interview_status = db.Column(db.String(50), default='pending') # pending, in_progress, completed, abandoned
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'template_id': self.template_id,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'duration_minutes': self.duration_minutes,
            'overall_score': str(self.overall_score) if self.overall_score else None,
            'communication_score': str(self.communication_score) if self.communication_score else None,
            'technical_score': str(self.technical_score) if self.technical_score else None,
            'confidence_score': str(self.confidence_score) if self.confidence_score else None,
            'problem_solving_score': str(self.problem_solving_score) if self.problem_solving_score else None,
            'security_score': str(self.security_score) if self.security_score else None,
            'behavioral_analysis': self.behavioral_analysis,
            'performance_summary': self.performance_summary,
            'strengths': self.strengths,
            'weaknesses': self.weaknesses,
            'preparation_plan': self.preparation_plan,
            'final_remarks': self.final_remarks,
            'verdict': self.verdict,
            'frames_analyzed': self.frames_analyzed,
            'tab_switch_count': self.tab_switch_count,
            'fullscreen_exit_count': self.fullscreen_exit_count,
            'face_missing_count': self.face_missing_count,
            'interview_status': self.interview_status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
