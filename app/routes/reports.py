from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/', methods=['GET'])
@jwt_required()
def get_reports():
    return jsonify({'reports': []}), 200

@reports_bp.route('/<id>', methods=['GET'])
@jwt_required()
def get_report(id):
    return jsonify({'report': {'id': id, 'details': 'mock report'}}), 200

@reports_bp.route('/<id>/pdf', methods=['GET'])
@jwt_required()
def get_report_pdf(id):
    return jsonify({'message': 'PDF generated (mock)', 'url': f'/static/reports/{id}.pdf'}), 200
