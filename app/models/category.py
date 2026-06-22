from app import db
from datetime import datetime

class InterviewCategory(db.Model):
    __tablename__ = 'interview_categories'

    id = db.Column(db.BigInteger, primary_key=True)
    category_name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'category_name': self.category_name,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
