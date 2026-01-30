#!/usr/bin/env python3
"""
Stellar Logic AI - Learning Platform
Persistent learning and adaptation system for the custom AI model
"""

import json
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Any

class StellarLearningPlatform:
    def __init__(self, db_path="stellar_learning.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the learning database with all necessary tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # User preferences and learning data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id TEXT PRIMARY KEY,
                email_style TEXT DEFAULT 'professional',
                paragraph_length TEXT DEFAULT '3-4',
                tone TEXT DEFAULT 'business-focused',
                formatting_preferences TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Conversation history with learning insights
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                user_message TEXT,
                ai_response TEXT,
                context TEXT,
                user_feedback TEXT,
                success_rating INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Learning patterns and successful approaches
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT,
                pattern_content TEXT,
                success_count INTEGER DEFAULT 0,
                usage_count INTEGER DEFAULT 0,
                effectiveness_score REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Feedback and adaptation history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                feedback_type TEXT,
                feedback_content TEXT,
                ai_adaptation TEXT,
                improvement_success INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Market and business intelligence
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS business_intelligence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                insight_content TEXT,
                confidence_score REAL DEFAULT 0.0,
                source TEXT,
                verified INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def store_conversation(self, user_id: str, user_message: str, ai_response: str, 
                          context: str = "", user_feedback: str = "", success_rating: int = 0):
        """Store conversation with learning metadata"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversations 
            (user_id, user_message, ai_response, context, user_feedback, success_rating)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, user_message, ai_response, context, user_feedback, success_rating))
        
        conn.commit()
        conn.close()
    
    def learn_from_feedback(self, user_id: str, feedback_type: str, feedback_content: str, 
                           ai_adaptation: str, improvement_success: int = 0):
        """Store and learn from user feedback"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO feedback_history 
            (user_id, feedback_type, feedback_content, ai_adaptation, improvement_success)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, feedback_type, feedback_content, ai_adaptation, improvement_success))
        
        # Update user preferences based on feedback
        self.update_preferences_from_feedback(user_id, feedback_type, feedback_content)
        
        conn.commit()
        conn.close()
    
    def update_preferences_from_feedback(self, user_id: str, feedback_type: str, feedback_content: str):
        """Update user preferences based on feedback patterns"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Extract preferences from feedback
        preferences = self.analyze_feedback_for_preferences(feedback_content)
        
        # Update or insert user preferences
        if preferences:
            set_clause = ", ".join([f"{k} = ?" for k in preferences.keys()])
            values = list(preferences.values()) + [user_id]
            
            cursor.execute(f'''
                UPDATE user_preferences 
                SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', values)
            
            # If no user exists, insert one
            if cursor.rowcount == 0:
                columns = ", ".join(preferences.keys())
                placeholders = ", ".join(["?"] * len(preferences))
                cursor.execute(f'''
                    INSERT INTO user_preferences (user_id, {columns})
                    VALUES (?, {placeholders})
                ''', [user_id] + list(preferences.values()))
        
        conn.commit()
        conn.close()
    
    def analyze_feedback_for_preferences(self, feedback_content: str) -> Dict[str, str]:
        """Analyze feedback content to extract user preferences"""
        preferences = {}
        feedback_lower = feedback_content.lower()
        
        # Email style preferences
        if "shorter" in feedback_lower or "concise" in feedback_lower:
            preferences["email_style"] = "concise"
        elif "detailed" in feedback_lower or "comprehensive" in feedback_lower:
            preferences["email_style"] = "detailed"
        
        # Paragraph length preferences
        if "short paragraphs" in feedback_lower or "brief" in feedback_lower:
            preferences["paragraph_length"] = "2-3"
        elif "longer paragraphs" in feedback_lower:
            preferences["paragraph_length"] = "4-5"
        
        # Formatting preferences
        if "format better" in feedback_lower or "structure" in feedback_lower:
            preferences["formatting_preferences"] = "structured"
        elif "casual" in feedback_lower:
            preferences["tone"] = "casual"
        elif "formal" in feedback_lower or "professional" in feedback_lower:
            preferences["tone"] = "formal"
        
        return preferences
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get learned user preferences"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM user_preferences WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        if result:
            columns = [description[0] for description in cursor.description]
            preferences = dict(zip(columns, result))
            return preferences
        else:
            # Return default preferences
            return {
                "email_style": "professional",
                "paragraph_length": "3-4",
                "tone": "business-focused",
                "formatting_preferences": "structured"
            }
    
    def get_learning_context(self, user_id: str) -> str:
        """Generate learning context for AI based on user history and preferences"""
        preferences = self.get_user_preferences(user_id)
        
        # Get recent successful patterns
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT feedback_content, ai_adaptation, improvement_success 
            FROM feedback_history 
            WHERE user_id = ? AND improvement_success > 0
            ORDER BY created_at DESC 
            LIMIT 5
        ''', (user_id,))
        
        successful_feedback = cursor.fetchall()
        conn.close()
        
        context_parts = []
        
        # Add preferences to context
        if preferences:
            context_parts.append(f"User Preferences: {preferences}")
        
        # Add successful adaptations
        if successful_feedback:
            context_parts.append("Successful Adaptations:")
            for feedback, adaptation, success in successful_feedback:
                context_parts.append(f"- {feedback} → {adaptation}")
        
        return "\n".join(context_parts)
    
    def store_successful_pattern(self, pattern_type: str, pattern_content: str, success: bool = True):
        """Store successful communication patterns"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO learning_patterns 
            (pattern_type, pattern_content, success_count, usage_count, effectiveness_score)
            VALUES (?, ?, 
                COALESCE((SELECT success_count FROM learning_patterns WHERE pattern_type = ? AND pattern_content = ?), 0) + ?,
                COALESCE((SELECT usage_count FROM learning_patterns WHERE pattern_type = ? AND pattern_content = ?), 0) + 1,
                COALESCE((SELECT effectiveness_score FROM learning_patterns WHERE pattern_type = ? AND pattern_content = ?), 0.0) * 0.9 + 0.1
            )
        ''', (pattern_type, pattern_content, pattern_type, pattern_content, 
              1 if success else 0, pattern_type, pattern_content, 
              pattern_type, pattern_content))
        
        conn.commit()
        conn.close()
    
    def get_effective_patterns(self, pattern_type: str, limit: int = 5) -> List[str]:
        """Get most effective patterns of a certain type"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT pattern_content FROM learning_patterns 
            WHERE pattern_type = ? AND effectiveness_score > 0.5
            ORDER BY effectiveness_score DESC, usage_count DESC
            LIMIT ?
        ''', (pattern_type, limit))
        
        patterns = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return patterns

# Initialize the learning platform
learning_platform = StellarLearningPlatform()
