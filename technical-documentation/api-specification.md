# Helm AI API Specification

## 🛡️ API Overview

Helm AI provides a RESTful API for integrating our multi-modal anti-cheat detection system into gaming applications. The API supports real-time detection, batch analysis, and comprehensive reporting.

### Base URL
```
Production: https://api.helm-ai.com/v1
Development: https://dev-api.helm-ai.com/v1
```

### Authentication
All API requests require authentication using Bearer tokens:

```http
Authorization: Bearer your-api-key-here
```

## 📊 API Endpoints

### Detection Endpoints

#### POST /detect/image
Analyze uploaded image for cheating indicators.

**Request:**
```http
POST /detect/image
Content-Type: multipart/form-data
Authorization: Bearer {api-key}
```

**Parameters:**
- `image` (file, required): Image file to analyze (PNG, JPG, JPEG)
- `game_id` (string, optional): Game identifier for context
- `user_id` (string, optional): User identifier for tracking

**Response:**
```json
{
  "success": true,
  "detection_id": "det_123456789",
  "timestamp": "2024-01-29T12:00:00Z",
  "results": {
    "prediction": 2,
    "risk_level": "Cheating Detected",
    "confidence": 0.95,
    "features": {
      "unusual_overlays": true,
      "suspicious_patterns": true,
      "third_party_software": false,
      "screen_manipulation": true,
      "aim_assistance": true
    },
    "processing_time": 0.15
  }
}
```

#### POST /detect/audio
Analyze audio data for cheating indicators.

**Request:**
```http
POST /detect/audio
Content-Type: multipart/form-data
Authorization: Bearer {api-key}
```

**Parameters:**
- `audio` (file, required): Audio file to analyze (MP3, WAV, M4A)
- `game_id` (string, optional): Game identifier
- `user_id` (string, optional): User identifier

**Response:**
```json
{
  "success": true,
  "detection_id": "det_123456790",
  "timestamp": "2024-01-29T12:00:00Z",
  "results": {
    "prediction": 1,
    "risk_level": "Suspicious",
    "confidence": 0.78,
    "features": {
      "voice_stress": 0.65,
      "background_noise": 0.45,
      "suspicious_patterns": 0.72
    },
    "processing_time": 0.08
  }
}
```

#### POST /detect/network
Analyze network traffic patterns for cheating indicators.

**Request:**
```http
POST /detect/network
Content-Type: application/json
Authorization: Bearer {api-key}
```

**Parameters:**
```json
{
  "game_id": "game_123",
  "user_id": "user_456",
  "network_data": {
    "packet_count": 1500,
    "average_latency": 45,
    "packet_loss": 0.02,
    "connection_patterns": [...],
    "timing_irregularities": [...]
  }
}
```

**Response:**
```json
{
  "success": true,
  "detection_id": "det_123456791",
  "timestamp": "2024-01-29T12:00:00Z",
  "results": {
    "prediction": 0,
    "risk_level": "Safe",
    "confidence": 0.92,
    "features": {
      "packet_anomalies": 0.15,
      "timing_irregularities": 0.08,
      "suspicious_connections": 0.12
    },
    "processing_time": 0.05
  }
}
```

#### POST /detect/multi-modal
Comprehensive analysis using all detection methods.

**Request:**
```http
POST /detect/multi-modal
Content-Type: multipart/form-data
Authorization: Bearer {api-key}
```

**Parameters:**
- `image` (file, optional): Screenshot to analyze
- `audio` (file, optional): Audio data to analyze
- `network_data` (json, optional): Network traffic data
- `game_id` (string, optional): Game identifier
- `user_id` (string, optional): User identifier

**Response:**
```json
{
  "success": true,
  "detection_id": "det_123456792",
  "timestamp": "2024-01-29T12:00:00Z",
  "results": {
    "overall_prediction": 2,
    "overall_risk_level": "Cheating Detected",
    "overall_confidence": 0.89,
    "modal_results": {
      "vision": {
        "prediction": 2,
        "confidence": 0.95,
        "risk_level": "Cheating Detected"
      },
      "audio": {
        "prediction": 1,
        "confidence": 0.78,
        "risk_level": "Suspicious"
      },
      "network": {
        "prediction": 0,
        "confidence": 0.92,
        "risk_level": "Safe"
      }
    },
    "processing_time": 0.25
  }
}
```

### Management Endpoints

#### GET /detections/{detection_id}
Retrieve detailed results for a specific detection.

**Response:**
```json
{
  "success": true,
  "detection": {
    "id": "det_123456789",
    "timestamp": "2024-01-29T12:00:00Z",
    "game_id": "game_123",
    "user_id": "user_456",
    "type": "image",
    "results": {...},
    "status": "completed"
  }
}
```

#### GET /detections
List detections with filtering and pagination.

**Parameters:**
- `game_id` (string, optional): Filter by game
- `user_id` (string, optional): Filter by user
- `start_date` (string, optional): Start date filter
- `end_date` (string, optional): End date filter
- `limit` (integer, optional): Results per page (default: 50)
- `offset` (integer, optional): Pagination offset

**Response:**
```json
{
  "success": true,
  "detections": [...],
  "pagination": {
    "total": 1250,
    "limit": 50,
    "offset": 0,
    "has_more": true
  }
}
```

#### GET /analytics
Get analytics and reporting data.

**Parameters:**
- `game_id` (string, optional): Filter by game
- `period` (string, optional): Time period (day, week, month, year)
- `metrics` (array, optional): Specific metrics to return

