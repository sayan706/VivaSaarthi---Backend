from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/overview', methods=['GET'])
@jwt_required()
def overview():
    # Mock data as requested
    return jsonify({
        "total_interviews": 24,
        "avg_score": 78,
        "best_score": 91,
        "current_streak": 6,
        "credits_remaining": 12
    }), 200

@dashboard_bp.route('/recent-interviews', methods=['GET'])
@jwt_required()
def recent_interviews():
    return jsonify({'recent_interviews': []}), 200

@dashboard_bp.route('/progress-chart', methods=['GET'])
@jwt_required()
def progress_chart():
    return jsonify({'progress_chart': []}), 200

@dashboard_bp.route('/recommendations', methods=['GET'])
@jwt_required()
def recommendations():
    return jsonify({'recommendations': []}), 200
