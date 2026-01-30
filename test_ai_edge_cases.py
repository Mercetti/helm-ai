import requests
import json

# Test edge cases and different input types
test_inputs = [
    '',  # Empty input
    '   ',  # Whitespace only
    'help',  # Single word
    'What is 2+2?',  # Math question
    'Tell me a joke',  # Non-business request
    'Who are you?',  # Identity question
    'Generate email to investor',  # Vague request
    'Research market size',  # Research request
    'Create document',  # Document request
    'Schedule meeting',  # Meeting request
    'asdfghjklqwerttyuiop',  # Gibberish
    'CAPITAL LETTERS TEST',  # All caps
    '123456789',  # Numbers only
    'Test with special chars: !@#$%^&*()',  # Special characters
    'Very short',
    'This is a very long message to test how the AI handles extended input and whether it provides appropriate responses for lengthy queries that might contain multiple questions or complex requests that require detailed analysis and comprehensive answers to ensure the system can handle various input lengths and complexities effectively.'
]

for i, test_input in enumerate(test_inputs):
    try:
        response = requests.post('http://localhost:5001/api/chat', 
                               json={'message': test_input}, 
                               timeout=30)
        print(f'Test {i+1}: "{test_input[:50]}{"..." if len(test_input) > 50 else ""}"')
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            response_text = data["response"]
            print(f'Response Length: {len(response_text)} chars')
            print(f'Response: {response_text[:200]}{"..." if len(response_text) > 200 else ""}')
        else:
            print(f'Error: {response.text}')
        print('-' * 60)
    except Exception as e:
        print(f'Test {i+1} Error: {e}')
        print('-' * 60)
