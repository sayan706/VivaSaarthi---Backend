import os
from flask import Blueprint, request, jsonify, make_response, current_app, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, set_access_cookies, unset_jwt_cookies
from app import db
from app.models.user import User
from app.models.plan import Plan
from app.models.subscription import Subscription
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password') or not data.get('name'):
        return jsonify({'message': 'Missing required fields'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'User already exists'}), 400

    new_user = User(
        name=data['name'],
        email=data['email'],
        password_hash=generate_password_hash(data['password'])
    )
    db.session.add(new_user)
    db.session.flush() # Get new_user.id
    
    # Get Free Plan with id '1'
    free_plan = Plan.query.get('1')
    if free_plan:
        # Create Subscription for the user
        new_subscription = Subscription(
            user_id=new_user.id,
            plan_id=free_plan.id,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=free_plan.duration_days),
            credits_allocated=free_plan.credits,
            credits_used=0,
            status='active'
        )
        db.session.add(new_subscription)
        
        # Assign credits to user
        new_user.credits_remaining = free_plan.credits

    db.session.commit()

    return jsonify({'message': 'User created successfully with Free plan', 'user': new_user.to_dict()}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing email or password'}), 400

    user = User.query.filter_by(email=data['email']).first()
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=user.id)
    resp = jsonify({'message': 'Login successful', 'user': user.to_dict()})
    set_access_cookies(resp, access_token)
    return resp, 200

@auth_bp.route('/logout', methods=['POST'])
def logout():
    resp = jsonify({'message': 'Logout successful'})
    unset_jwt_cookies(resp)
    return resp, 200

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    # Mock implementation for password reset
    data = request.get_json()
    if not data or not data.get('email'):
        return jsonify({'message': 'Email required'}), 400
    return jsonify({'message': 'Password reset link sent (mock)'}), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    return jsonify({'user': user.to_dict()}), 200

@auth_bp.route('/profile-image', methods=['POST'])
@jwt_required()
def upload_profile_image():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    if file:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404

        ext = os.path.splitext(secure_filename(file.filename))[1]
        if ext.lower() not in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
            return jsonify({'message': 'Invalid file type'}), 400

        filename = f"profile_{user.id}{ext}"
        profiles_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'profiles')
        os.makedirs(profiles_dir, exist_ok=True)
        file_path = os.path.join(profiles_dir, filename)
        file.save(file_path)

        user.profile_image = f"/api/auth/uploads/profiles/{filename}"
        db.session.commit()

        return jsonify({'message': 'Profile image updated', 'user': user.to_dict()}), 200

@auth_bp.route('/uploads/profiles/<filename>', methods=['GET'])
def get_profile_image(filename):
    profiles_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'profiles')
    return send_from_directory(profiles_dir, filename)
