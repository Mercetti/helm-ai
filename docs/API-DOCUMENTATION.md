# 📚 Helm AI API Documentation

## 🛡️ Overview

Helm AI provides a comprehensive REST API for AI governance, safety, and constitutional AI capabilities. This documentation covers all available endpoints, authentication, and integration patterns.

## 🔗 Base URL

```
Development: http://localhost:3001/api
Production: https://api.helm-ai.com/v1
```

## 📋 Authentication

### **🔑 API Key Authentication**
```http
Authorization: Bearer YOUR_API_KEY
X-API-Key: YOUR_API_KEY
```

### **🛡️ Enterprise Authentication**
```http
Authorization: Helm-Enterprise ENTERPRISE_TOKEN
X-Enterprise-ID: YOUR_ENTERPRISE_ID
```

## 📡 Core Endpoints

### **🔍 Health Check**
```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "Helm AI",
  "timestamp": "2026-01-28T20:30:00.000Z",
  "version": "1.0.0",
  "uptime": 3600
}
```

### **🧠 LLM Development Analysis**
```http
GET /api/ai/llm-development
```

**Response:**
```json
{
  "success": true,
  "data": {
    "developmentPhases": {
      "foundation": {
        "name": "Foundation Phase",
        "duration": "6-12 months",
        "progress": 25
      }
    },
    "dependencyReduction": {
      "currentDependencies": [
        {
          "name": "External LLM APIs",
          "impact": "High",
          "replacementStrategy": "Develop proprietary LLM"
        }
      ]
    }
  }
}
```

### **🛡️ Safety Governance**
```http
GET /api/ai/safety-governance
```

**Response:**
```json
{
  "success": true,
  "data": {
    "constitutionalPrinciples": [
      "safety_first",
      "human_oversight",
      "transparency",
      "accountability"
    ],
    "governanceLayers": [
      "input_validation",
      "constitutional_constraints",
      "safety_checks",
      "human_approval"
    ]
  }
}
```

### **💎 Valuation Analysis**
```http
GET /api/ai/valuation
```

**Response:**
```json
{
  "success": true,
  "data": {
    "totalValuation": 12500000000,
    "marketSize": 50000000000,
    "growthRate": 0.35,
    "components": {
      "coreAI": 8000000000,
      "advancedCapabilities": 2500000000,
      "learningEnhancement": 1000000000,
      "safetyGovernance": 1000000000
    }
  }
}
```

## 🎮 Integration Endpoints

### **🎯 Player Behavior Analysis**
```http
POST /api/integration/player-behavior
```

**Request Body:**
```json
{
  "playerId": "player_123",
  "action": "raise",
  "amount": 100,
  "timestamp": "2026-01-28T20:30:00.000Z",
  "context": {
    "gameType": "texas_holdem",
    "blinds": [10, 20],
    "potSize": 500
  }
}
```

**Response:**
```json
{
  "success": true,
  "analysis": {
    "riskLevel": "low",
    "behaviorPattern": "aggressive",
    "recommendations": [
      "Monitor for unusual betting patterns",
      "Consider player profiling"
    ],
    "confidence": 0.85
  }
}
```

### **🛡️ Security Threat Detection**
```http
POST /api/integration/security-threat
```

**Request Body:**
```json
{
  "input": "system('rm -rf /')",
  "context": "user_input_validation",
  "severity": "critical",
  "source": "poker_game"
}
```

**Response:**
```json
{
  "success": true,
  "threatDetected": true,
  "riskLevel": "critical",
  "threatType": "command_injection",
  "mitigation": "Input blocked and logged",
  "recommendations": [
    "Implement input sanitization",
    "Add rate limiting"
  ]
}
```

### **🎯 Game Event Analysis**
```http
POST /api/integration/game-event
```

**Request Body:**
```json
{
  "eventType": "tournament_start",
  "tournamentId": "tournament_456",
  "playerCount": 50,
  "timestamp": "2026-01-28T20:30:00.000Z",
  "metadata": {
    "buyIn": 100,
    "prizePool": 5000,
    "duration": "4_hours"
  }
}
```

## 🛡️ Constitutional AI Endpoints

### **📋 Constitutional Principles**
```http
POST /api/constitutional/principles
```

**Request Body:**
```json
{
  "framework": "helm_ai_constitutional",
  "principles": ["safety_first", "human_oversight"],
  "context": "enterprise_ai_governance"
}
```

### **🔗 Governance Layers**
```http
POST /api/constitutional/governance-layers
```

**Request Body:**
```json
{
  "layers": ["input_validation", "constitutional_constraints"],
  "activeLayer": "constitutional_constraints",
  "governanceMode": "enterprise"
}
```

### **⚠️ Safety Constraints**
```http
POST /api/constitutional/safety-constraints
```

**Request Body:**
```json
{
  "constraintType": "constitutional_safety",
  "enabledConstraints": ["no_harm_principle", "human_control"],
  "riskLevel": "enterprise_grade",
  "auditTrail": true
}
```

## 📊 Error Handling

### **🔍 Standard Error Response**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": {
      "field": "playerId",
      "reason": "Required field missing"
    }
  },
  "timestamp": "2026-01-28T20:30:00.000Z"
}
```

### **🛡️ Security Error Response**
```json
{
  "success": false,
  "error": {
    "code": "SECURITY_VIOLATION",
    "message": "Input blocked due to security policy",
    "threatLevel": "high"
  }
}
```

## 📈 Rate Limiting

### **🎯 Rate Limits**
```
Free Tier: 100 requests/hour
Professional: 1000 requests/hour
Enterprise: 10000 requests/hour
```

### **📊 Rate Limit Headers**
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1643328600
```

## 🚀 SDK Integration

### **📱 JavaScript SDK**
```javascript
import { HelmAI } from '@helm-ai/sdk';

const helmAI = new HelmAI({
  apiKey: 'YOUR_API_KEY',
  baseUrl: 'http://localhost:3001/api'
});

// Analyze player behavior
const analysis = await helmAI.analyzePlayerBehavior({
  playerId: 'player_123',
  action: 'raise',
  amount: 100
});

// Detect security threats
const threat = await helmAI.detectSecurityThreat({
  input: userInput,
  context: 'game_input'
});
```

### **🐍 Python SDK**
```python
from helm_ai import HelmAI

helm = HelmAI(api_key='YOUR_API_KEY')

# Analyze player behavior
analysis = helm.analyze_player_behavior(
    player_id='player_123',
    action='raise',
    amount=100
)

# Detect security threats
threat = helm.detect_security_threat(
    input=user_input,
    context='game_input'
)
```

## 🛡️ Security Best Practices

### **🔑 API Key Management**
- Store API keys securely
- Rotate keys regularly
- Use environment variables
- Implement key rotation policies

### **📊 Input Validation**
- Always validate input data
- Sanitize user inputs
- Implement rate limiting
- Monitor for abuse patterns

### **🔒 HTTPS Required**
- Use HTTPS in production
- Implement TLS 1.3
- Use certificate pinning
- Monitor SSL certificates

## 📞 Support

### **🎯 Technical Support**
- Email: support@helm-ai.com
- Documentation: https://docs.helm-ai.com
- Status Page: https://status.helm-ai.com

### **🛡️ Security Issues**
- Email: security@helm-ai.com
- Responsible Disclosure Policy
- Bug Bounty Program

---

*Complete API documentation for $12B+ AI governance platform*
