import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.session import InterviewSession
from app.services.cv_parser import parse_cv, allowed_file
from datetime import datetime

interview_bp = Blueprint('interview_session', __name__)

@interview_bp.route('/upload-cv', methods=['POST'])
@jwt_required()
def upload_cv():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided.'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected.'}), 400
    
    if not allowed_file(file.filename, current_app.config['ALLOWED_CV_EXTENSIONS']):
        return jsonify({'error': 'Unsupported file format. Allowed: .pdf, .docx'}), 400
    
    ext = os.path.splitext(secure_filename(file.filename))[1]
    cv_id = str(uuid.uuid4())
    safe_filename = f"{cv_id}{ext}"
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], safe_filename)
    
    try:
        file.save(file_path)
        cv_text = parse_cv(file_path)
        
        return jsonify({
            'cv_id': cv_id,
            'cv_text': cv_text,
            'message': 'CV uploaded and parsed successfully.'
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to process CV.'}), 500
    finally:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass

@interview_bp.route('/start', methods=['POST'])
@jwt_required()
def start():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    if not data or not data.get('template_id'):
        return jsonify({'message': 'Template ID required'}), 400

    new_session = InterviewSession(
        user_id=current_user_id,
        template_id=data['template_id'],
        started_at=datetime.utcnow(),
        interview_status='in_progress'
    )
    db.session.add(new_session)
    db.session.commit()

    return jsonify({'message': 'Interview started', 'session': new_session.to_dict()}), 201

@interview_bp.route('/answer', methods=['POST'])
@jwt_required()
def answer():
    # Placeholder for answering logic
    return jsonify({'message': 'Answer received'}), 200

@interview_bp.route('/end', methods=['POST'])
@jwt_required()
def end():
    data = request.get_json()
    if not data or not data.get('session_id'):
        return jsonify({'message': 'Session ID required'}), 400
        
    session = InterviewSession.query.get(data['session_id'])
    if session:
        session.ended_at = datetime.utcnow()
        session.interview_status = 'completed'
        
        # Save proctoring metrics if provided
        session.tab_switch_count = data.get('tab_switch_count', session.tab_switch_count or 0)
        session.fullscreen_exit_count = data.get('fullscreen_exit_count', session.fullscreen_exit_count or 0)
        session.face_missing_count = data.get('face_missing_count', session.face_missing_count or 0)
        
        # Deduct 10 credits
        user = session.user
        if user:
            user.credits_remaining = max(0, (user.credits_remaining or 0) - 10)
            
            # Update active subscription credits_used
            from app.models.subscription import Subscription
            active_sub = Subscription.query.filter_by(user_id=user.id, status='active').first()
            if active_sub:
                active_sub.credits_used = (active_sub.credits_used or 0) + 10
                
        db.session.commit()
        return jsonify({'message': 'Interview ended and credits deducted', 'session': session.to_dict()}), 200
        
    return jsonify({'message': 'Session not found'}), 404

@interview_bp.route('/frame', methods=['POST'])
@jwt_required()
def frame():
    # Placeholder for frame analysis
    return jsonify({'message': 'Frame analyzed'}), 200

@interview_bp.route('/session/<id>', methods=['GET'])
@jwt_required()
def get_session(id):
    session = InterviewSession.query.get(id)
    if not session:
        return jsonify({'message': 'Session not found'}), 404
    return jsonify({'session': session.to_dict()}), 200

@interview_bp.route('/messages/<session_id>', methods=['GET'])
@jwt_required()
def get_messages(session_id):
    from app.models.message import InterviewMessage
    
    messages = InterviewMessage.query.filter_by(session_id=session_id).order_by(InterviewMessage.created_at.asc()).all()
    return jsonify({
        'messages': [msg.to_dict() for msg in messages]
    }), 200