**Response:**
```json
{
  "success": true,
  "analytics": {
    "total_detections": 15420,
    "cheating_detected": 1847,
    "suspicious": 2341,
    "safe": 11232,
    "accuracy": 0.96,
    "false_positive_rate": 0.04,
    "average_processing_time": 0.12,
    "trends": {
      "daily": [...],
      "weekly": [...],
      "monthly": [...]
    }
  }
}
```

## 🔧 Configuration Endpoints

#### GET /config
Get current API configuration.

**Response:**
```json
{
  "success": true,
  "config": {
    "rate_limits": {
      "requests_per_minute": 1000,
      "requests_per_hour": 50000
    },
    "supported_formats": {
      "image": ["png", "jpg", "jpeg"],
      "audio": ["mp3", "wav", "m4a"]
    },
    "max_file_size": {
      "image": 10485760,
      "audio": 52428800
    }
  }
}
```

#### PUT /config
Update configuration (admin only).

## 🚨 Error Handling

### Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "INVALID_API_KEY",
    "message": "The provided API key is invalid or expired",
    "details": {
      "request_id": "req_123456789",
      "timestamp": "2024-01-29T12:00:00Z"
    }
  }
}
```

### Error Codes
- `INVALID_API_KEY`: API key is invalid or expired
- `RATE_LIMIT_EXCEEDED`: Rate limit exceeded
- `INVALID_FILE_FORMAT`: Unsupported file format
- `FILE_TOO_LARGE`: File exceeds size limit
- `MISSING_REQUIRED_PARAMETER`: Required parameter missing
- `PROCESSING_ERROR`: Error during detection processing
- `SERVER_ERROR`: Internal server error

## 🔄 Webhooks

### Configure Webhooks
Set up webhooks to receive real-time notifications:

```http
POST /webhooks
Content-Type: application/json
Authorization: Bearer {api-key}
```

**Parameters:**
```json
{
  "url": "https://your-domain.com/webhook",
  "events": ["detection.completed", "detection.failed"],
  "secret": "your-webhook-secret"
}
```

### Webhook Payload
```json
{
  "event": "detection.completed",
  "timestamp": "2024-01-29T12:00:00Z",
  "data": {
    "detection_id": "det_123456789",
    "game_id": "game_123",
    "user_id": "user_456",
    "results": {...}
  }
}
```

## 📈 Rate Limits

### Standard Limits
- **Requests per minute**: 1,000
- **Requests per hour**: 50,000
- **Requests per day**: 1,000,000

### Rate Limit Headers
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640784000
```

## 🧪 SDKs and Libraries

### Python SDK
```python
from helm_ai import HelmAI

client = HelmAI(api_key="your-api-key")

# Image detection
result = client.detect_image(
    image_path="screenshot.png",
    game_id="my_game"
)

# Multi-modal detection
result = client.detect_multi_modal(
    image_path="screenshot.png",
    audio_path="audio.wav",
    game_id="my_game"
)
```

### JavaScript SDK
```javascript
import { HelmAI } from 'helm-ai-js';

const client = new HelmAI('your-api-key');

// Image detection
const result = await client.detectImage({
  image: file,
  gameId: 'my_game'
});

// Multi-modal detection
const result = await client.detectMultiModal({
  image: file,
  audio: file,
  gameId: 'my_game'
});
```

## 🔒 Security

### API Key Security
- Keep API keys confidential
- Use environment variables for storage
- Rotate keys regularly
- Monitor usage for anomalies

### Data Privacy
- All data is encrypted in transit
- Data retention policies apply
- GDPR and CCPA compliant
- Optional data deletion available

## 📋 Integration Examples

### Unity Integration
```csharp
using UnityEngine;
using HelmAI;

public class AntiCheatManager : MonoBehaviour
{
    private HelmAIClient client;
    
    void Start()
    {
        client = new HelmAIClient("your-api-key");
    }
    
    public async void AnalyzeScreenshot()
    {
        var screenshot = CaptureScreenshot();
        var result = await client.DetectImageAsync(screenshot);
        
        if (result.RiskLevel == "Cheating Detected")
        {
            // Handle cheating detection
            HandleCheating(result);
        }
    }
}
```

### Unreal Engine Integration
```cpp
#include "HelmAI.h"
#include "Engine/Engine.h"

void UAntiCheatComponent::AnalyzeScreenshot()
{
    UHelmAIClient* Client = NewObject<UHelmAIClient>();
    Client->Initialize("your-api-key");
    
    TArray<uint8> ScreenshotData = CaptureScreenshot();
    
    Client->DetectImage(ScreenshotData, 
        FHelmAIDetectionDelegate::CreateUObject(this, 
            &UAntiCheatComponent::OnDetectionComplete));
}
```

## 🎯 Best Practices

### Performance Optimization
- Batch multiple detections when possible
- Use appropriate image compression
- Implement client-side caching
- Monitor API usage and optimize

### Error Handling
- Implement exponential backoff for retries
- Log errors for debugging
- Provide fallback mechanisms
- Monitor error rates

### Security
- Validate all inputs
- Use HTTPS for all requests
- Implement proper authentication
- Monitor for unusual usage patterns

---

## 📞 Support

### Documentation
- [API Reference](https://docs.helm-ai.com/api)
- [SDK Documentation](https://docs.helm-ai.com/sdk)
- [Integration Guides](https://docs.helm-ai.com/integration)

### Contact
- **Email**: api-support@helm-ai.com
- **Status Page**: https://status.helm-ai.com
- **Community**: https://community.helm-ai.com

---

**🛡️ Helm AI - Advanced Anti-Cheat Detection API**
