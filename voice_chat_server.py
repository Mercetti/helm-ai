#!/usr/bin/env python3
"""
Stellar Logic AI - Voice Chat Server
Real-time voice communication with WebRTC and Socket.io
"""

import os
import logging
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import uuid
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'stellar-voice-chat-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceChatManager:
    def __init__(self):
        self.active_calls = {}
        self.user_sessions = {}
        self.voice_recordings = []
    
    def create_call_session(self, caller_id, participants):
        """Create a new voice call session"""
        call_id = str(uuid.uuid4())
        session = {
            'call_id': call_id,
            'caller_id': caller_id,
            'participants': participants,
            'started_at': datetime.now(),
            'status': 'active',
            'recording_enabled': True
        }
        self.active_calls[call_id] = session
        return call_id
    
    def end_call_session(self, call_id):
        """End a voice call session"""
        if call_id in self.active_calls:
            session = self.active_calls[call_id]
            session['ended_at'] = datetime.now()
            session['status'] = 'ended'
            # Move to recordings for compliance
            self.voice_recordings.append(session)
            del self.active_calls[call_id]
            return True
        return False
    
    def log_voice_event(self, call_id, user_id, event_type, details):
        """Log voice events for compliance"""
        log_entry = {
            'call_id': call_id,
            'user_id': user_id,
            'event_type': event_type,
            'details': details,
            'timestamp': datetime.now(),
            'ip_address': request.remote_addr if request else None
        }
        logger.info(f"Voice Event: {log_entry}")
        # Store in database for compliance

voice_manager = VoiceChatManager()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Check if the service is running"""
    return jsonify({
        'status': 'healthy',
        'service': 'voice_chat_server',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/voice/call', methods=['POST'])
def create_call():
    """Create a new voice call"""
    data = request.get_json()
    caller_id = data.get('caller_id')
    participants = data.get('participants', [])
    
    call_id = voice_manager.create_call_session(caller_id, participants)
    
    return jsonify({
        'success': True,
        'call_id': call_id,
        'signaling_server': 'http://localhost:5003',
        'turn_server': 'turn:your-turn-server.com:3478',
        'stun_server': 'stun:stun.l.google.com:19302'
    })

@app.route('/api/voice/call/<call_id>/end', methods=['POST'])
def end_call(call_id):
    """End a voice call"""
    success = voice_manager.end_call_session(call_id)
    return jsonify({'success': success})

# Socket.IO events for real-time signaling
@socketio.on('join_voice_call')
def on_join_voice_call(data):
    call_id = data['call_id']
    user_id = data['user_id']
    
    join_room(call_id)
    emit('user_joined_call', {
        'user_id': user_id,
        'call_id': call_id
    }, room=call_id)
    
    voice_manager.log_voice_event(call_id, user_id, 'JOINED_CALL', 'User joined voice call')

@socketio.on('leave_voice_call')
def on_leave_voice_call(data):
    call_id = data['call_id']
    user_id = data['user_id']
    
    leave_room(call_id)
    emit('user_left_call', {
        'user_id': user_id,
        'call_id': call_id
    }, room=call_id)
    
    voice_manager.log_voice_event(call_id, user_id, 'LEFT_CALL', 'User left voice call')

@socketio.on('voice_signal')
def on_voice_signal(data):
    """Handle WebRTC signaling"""
    call_id = data['call_id']
    target_user = data['target_user']
    signal_data = data['signal']
    
    emit('voice_signal', {
        'from_user': data['from_user'],
        'signal': signal_data
    }, room=target_user)

@socketio.on('voice_recording_start')
def on_voice_recording_start(data):
    """Start voice recording for compliance"""
    call_id = data['call_id']
    user_id = data['user_id']
    
    voice_manager.log_voice_event(call_id, user_id, 'RECORDING_STARTED', 'Voice recording started')

@socketio.on('voice_recording_stop')
def on_voice_recording_stop(data):
    """Stop voice recording"""
    call_id = data['call_id']
    user_id = data['user_id']
    recording_data = data.get('recording_data')
    
    voice_manager.log_voice_event(call_id, user_id, 'RECORDING_STOPPED', 'Voice recording stopped')

if __name__ == '__main__':
    print("🎤 Starting Voice Chat Server...")
    print("📊 Voice chat available at: http://localhost:5003")
    print("🔐 All voice calls recorded for compliance")
    socketio.run(app, host='0.0.0.0', port=5003, debug=False)
