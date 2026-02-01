
"""
Simple UTF-8 Encoding Test
Tests basic Unicode functionality
"""

def test_unicode_handling():
    """Test basic Unicode handling"""
    
    # Test special characters
    test_strings = [
        'Hello World',
        'Hola Mundo',
        'Bonjour le Monde',
        '你好世界',
        'العربية',
        'Security 🔒🛡️🔐',
        'Patient: José García',
        'Currency: $100 €100 £100 ¥100'
    ]
    
    print("Testing Unicode string handling...")
    
    for test_str in test_strings:
        try:
            # Test encoding
            encoded = test_str.encode('utf-8', errors='ignore')
            decoded = encoded.decode('utf-8', errors='ignore')
            
            if decoded == test_str:
                print(f"✅ {test_str}")
            else:
                print(f"❌ {test_str} -> {decoded}")
                
        except Exception as e:
            print(f"❌ Error with {test_str}: {e}")
    
    # Test file operations
    print("\nTesting file operations...")
    
    test_data = {
        'multilingual': {
            'english': 'Security System',
            'spanish': 'Sistema de Seguridad',
            'chinese': '安全系统',
            'arabic': 'نظام الأمان',
            'emoji': '🤖🔒🛡️'
        }
    }
    
    try:
        # Write test file
        with open('unicode_test.json', 'w', encoding='utf-8') as f:
            import json
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        # Read test file
        with open('unicode_test.json', 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        print("✅ File operations successful")
        
        # Clean up
        os.remove('unicode_test.json')
        
    except Exception as e:
        print(f"❌ File operations failed: {e}")

if __name__ == '__main__':
    test_unicode_handling()
    print("\n🎯 Unicode encoding test completed!")
