#!/usr/bin/env python3
"""
Stellar Logic AI - Friends & Presence System
Gaming-inspired social features with unified messaging
"""

import sqlite3
import json
import time
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app, origins=['http://localhost:5000', 'http://localhost:8000'])

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FriendsSystem:
    def __init__(self, db_path="friends_system.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize friends system database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users with gaming-style profiles
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                display_name TEXT NOT NULL,
                avatar TEXT DEFAULT '👤',
                status TEXT DEFAULT 'offline',
                status_message TEXT,
                last_seen TIMESTAMP,
                current_activity TEXT,
                role TEXT DEFAULT 'member',
                level INTEGER DEFAULT 1,
                experience INTEGER DEFAULT 0,
                achievements TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Friends relationships
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS friendships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                friend_id INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                request_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                accepted_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (friend_id) REFERENCES users (id),
                UNIQUE(user_id, friend_id)
            )
        ''')
        
        # Groups/Teams
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                icon TEXT DEFAULT '👥',
                color TEXT DEFAULT '#667eea',
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users (id)
            )
        ''')
        
        # Group memberships
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS group_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                role TEXT DEFAULT 'member',
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (group_id) REFERENCES groups (id),
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(group_id, user_id)
            )
        ''')
        
        # Unified messaging system
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER NOT NULL,
                recipient_id INTEGER,
                group_id INTEGER,
                message_type TEXT DEFAULT 'text',
                content TEXT NOT NULL,
                attachments TEXT,
                reactions TEXT,
                edited BOOLEAN DEFAULT FALSE,
                edited_at TIMESTAMP,
                deleted BOOLEAN DEFAULT FALSE,
                deleted_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sender_id) REFERENCES users (id),
                FOREIGN KEY (recipient_id) REFERENCES users (id),
                FOREIGN KEY (group_id) REFERENCES groups (id)
            )
        ''')
        
        # Activity feed
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                activity_type TEXT NOT NULL,
                activity_data TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Presence/Status updates
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS presence_updates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                activity TEXT,
                location TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_user(self, username, display_name, role='member'):
        """Create new user with gaming profile"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (username, display_name, role, status)
                VALUES (?, ?, ?, 'offline')
            ''', (username, display_name, role))
            
            user_id = cursor.lastrowid
            conn.commit()
            
            # Log activity
            self.log_activity(user_id, 'USER_CREATED', {'username': username})
            
            return {'success': True, 'user_id': user_id}
        except sqlite3.IntegrityError:
            return {'success': False, 'error': 'Username already exists'}
        finally:
            conn.close()
    
    def send_friend_request(self, user_id, friend_id, message=''):
        """Send friend request"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO friendships (user_id, friend_id, status, request_message)
                VALUES (?, ?, 'pending', ?)
            ''', (user_id, friend_id, message))
            
            conn.commit()
            
            # Log activity
            self.log_activity(user_id, 'FRIEND_REQUEST_SENT', {'friend_id': friend_id})
            
            return {'success': True}
        except sqlite3.IntegrityError:
            return {'success': False, 'error': 'Friendship already exists'}
        finally:
            conn.close()
    
    def accept_friend_request(self, user_id, friend_id):
        """Accept friend request"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE friendships 
            SET status = 'accepted', accepted_at = CURRENT_TIMESTAMP 
            WHERE user_id = ? AND friend_id = ?
        ''', (friend_id, user_id))
        
        conn.commit()
        conn.close()
        
        # Log activities
        self.log_activity(user_id, 'FRIEND_REQUEST_ACCEPTED', {'friend_id': friend_id})
        self.log_activity(friend_id, 'FRIEND_REQUEST_ACCEPTED', {'friend_id': user_id})
        
        return {'success': True}
    
    def get_friends_list(self, user_id):
        """Get user's friends with online status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.id, u.username, u.display_name, u.avatar, u.status, 
                   u.status_message, u.last_seen, u.current_activity
            FROM users u
            JOIN friendships f ON (
                (f.user_id = ? AND f.friend_id = u.id AND f.status = 'accepted') OR
                (f.friend_id = ? AND f.user_id = u.id AND f.status = 'accepted')
            )
            WHERE u.id != ?
            ORDER BY u.status DESC, u.last_seen DESC
        ''', (user_id, user_id, user_id))
        
        friends = cursor.fetchall()
        conn.close()
        
        return [{
            'id': friend[0],
            'username': friend[1],
            'display_name': friend[2],
            'avatar': friend[3],
            'status': friend[4],
            'status_message': friend[5],
            'last_seen': friend[6],
            'current_activity': friend[7]
        } for friend in friends]
    
    def update_presence(self, user_id, status, activity=None, location=None):
        """Update user presence and status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update user status
        cursor.execute('''
            UPDATE users 
            SET status = ?, current_activity = ?, last_seen = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, activity, user_id))
        
        # Log presence update
        cursor.execute('''
            INSERT INTO presence_updates (user_id, status, activity, location)
            VALUES (?, ?, ?, ?)
        ''', (user_id, status, activity, location))
        
        conn.commit()
        conn.close()
        
        # Log activity
        self.log_activity(user_id, 'PRESENCE_UPDATE', {'status': status, 'activity': activity})
        
        return {'success': True}
    
    def send_message(self, sender_id, recipient_id=None, group_id=None, content='', message_type='text'):
        """Send message to user or group"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO messages (sender_id, recipient_id, group_id, message_type, content)
            VALUES (?, ?, ?, ?, ?)
        ''', (sender_id, recipient_id, group_id, message_type, content))
        
        message_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Log activity
        self.log_activity(sender_id, 'MESSAGE_SENT', {
            'recipient_id': recipient_id,
            'group_id': group_id,
            'message_type': message_type
        })
        
        return {'success': True, 'message_id': message_id}
    
    def get_unified_inbox(self, user_id, limit=50):
        """Get unified inbox with all messages"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT m.id, m.sender_id, m.recipient_id, m.group_id, m.message_type, 
                   m.content, m.created_at, u.display_name, u.avatar
            FROM messages m
            JOIN users u ON m.sender_id = u.id
            WHERE (m.recipient_id = ? OR m.group_id IN (
                SELECT group_id FROM group_members WHERE user_id = ?
            )) AND m.deleted = FALSE
            ORDER BY m.created_at DESC
            LIMIT ?
        ''', (user_id, user_id, limit))
        
        messages = cursor.fetchall()
        conn.close()
        
        return [{
            'id': msg[0],
            'sender_id': msg[1],
            'recipient_id': msg[2],
            'group_id': msg[3],
            'message_type': msg[4],
            'content': msg[5],
            'created_at': msg[6],
            'sender_name': msg[7],
            'sender_avatar': msg[8]
        } for msg in messages]
    
    def log_activity(self, user_id, activity_type, activity_data):
        """Log user activity for feed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO activities (user_id, activity_type, activity_data)
            VALUES (?, ?, ?)
        ''', (user_id, activity_type, json.dumps(activity_data)))
        
        conn.commit()
        conn.close()
    
    def get_activity_feed(self, user_id, limit=20):
        """Get activity feed for user and friends"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT a.activity_type, a.activity_data, a.timestamp, u.display_name, u.avatar
            FROM activities a
            JOIN users u ON a.user_id = u.id
            WHERE a.user_id = ? OR a.user_id IN (
                SELECT friend_id FROM friendships 
                WHERE user_id = ? AND status = 'accepted'
                UNION
                SELECT user_id FROM friendships 
                WHERE friend_id = ? AND status = 'accepted'
            )
            ORDER BY a.timestamp DESC
            LIMIT ?
        ''', (user_id, user_id, user_id, limit))
        
        activities = cursor.fetchall()
        conn.close()
        
        return [{
            'activity_type': act[0],
            'activity_data': json.loads(act[1]) if act[1] else {},
            'timestamp': act[2],
            'user_name': act[3],
            'user_avatar': act[4]
        } for act in activities]

