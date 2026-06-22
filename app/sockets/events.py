from flask import request
from flask_socketio import emit
import json
import re
from datetime import datetime
from app import socketio, db
from app.models.session import InterviewSession
from app.models.template import InterviewTemplate
from app.services.deepseek import generate_with_retry, check_answer_relevance
from app.services.utils import strip_markdown
from app.services.cv_parser import build_cv_context
from app.services.gemini_vision import analyze_frames_batch

# Store active sessions in memory by socket ID
sessions = {}

MAX_QUESTIONS = 5
MAX_FRAMES_STORED = 20

@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")
    if request.sid in sessions:
        # We could potentially handle abandonment here and save to DB
        del sessions[request.sid]

@socketio.on('start_interview')
def handle_start_interview(data):
    session_id = data.get('session_id')
    cv_text = data.get('cv_text', None)

    if not session_id:
        emit('error', {'message': 'session_id is required'})
        return

    # Fetch from DB
    db_session = InterviewSession.query.get(session_id)
    if not db_session:
        emit('error', {'message': 'Invalid session_id'})
        return
        
    template = InterviewTemplate.query.get(db_session.template_id)
    if not template:
        emit('error', {'message': 'Template not found for this session'})
        return

    print(f"Starting interview '{template.name}' for session {request.sid}")

    # Build system prompt
    system_prompt = template.system_prompt
    has_cv = False

    # Optional: Logic for CV context if template implies it, though template DB doesn't have requires_cv by default
    # but we can check if cv_text is provided
    if cv_text:
        cv_context = build_cv_context(cv_text)
        system_prompt = system_prompt + cv_context
        has_cv = True
        print(f"CV context injected for '{template.name}'")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Please begin the interview."}
    ]

    # Generate first question
    first_question = generate_with_retry(messages)
    messages.append({"role": "assistant", "content": first_question})

    # Save memory session
    sessions[request.sid] = {
        'db_session_id': session_id,
        'messages': messages,
        'question_count': 1,
        'has_cv': has_cv,
        'frames': [],
    }
    
    # Update DB status
    db_session.interview_status = 'in_progress'
    db.session.commit()

    emit('question', {
        'question_number': 1,
        'text': first_question,
        'clean_text': strip_markdown(first_question),
        'is_finished': False,
        'has_cv': has_cv
    })

@socketio.on('answer')
def handle_answer(data):
    if request.sid not in sessions:
        emit('error', {'message': 'Session not found. Please start an interview first.'})
        return

    session = sessions[request.sid]
    answer = data.get('answer', '').strip()
    
    if not answer:
        emit('error', {'message': 'Answer cannot be empty'})
        return

    if answer.lower() in ("quit", "exit", "stop"):
        session['messages'].append({"role": "user", "content": answer})
        generate_report(request.sid)
        return

    is_relevant = check_answer_relevance(session['messages'], answer)

    if not is_relevant:
        warning_msg = "Please stay on topic and answer the interview question."
        session['messages'].append({"role": "user", "content": answer})
        session['messages'].append({"role": "assistant", "content": warning_msg})
        emit('question', {
            'question_number': session['question_count'],
            'text': warning_msg,
            'clean_text': warning_msg,
            'is_finished': False
        })
        return

    session['messages'].append({"role": "user", "content": answer})

    if session['question_count'] < MAX_QUESTIONS:
        next_question = generate_with_retry(session['messages'])
        session['messages'].append({"role": "assistant", "content": next_question})
        session['question_count'] += 1

        emit('question', {
            'question_number': session['question_count'],
            'text': next_question,
            'clean_text': strip_markdown(next_question),
            'is_finished': False
        })
    else:
        generate_report(request.sid)

@socketio.on('receive_frame')
def handle_receive_frame(data):
    if request.sid not in sessions:
        return

    session = sessions[request.sid]
    frame_data = data.get('frame_data', None)

    if not frame_data:
        return

    if len(session['frames']) < MAX_FRAMES_STORED:
        session['frames'].append(frame_data)
    
    emit('frame_received', {
        'frame_count': len(session['frames']),
        'max_frames': MAX_FRAMES_STORED
    })

