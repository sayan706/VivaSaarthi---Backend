from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

progress_bp = Blueprint('progress', __name__)

@progress_bp.route('/monthly', methods=['GET'])
@jwt_required()
def monthly():
    return jsonify({'monthly_progress': []}), 200

@progress_bp.route('/skills', methods=['GET'])
@jwt_required()
def skills():
    return jsonify({'skills_progress': []}), 200

@progress_bp.route('/trends', methods=['GET'])
@jwt_required()
def trends():
    return jsonify({'trends': []}), 200