# Initialize friends system
friends_system = FriendsSystem()

# API Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Check if the service is running"""
    return jsonify({
        'status': 'healthy',
        'service': 'friends_system_server',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/friends', methods=['GET'])
def get_friends():
    """Get user's friends list"""
    user_id = request.args.get('user_id', 1)
    friends = friends_system.get_friends_list(user_id)
    return jsonify({'friends': friends})

@app.route('/api/friends/request', methods=['POST'])
def send_friend_request():
    """Send friend request"""
    data = request.get_json()
    user_id = data.get('user_id')
    friend_id = data.get('friend_id')
    message = data.get('message', '')
    
    result = friends_system.send_friend_request(user_id, friend_id, message)
    return jsonify(result)

@app.route('/api/friends/accept', methods=['POST'])
def accept_friend_request():
    """Accept friend request"""
    data = request.get_json()
    user_id = data.get('user_id')
    friend_id = data.get('friend_id')
    
    result = friends_system.accept_friend_request(user_id, friend_id)
    return jsonify(result)

@app.route('/api/presence', methods=['POST'])
def update_presence():
    """Update user presence"""
    data = request.get_json()
    user_id = data.get('user_id')
    status = data.get('status')
    activity = data.get('activity')
    location = data.get('location')
    
    result = friends_system.update_presence(user_id, status, activity, location)
    return jsonify(result)

@app.route('/api/messages/unified', methods=['GET'])
def get_unified_inbox():
    """Get unified message inbox"""
    user_id = request.args.get('user_id', 1)
    limit = request.args.get('limit', 50)
    
    messages = friends_system.get_unified_inbox(user_id, limit)
    return jsonify({'messages': messages})

@app.route('/api/messages/send', methods=['POST'])
def send_message():
    """Send message to user or group"""
    data = request.get_json()
    sender_id = data.get('sender_id')
    recipient_id = data.get('recipient_id')
    group_id = data.get('group_id')
    content = data.get('content')
    message_type = data.get('message_type', 'text')
    
    result = friends_system.send_message(sender_id, recipient_id, group_id, content, message_type)
    return jsonify(result)

@app.route('/api/activity/feed', methods=['GET'])
def get_activity_feed():
    """Get activity feed"""
    user_id = request.args.get('user_id', 1)
    limit = request.args.get('limit', 20)
    
    activities = friends_system.get_activity_feed(user_id, limit)
    return jsonify({'activities': activities})

if __name__ == '__main__':
    print("👥 Starting Friends & Presence System...")
    print("📊 Available at: http://localhost:5005")
    print("🎮 Gaming-style social features ready!")
    app.run(host='0.0.0.0', port=5005, debug=False)
