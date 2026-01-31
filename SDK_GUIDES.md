# SDK Guides

## Overview
Complete SDK documentation for Python, JavaScript, Java, and Go with integration examples and best practices.

## Python SDK
### Installation
```bash
pip install stellarlogic-ai
```

### Quick Start
```python
from stellarlogic_ai import StellarLogicClient

client = StellarLogicClient(api_key="your-api-key")
result = client.analyze_threat({
    "type": "malware",
    "source": "email",
    "content": "suspicious attachment"
})
```

### Advanced Features
- Async/await support
- Batch processing
- Error handling
- Logging and monitoring

## JavaScript SDK
### Installation
```bash
npm install @stellarlogic-ai/client
```

### Quick Start
```javascript
import { StellarLogicClient } from '@stellarlogic-ai/client';

const client = new StellarLogicClient('your-api-key');
const result = await client.analyzeThreat({
    type: 'malware',
    source: 'email',
    content: 'suspicious attachment'
});
```

### Browser Support
- Modern browsers (Chrome, Firefox, Safari, Edge)
- Node.js backend support
- TypeScript definitions included

## Java SDK
### Installation
```xml
<dependency>
    <groupId>com.stellarlogic</groupId>
    <artifactId>stellarlogic-client</artifactId>
    <version>1.0.0</version>
</dependency>
```

### Quick Start
```java
import com.stellarlogic.client.StellarLogicClient;

StellarLogicClient client = new StellarLogicClient("your-api-key");
ThreatData threatData = new ThreatData("malware", "email", "suspicious");
JsonNode result = client.analyzeThreat(threatData);
```

### Enterprise Features
- Spring Boot integration
- JAX-RS support
- Enterprise security
- Performance optimization

## Go SDK
### Installation
```bash
go get github.com/stellarlogic/go-client
```

### Quick Start
```go
package main

import "github.com/stellarlogic/go-client"
import "github.com/stellarlogic/go-client/types"

func main() {
    client := stellarlogic.NewClient("your-api-key")
    
    threat := &types.ThreatData{
        Type: "malware",
        Source: "email",
        Content: "suspicious attachment",
    }
    
    result, err := client.AnalyzeThreat(threat)
    if err != nil {
        log.Fatal(err)
    }
    
    fmt.Printf("Result: %+v\n", result)
}
```

### Performance Features
- Goroutine support
- Connection pooling
- Context cancellation
- Memory efficiency

## Integration Examples

### Web Application Integration
```python
# Flask web application example
from flask import Flask, request, jsonify
from stellarlogic_ai import StellarLogicClient

app = Flask(__name__)
client = StellarLogicClient(os.environ.get('API_KEY'))

@app.route('/api/analyze', methods=['POST'])
def analyze_threat():
    data = request.get_json()
    result = client.analyze_threat(data)
    return jsonify(result)
```

### Mobile Application Integration
```javascript
// React Native integration
import { StellarLogicClient } from '@stellarlogic-ai/client';

const client = new StellarLogicClient('your-api-key');

export const analyzeThreat = async (threatData) => {
    try {
        const result = await client.analyzeThreat(threatData);
        return result;
    } catch (error) {
        throw error('Analysis failed:', error.message);
    }
};
```

### Enterprise Integration
```java
// Spring Boot integration
@RestController
@RequestMapping("/api/security")
public class SecurityController {
    
    @Autowired
    private StellarLogicClient stellarLogicClient;
    
    @PostMapping("/analyze")
    public ResponseEntity<?> analyzeThreat(@RequestBody ThreatData threat) {
        JsonNode result = stellarLogicClient.analyzeThreat(threat);
        return ResponseEntity.ok(result);
    }
}
```

## Best Practices

### Error Handling
```python
# Python error handling
try:
    result = client.analyze_threat(threat_data)
except StellarLogicAPIError as e:
    logger.error(f"API Error: {e}")
    return None
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return None
```

### Performance Optimization
```python
# Connection pooling and caching
import aiohttp
import asyncio

class OptimizedStellarLogicClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.session = None
        self.cache = {}
    
    async def __aenter__(self):
        connector = aiohttp.TCPConnector(limit=100)
        self.session = aiohttp.ClientSession(connector=connector)
        return self
    
    async def analyze_threat_batch(self, threats):
        tasks = [self.analyze_threat(threat) for threat in threats]
        return await asyncio.gather(*tasks)
```

### Security Best Practices
```python
# Secure API key management
import os
from stellarlogic_ai import StellarLogicClient

# Use environment variables for API keys
client = StellarLogicClient(api_key=os.environ.get('STELLARLOGIC_API_KEY'))

# Implement retry logic with exponential backoff
import time
import random

def analyze_threat_with_retry(threat_data, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.analyze_threat(threat_data)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(wait_time)
```

## Testing and Validation

### Unit Testing
```python
# Python unit tests
import unittest
from unittest.mock import patch
from stellarlogic_ai import StellarLogicClient

class TestStellarLogicClient(unittest.TestCase):
    def setUp(self):
        self.client = StellarLogicClient("test-api-key")
    
    def test_analyze_threat(self):
        threat_data = {
            "type": "malware",
            "source": "test",
            "content": "test content"
        }
        
        result = self.client.analyze_threat(threat_data)
        
        self.assertIn('threat_id', result)
        self.assertIn('analysis_result', result)
        self.assertIsInstance(result['confidence_score'], (int, float))
```

### Integration Testing
```python
# Integration tests
import pytest
import requests

def test_api_integration():
    # Test actual API integration
    response = requests.post(
        'https://api.stellarlogic.ai/v1/threats/analyze',
        headers={'Authorization': 'Bearer test-key'},
        json={'type': 'malware', 'source': 'test', 'content': 'test'}
    )
    
    assert response.status_code == 200
    assert 'threat_id' in response.json()
```

## Documentation and Support

### API Documentation
- Complete API reference
- Code examples for all languages
- Error code documentation
- Rate limiting information
- Authentication guide

### Community Support
- GitHub repository with examples
- Stack Overflow tag monitoring
- Developer Discord community
- Email support for enterprise customers
