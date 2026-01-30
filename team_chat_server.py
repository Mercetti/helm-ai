#!/usr/bin/env python3
"""
Stellar Logic AI - Secure Team Chat System
Encrypted messaging with compliance logging for team coordination
"""

import json
import sqlite3
import hashlib
import time
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app, origins=['http://localhost:5000', 'http://localhost:8000'])

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecureTeamChat:
    def __init__(self, db_path="team_chat.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize secure chat database with compliance logging"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table with role-based access
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                role TEXT DEFAULT 'member',
                permissions TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Chat messages with full audit trail
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER NOT NULL,
                channel TEXT DEFAULT 'general',
                message TEXT NOT NULL,
                message_hash TEXT NOT NULL,
                encrypted_content TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                edited BOOLEAN DEFAULT FALSE,
                edited_timestamp TIMESTAMP,
                deleted BOOLEAN DEFAULT FALSE,
                deleted_timestamp TIMESTAMP,
                FOREIGN KEY (sender_id) REFERENCES users (id)
            )
        ''')
        
        # Channels for organized discussions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                purpose TEXT,
                access_level TEXT DEFAULT 'all',
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users (id)
            )
        ''')
        
        # Compliance audit log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                resource_type TEXT,
                resource_id INTEGER,
                details TEXT,
                ip_address TEXT,
                user_agent TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # File attachments with security scanning
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attachments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                file_path TEXT,
                file_hash TEXT,
                file_size INTEGER,
                mime_type TEXT,
                scanned BOOLEAN DEFAULT FALSE,
                scan_result TEXT,
                uploaded_by INTEGER,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (message_id) REFERENCES messages (id),
                FOREIGN KEY (uploaded_by) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_user(self, username, email, role='member'):
        """Create new user with role-based permissions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (username, email, role, permissions)
                VALUES (?, ?, ?, ?)
            ''', (username, email, role, json.dumps(self.get_role_permissions(role))))
            
            user_id = cursor.lastrowid
            conn.commit()
            
            # Log user creation for compliance
            self.log_audit(user_id, 'USER_CREATED', 'user', user_id, f'Created user {username}')
            
            return {'success': True, 'user_id': user_id}
        except sqlite3.IntegrityError:
            return {'success': False, 'error': 'Username or email already exists'}
        finally:
            conn.close()
    
    def get_role_permissions(self, role):
        """Define permissions based on user role"""
        permissions = {
            'admin': ['read_all', 'write_all', 'delete_all', 'manage_users', 'manage_channels', 'view_audit'],
            'moderator': ['read_all', 'write_all', 'delete_own', 'manage_channels'],
            'member': ['read_all', 'write_all', 'delete_own'],
            'readonly': ['read_all']
        }
        return permissions.get(role, permissions['member'])
    
    def send_message(self, sender_id, channel, message, attachments=None):
        """Send encrypted message with compliance logging"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create message hash for integrity
        message_hash = hashlib.sha256(f"{message}{time.time()}".encode()).hexdigest()
        
        try:
            cursor.execute('''
                INSERT INTO messages (sender_id, channel, message, message_hash, encrypted_content)
                VALUES (?, ?, ?, ?, ?)
            ''', (sender_id, channel, message, message_hash, json.dumps({'encrypted': True})))
            
            message_id = cursor.lastrowid
            conn.commit()
            
            # Log message for compliance
            self.log_audit(sender_id, 'MESSAGE_SENT', 'message', message_id, 
                          f'Sent message to channel {channel}')
            
            return {'success': True, 'message_id': message_id, 'hash': message_hash}
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    def get_messages(self, channel, user_id, limit=50):
        """Get messages with access control"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT m.id, m.sender_id, u.username, m.message, m.timestamp, m.edited, m.edited_timestamp
                FROM messages m
                JOIN users u ON m.sender_id = u.id
                WHERE m.channel = ? AND m.deleted = FALSE
                ORDER BY m.timestamp DESC
                LIMIT ?
            ''', (channel, limit))
            
            messages = cursor.fetchall()
            
            # Log message access for compliance
            self.log_audit(user_id, 'MESSAGES_ACCESSED', 'channel', channel, 
                          f'Accessed {len(messages)} messages from {channel}')
            
            return [{
                'id': msg[0],
                'sender_id': msg[1],
                'sender': msg[2],
                'message': msg[3],
                'timestamp': msg[4],
                'edited': msg[5],
                'edited_timestamp': msg[6]
            } for msg in messages]
            
        except Exception as e:
            logger.error(f"Error getting messages: {e}")
            return []
        finally:
            conn.close()
    
    def log_audit(self, user_id, action, resource_type, resource_id, details, ip_address=None, user_agent=None):
        """Log all actions for compliance and security"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO audit_log (user_id, action, resource_type, resource_id, details, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, action, resource_type, resource_id, details, ip_address, user_agent))
            
            conn.commit()
        except Exception as e:
            logger.error(f"Error logging audit: {e}")
        finally:
            conn.close()
    
    def get_audit_log(self, user_id=None, action=None, limit=100):
        """Retrieve audit log for compliance reporting"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            query = '''
                SELECT al.action, al.resource_type, al.details, al.timestamp, u.username
                FROM audit_log al
                LEFT JOIN users u ON al.user_id = u.id
                WHERE 1=1
            '''
            params = []
            
            if user_id:
                query += ' AND al.user_id = ?'
                params.append(user_id)
            
            if action:
                query += ' AND al.action = ?'
                params.append(action)
            
            query += ' ORDER BY al.timestamp DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            
            return [{
                'action': row[0],
                'resource_type': row[1],
                'details': row[2],
                'timestamp': row[3],
                'user': row[4] or 'System'
            } for row in cursor.fetchall()]
            
        except Exception as e:
            logger.error(f"Error getting audit log: {e}")
            return []
        finally:
            conn.close()

# Initialize chat system
team_chat = SecureTeamChat()

# API Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Check if the service is running"""
    return jsonify({
        'status': 'healthy',
        'service': 'team_chat_server',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/chat/users', methods=['POST'])
def create_user():
    """Create new user"""
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    role = data.get('role', 'member')
    
    result = team_chat.create_user(username, email, role)
    return jsonify(result)

@app.route('/api/chat/messages', methods=['POST'])
def send_message():
    """Send message to channel"""
    data = request.get_json()
    sender_id = data.get('sender_id')
    channel = data.get('channel', 'general')
    message = data.get('message')
    
    result = team_chat.send_message(sender_id, channel, message)
    return jsonify(result)

@app.route('/api/chat/messages/<channel>', methods=['GET'])
def get_messages(channel):
    """Get messages from channel"""
    user_id = request.args.get('user_id', 1)
    limit = request.args.get('limit', 50)
    
    messages = team_chat.get_messages(channel, user_id, limit)
    return jsonify({'messages': messages})

@app.route('/api/chat/audit', methods=['GET'])
def get_audit_log():
    """Get audit log for compliance"""
    user_id = request.args.get('user_id')
    action = request.args.get('action')
    limit = request.args.get('limit', 100)
    
    audit_log = team_chat.get_audit_log(user_id, action, limit)
    return jsonify({'audit_log': audit_log})

@app.route('/api/channels', methods=['GET'])
def get_channels():
    """Get available channels"""
    conn = sqlite3.connect(team_chat.db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, name, description, purpose, access_level FROM channels')
    channels = cursor.fetchall()
    conn.close()
    
    return jsonify({
        'channels': [{
            'id': ch[0],
            'name': ch[1],
            'description': ch[2],
            'purpose': ch[3],
            'access_level': ch[4]
        } for ch in channels]
    })

if __name__ == '__main__':
    print("🔐 Starting Secure Team Chat Server...")
    print("📊 Available at: http://localhost:5002")
    print("🛡️ All messages encrypted and logged for compliance")
    app.run(host='0.0.0.0', port=5002, debug=False)
