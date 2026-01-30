import requests
import json

# Test specific business-related questions
test_inputs = [
    'What is Sarah Chen\'s email address?',
    'Generate an email to Sarah Chen',
    'What is our funding goal?',
    'Tell me about our anti-cheat technology',
    'How accurate is our technology?',
    'Who are our target investors?',
    'Create a pitch for Andreessen Horowitz',
    'What stage are we at?'
]

for i, test_input in enumerate(test_inputs):
    try:
        response = requests.post('http://localhost:5001/api/chat', 
                               json={'message': test_input}, 
                               timeout=30)
        print(f'Test {i+1}: "{test_input}"')
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'Response: {data["response"]}')
        else:
            print(f'Error: {response.text}')
        print('=' * 80)
    except Exception as e:
        print(f'Test {i+1} Error: {e}')
        print('=' * 80)
