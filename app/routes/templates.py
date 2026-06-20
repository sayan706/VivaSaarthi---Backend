from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.models.template import InterviewTemplate

templates_bp = Blueprint('templates', __name__)

@templates_bp.route('/categories', methods=['GET'])
@jwt_required()
def categories():
    return jsonify({'categories': ['CSE', 'Government', 'MBA', 'Civil', 'Arts']}), 200

@templates_bp.route('/templates', methods=['GET'])
@jwt_required()
def get_templates():
    templates = InterviewTemplate.query.filter_by(is_active=True).all()
    return jsonify({'templates': [t.to_dict() for t in templates]}), 200

@templates_bp.route('/template/<id>', methods=['GET'])
@jwt_required()
def get_template(id):
    template = InterviewTemplate.query.get(id)
    if not template:
        return jsonify({'message': 'Template not found'}), 404
    return jsonify({'template': template.to_dict()}), 200
