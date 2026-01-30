#!/usr/bin/env python3
"""
Test script to verify static file serving
"""

import requests
import time

def test_static_files():
    """Test if static files are served correctly"""
    base_url = "http://localhost:5000"
    
    files_to_test = [
        '/Stellar_Logic_AI_Logo.png',
        '/favicon_32x32.png',
        '/favicon_16x16.png',
        '/favicon.ico'
    ]
    
    print("🧪 Testing Static File Serving...")
    print("=" * 50)
    
    for file_path in files_to_test:
        url = base_url + file_path
        try:
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', 'unknown')
                size = len(response.content)
                print(f"✅ {file_path}: {response.status_code} - {content_type} - {size} bytes")
            else:
                print(f"❌ {file_path}: {response.status_code} - {response.text[:100]}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {file_path}: Connection error - {e}")
    
    print("\n🎯 Test completed!")

if __name__ == "__main__":
    test_static_files()
