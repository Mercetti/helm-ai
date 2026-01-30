import requests
import json

test_inputs = [
    'Hello, what can you help me with?',
    'Generate business plan',
    'What is 2+2?',
    'Tell me about Stellar Logic AI',
    'Help me with investor outreach',
    'Random text: asdfghjkl',
    'Empty input test',
    'Very long message: ' + 'test ' * 100
]

for i, test_input in enumerate(test_inputs):
    try:
        response = requests.post('http://localhost:5001/api/chat', 
                               json={'message': test_input}, 
                               timeout=30)
        print(f'Test {i+1}: Status {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'Response: {data["response"][:100]}...')
        else:
            print(f'Error: {response.text}')
        print('-' * 50)
    except Exception as e:
        print(f'Test {i+1} Error: {e}')
        print('-' * 50)
