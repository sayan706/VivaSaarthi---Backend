from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.plan import Plan
from app.models.subscription import Subscription
from datetime import datetime, timedelta

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
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
        
    # Add 50 credits for testing purposes
    user.credits_remaining = (user.credits_remaining or 0) + 50
    
    # Manage 30 days subscription expiry
    sub = Subscription.query.filter_by(user_id=current_user_id, status='active').first()
    
    if sub:
        # If they already have an active subscription, extend it by 30 days
        if sub.end_date and sub.end_date > datetime.utcnow():
            sub.end_date = sub.end_date + timedelta(days=30)
        else:
            sub.end_date = datetime.utcnow() + timedelta(days=30)
    else:
        # Reactivate an old one or create a new one
        sub = Subscription.query.filter_by(user_id=current_user_id).first()
        if sub:
            sub.status = 'active'
            sub.start_date = datetime.utcnow()
            sub.end_date = datetime.utcnow() + timedelta(days=30)
        else:
            # Find a default plan
            plan = Plan.query.first()
            sub = Subscription(
                user_id=current_user_id,
                plan_id=plan.id if plan else None,
                status='active',
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=30),
                auto_renew=False
            )
            db.session.add(sub)
            
    db.session.commit()
    
    return jsonify({
        'message': 'Plan renewed successfully! 30 days & 50 credits added.',
        'credits_remaining': user.credits_remaining,
        'subscription': sub.to_dict()
    }), 200
