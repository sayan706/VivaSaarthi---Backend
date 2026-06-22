"""
ElevenLabs TTS Proxy Route
Proxies text-to-speech requests to ElevenLabs to keep the API key secure.
"""

import requests as http_requests
from flask import Blueprint, request, Response, jsonify
from app.config import Config

tts_bp = Blueprint('tts', __name__)

@tts_bp.route('/', methods=['POST'])
def text_to_speech():
    """
    Proxy TTS request to ElevenLabs API.
    
    Accepts JSON: { "text": "...", "voice_gender": "male" | "female" }
    Returns: MP3 audio binary
    """
    if not Config.ELEVENLABS_API_KEY:
        return jsonify({'error': 'ElevenLabs API key not configured'}), 503

    data = request.get_json()
    if not data or not data.get('text'):
        return jsonify({'error': 'text is required'}), 400

    text = data['text']
    voice_gender = data.get('voice_gender', 'male')

    # ElevenLabs Voice IDs
    # You can replace these with exact Indian Voice IDs from your Voice Library
    if voice_gender == 'female':
        voice_id = "21m00Tcm4TlvDq8ikWAM" # Default: Rachel. Replace with an Indian female voice ID.
    else:
        voice_id = "pNInz6obpgDQGcFmaJgB" # Default: Adam. Replace with an Indian male voice ID.

    # Truncate very long text to avoid huge TTS costs
    if len(text) > 1000:
        text = text[:1000]

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "xi-api-key": Config.ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    }

    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }

    try:
        response = http_requests.post(url, json=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            return Response(
                response.content,
                mimetype='audio/mpeg',
                headers={
                    'Content-Type': 'audio/mpeg',
                    'Cache-Control': 'no-cache'
                }
            )
        else:
            error_msg = response.text[:200] if response.text else 'Unknown ElevenLabs error'
            print(f"ElevenLabs API error ({response.status_code}): {error_msg}")
            
            return jsonify({
                'error': f'ElevenLabs API error: {response.status_code}',
                'details': error_msg
            }), response.status_code

    except http_requests.exceptions.Timeout:
        return jsonify({'error': 'TTS request timed out'}), 504
    except Exception as e:
        print(f"TTS proxy error: {e}")
        return jsonify({'error': 'TTS service unavailable'}), 500
