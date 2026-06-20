from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.plan import Plan
from app.models.subscription import Subscription

subscriptions_bp = Blueprint('subscriptions', __name__)

@subscriptions_bp.route('/plans', methods=['GET'])
def get_plans():
    plans = Plan.query.filter_by(is_active=True).all()
    return jsonify({'plans': [p.to_dict() for p in plans]}), 200

@subscriptions_bp.route('/current', methods=['GET'])
@jwt_required()
def current_subscription():
    current_user_id = get_jwt_identity()
    sub = Subscription.query.filter_by(user_id=current_user_id, status='active').first()
    if sub:
        return jsonify({'subscription': sub.to_dict()}), 200
    return jsonify({'message': 'No active subscription'}), 404

@subscriptions_bp.route('/upgrade', methods=['POST'])
@jwt_required()
def upgrade():
    # Placeholder logic
    return jsonify({'message': 'Upgrade initiated (mock)'}), 200
