from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.session import InterviewSession

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/overview', methods=['GET'])
@jwt_required()
def overview():
    current_user_id = get_jwt_identity()
    sessions = InterviewSession.query.filter_by(user_id=current_user_id).all()
    
    total_interviews = len(sessions)
    if total_interviews > 0:
        valid_overall = [float(s.overall_score) for s in sessions if s.overall_score]
        avg_score = sum(valid_overall) / len(valid_overall) if valid_overall else 0
        best_score = max(valid_overall) if valid_overall else 0
        
        valid_comm = [float(s.communication_score) for s in sessions if s.communication_score]
        avg_comm = sum(valid_comm) / len(valid_comm) if valid_comm else 0
        
        valid_conf = [float(s.confidence_score) for s in sessions if s.confidence_score]
        avg_conf = sum(valid_conf) / len(valid_conf) if valid_conf else 0
    else:
        avg_score = 0
        best_score = 0
        avg_comm = 0
        avg_conf = 0
        
    return jsonify({
        "total_interviews": total_interviews,
        "avg_score": round(avg_score, 1),
        "best_score": round(best_score, 1),
        "communication": round(avg_comm, 1),
        "confidence": round(avg_conf, 1),
        "current_streak": 0, # Mock for now
        "credits_remaining": 0 # Handled in user object if needed
    }), 200

@dashboard_bp.route('/recent-interviews', methods=['GET'])
@jwt_required()
def recent_interviews():
    current_user_id = get_jwt_identity()
    sessions = InterviewSession.query.filter_by(user_id=current_user_id).order_by(InterviewSession.created_at.desc()).limit(5).all()
    return jsonify({'recent_interviews': [s.to_dict() for s in sessions]}), 200

@dashboard_bp.route('/progress-chart', methods=['GET'])
@jwt_required()
def progress_chart():
    return jsonify({'progress_chart': []}), 200

@dashboard_bp.route('/recommendations', methods=['GET'])
@jwt_required()
def recommendations():
    return jsonify({'recommendations': []}), 200
