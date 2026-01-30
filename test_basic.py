#!/usr/bin/env python3
"""
Very simple database test
"""

import sys
import os
sys.path.append('src')

def test_basic():
    """Basic test"""
    print("🚀 Testing Basic Database Functionality")
    print("=" * 50)
    
    try:
        # Test imports
        print("📦 Testing imports...")
        from models import User, APIKey, AuditLog, GameSession
        from models.user import UserRole
        from models.api_key import APIKeyScope, APIKeyStatus
        from models.audit_log import AuditAction, AuditCategory
        from models.game_session import GameType
        print("✅ All imports successful")
        
        # Test enum values
        print("🔧 Testing enum values...")
        print(f"✅ UserRole.USER = {UserRole.USER}")
        print(f"✅ APIKeyStatus.ACTIVE = {APIKeyStatus.ACTIVE}")
        print(f"✅ AuditAction.CREATE = {AuditAction.CREATE}")
        print(f"✅ GameType.POKER = {GameType.POKER}")
        
        print("\n🎉 Basic tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_basic()
    sys.exit(0 if success else 1)
