from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.session import InterviewSession

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/', methods=['GET'])
@jwt_required()
def get_reports():
    current_user_id = get_jwt_identity()
    sessions = InterviewSession.query.filter_by(user_id=current_user_id).order_by(InterviewSession.created_at.desc()).all()
    return jsonify({'reports': [s.to_dict() for s in sessions]}), 200

@reports_bp.route('/<id>', methods=['GET'])
@jwt_required()
def get_report(id):
    current_user_id = get_jwt_identity()
    session = InterviewSession.query.filter_by(id=id, user_id=current_user_id).first()
    if not session:
        return jsonify({'message': 'Report not found'}), 404
    return jsonify({'report': session.to_dict()}), 200

@reports_bp.route('/<id>/pdf', methods=['GET'])
@jwt_required()
def get_report_pdf(id):
    return jsonify({'message': 'PDF generated (mock)', 'url': f'/static/reports/{id}.pdf'}), 200