def generate_report(sid):
    session = sessions[sid]
    
    # Prompt for structured JSON response to save to DB
    json_prompt = """
INTERVIEW_FINISHED

Generate a detailed evaluation report. 
IMPORTANT: You MUST return your response as a valid JSON object exactly matching this structure, with no extra markdown blocks or text outside the JSON:

{
  "performance_summary": "A brief overview of the candidate's performance.",
  "preparation_plan": "A clear, actionable step-by-step plan for the candidate to improve their weak areas.",
  "strengths": "Bullet points of strengths",
  "weaknesses": "Bullet points of weaknesses",
  "final_remarks": "A short closing encouraging sentence.",
  "overall_score": 85.0,
  "communication_score": 90.0,
  "technical_score": 80.0,
  "confidence_score": 85.0,
  "problem_solving_score": 85.0,
  "security_score": 85.0
}

Ensure the numeric scores are out of 100.
"""
    session['messages'].append({
        "role": "user",
        "content": json_prompt
    })

    print(f"Generating report for session {sid}...")
    raw_response = generate_with_retry(session['messages'])
    
    # Parse the JSON response
    report_data = {}
    try:
        # Strip markdown json blocks if AI included them
        clean_json = re.sub(r'```json\n|\n```|```', '', raw_response).strip()
        report_data = json.loads(clean_json)
    except json.JSONDecodeError:
        print("Failed to decode JSON from AI, fallback to raw text.")
        report_data = {
            "performance_summary": raw_response,
            "final_remarks": "Thank you for completing the interview.",
            "overall_score": 0
        }

    # Behavioral Analysis
    behavioral_summary = None
    frames = session.get('frames', [])
    if frames and len(frames) > 0:
        try:
            behavioral_summary = analyze_frames_batch(frames)
        except Exception as e:
            print(f"Behavioral analysis failed: {e}")
            behavioral_summary = "Behavioral analysis could not be completed."
    
    # Save to Database
    db_session = InterviewSession.query.get(session['db_session_id'])
    if db_session:
        db_session.ended_at = datetime.utcnow()
        db_session.interview_status = 'completed'
        
        # Calculate duration if started_at exists
        if db_session.started_at:
            duration = db_session.ended_at - db_session.started_at
            db_session.duration_minutes = duration.seconds // 60
            
        db_session.performance_summary = report_data.get('performance_summary', '')
        db_session.preparation_plan = report_data.get('preparation_plan', '')
        db_session.strengths = report_data.get('strengths', '')
        db_session.weaknesses = report_data.get('weaknesses', '')
        db_session.final_remarks = report_data.get('final_remarks', '')
        
        db_session.overall_score = report_data.get('overall_score')
        db_session.communication_score = report_data.get('communication_score')
        db_session.technical_score = report_data.get('technical_score')
        db_session.confidence_score = report_data.get('confidence_score')
        db_session.problem_solving_score = report_data.get('problem_solving_score')
        db_session.security_score = report_data.get('security_score')
        
        db_session.behavioral_analysis = behavioral_summary
        db_session.frames_analyzed = len(frames)
        
        db.session.commit()
        print(f"Saved session results to DB for {session['db_session_id']}")

    # Build visual report for frontend
    visual_report = f"## Performance Summary\n{report_data.get('performance_summary', '')}\n\n"
    visual_report += f"## Preparation Plan\n{report_data.get('preparation_plan', '')}\n\n"
    if behavioral_summary:
        visual_report += f"\n\n============================================================\n\n## 📹 VIDEO BEHAVIORAL ANALYSIS\n(Powered by AI Video Analysis)\n\n{behavioral_summary}"

    spoken_remarks = report_data.get('final_remarks', 'The interview has concluded.')

    emit('report', {
        'text': visual_report,
        'clean_text': strip_markdown(visual_report),
        'spoken_remarks': spoken_remarks,
        'is_finished': True,
        'has_behavioral_analysis': behavioral_summary is not None,
        'frames_analyzed': len(frames),
        'scores': {
            'overall': report_data.get('overall_score'),
            'technical': report_data.get('technical_score'),
            'communication': report_data.get('communication_score')
        }
    })

    if sid in sessions:
        del sessions[sid]
