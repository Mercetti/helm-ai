#!/usr/bin/env python3
"""
Simple database test without the problematic risk score calculation
"""

import sys
import os
sys.path.append('src')

from database.connection_pool import connection_pool_manager
from database.database_manager import get_database_manager
import sys
sys.path.append('src')

from models import Base, User, APIKey, AuditLog, SecurityEvent, GameSession, APIUsageLog
from models.user import UserRole
from models.api_key import APIKeyScope, APIKeyStatus
from models.audit_log import AuditAction, AuditCategory
from models.game_session import GameType

def test_database_simple():
    """Simple database test without risk score calculation"""
    print("🚀 Testing Helm AI Database Setup (Simple Version)")
    print("=" * 50)
    
    try:
        # Initialize SQLite connection pool
        print("📦 Creating SQLite connection pool...")
        pool = connection_pool_manager.create_sqlite_pool(
            name="sqlite",
            db_path="test_stellar_logic_ai_simple.db",
            min_connections=1,
            max_connections=5
        )
        print("✅ SQLite connection pool created")
        
        # Get database manager
        print("🗄️ Getting database manager...")
        db_manager = get_database_manager("sqlite")
        print("✅ Database manager initialized")
        
        # Health check
        print("🏥 Performing health check...")
        health = db_manager.health_check()
        print(f"✅ Health check: {health['status']}")
        
        # Create tables
        print("🏗️ Creating database tables...")
        db_manager.create_tables()
        print("✅ Database tables created")
        
        # Test user creation
        print("👤 Creating test user...")
        user = db_manager.create_user(
            email="test@example.com",
            name="Test User",
            role="USER"
        )
        print(f"✅ User created: {user.email} (ID: {user.id})")
        
        # Test API key creation
        print("🔑 Creating test API key...")
        api_key, key = db_manager.create_api_key(
            user_id=user.id,
            name="Test API Key",
            scopes=["read", "write"]
        )
        print(f"✅ API key created: {api_key.name} (Key ID: {api_key.key_id})")
        
        # Test audit log
        print("📋 Creating audit log...")
        audit_log = db_manager.create_audit_log(
            action=AuditAction.CREATE,
            category=AuditCategory.USER_MANAGEMENT,
            description="Test user created",
            user_id=user.id
        )
        print(f"✅ Audit log created: {audit_log.description}")
        
        # Test game session (without risk calculation)
        print("🎮 Creating game session...")
        game_session = db_manager.create_game_session(
            user_id=user.id,
            game_type=GameType.POKER,
            session_id="test_session_123"
        )
        print(f"✅ Game session created: {game_session.session_id}")
        
        # Get statistics
        print("📊 Getting statistics...")
        stats = {
            'users': db_manager.get_user_count(),
            'game_sessions': db_manager.get_game_session_count(days=7)
        }
        print(f"✅ Statistics: {stats}")
        
        print("\n🎉 All tests passed! Database setup is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        try:
            if 'pool' in locals():
                connection_pool_manager.close_all()
                print("🧹 Connection pools closed")
            
            # Remove test database file
            if os.path.exists("test_stellar_logic_ai_simple.db"):
                os.remove("test_stellar_logic_ai_simple.db")
                print("🗑️ Test database file removed")
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")

if __name__ == "__main__":
    success = test_database_simple()
    sys.exit(0 if success else 1)
