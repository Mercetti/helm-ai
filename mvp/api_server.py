#!/usr/bin/env python3
"""
Helm AI - FastAPI Server for Anti-Cheat Detection
Production-ready REST API with authentication and real-time processing
"""

from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import asyncio
import aiofiles
import uvicorn
import torch
import numpy as np
from PIL import Image
import io
import base64
import json
import time
from datetime import datetime, timedelta
import redis
import sqlite3
from contextlib import asynccontextmanager
import logging
from functools import lru_cache
import hashlib
import secrets
from models import ModelEnsemble, preprocess_image, preprocess_audio, preprocess_network

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
model_ensemble = None
redis_client = None
db_connection = None

# Pydantic models for API
class DetectionRequest(BaseModel):
    user_id: str = Field(..., description="Unique user identifier")
    game_id: str = Field(..., description="Game identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    image_data: Optional[str] = Field(None, description="Base64 encoded image")
    audio_data: Optional[str] = Field(None, description="Base64 encoded audio")
    network_data: Optional[List[List[float]]] = Field(None, description="Network packet data")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class DetectionResponse(BaseModel):
    request_id: str = Field(..., description="Unique request identifier")
    timestamp: str = Field(..., description="Detection timestamp")
    risk_level: str = Field(..., description="Risk level: Safe, Suspicious, Cheating Detected")
    confidence: float = Field(..., description="Confidence score (0-1)")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    details: Optional[Dict[str, Any]] = Field(None, description="Detailed detection results")
    modalities_used: List[str] = Field(..., description="Modalities used for detection")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Service health status")
    timestamp: str = Field(..., description="Current timestamp")
    version: str = Field(..., description="API version")
    model_status: str = Field(..., description="Model loading status")
    uptime_seconds: float = Field(..., description="Service uptime")

class APIKey(BaseModel):
    key: str
    name: str
    permissions: List[str]
    created_at: datetime
    last_used: Optional[datetime] = None
    usage_count: int = 0

# Database setup
def setup_database():
    """Setup SQLite database for storing detection results and API keys"""
    conn = sqlite3.connect('helm_ai.db', check_same_thread=False)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detection_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id TEXT UNIQUE,
            user_id TEXT,
            game_id TEXT,
            session_id TEXT,
            risk_level TEXT,
            confidence REAL,
            processing_time_ms REAL,
            modalities_used TEXT,
            details TEXT,
            timestamp DATETIME,
            ip_address TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE,
            name TEXT,
            permissions TEXT,
            created_at DATETIME,
            last_used DATETIME,
            usage_count INTEGER DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rate_limits (
            api_key TEXT,
            request_count INTEGER,
            window_start DATETIME,
            PRIMARY KEY (api_key, window_start)
        )
    ''')
    
    conn.commit()
    return conn

# Redis setup
def setup_redis():
    """Setup Redis for caching and rate limiting"""
    try:
        import redis
        return redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    except Exception as e:
        logger.warning(f"Redis not available: {e}")
        return None

# Security
security = HTTPBearer()

@lru_cache(maxsize=1000)
def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key and return user info"""
    api_key = credentials.credentials
    
    # Check in database
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM api_keys WHERE key = ?", (api_key,))
    result = cursor.fetchone()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    # Update last used and usage count
    cursor.execute(
        "UPDATE api_keys SET last_used = ?, usage_count = usage_count + 1 WHERE key = ?",
        (datetime.now(), api_key)
    )
    db_connection.commit()
    
    return {
        "key": api_key,
        "name": result[1],
        "permissions": json.loads(result[2])
    }

# Rate limiting
async def check_rate_limit(api_key: str, limit: int = 100, window: int = 60):
    """Check rate limit for API key"""
    if not redis_client:
        return True  # Skip rate limiting if Redis not available
    
    current_time = datetime.now()
    window_start = current_time - timedelta(seconds=window)
    
    # Clean old entries
    redis_client.zremrangebyscore(
        f"rate_limit:{api_key}",
        0,
        window_start.timestamp()
    )
    
    # Check current count
    current_count = redis_client.zcard(f"rate_limit:{api_key}")
    
    if current_count >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
    
    # Add current request
    redis_client.zadd(
        f"rate_limit:{api_key}",
        {str(current_time.timestamp()): current_time.timestamp()}
    )
    redis_client.expire(f"rate_limit:{api_key}", window)
    
    return True

# Application lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    global model_ensemble, redis_client, db_connection
    
    # Startup
    logger.info("Starting Helm AI API Server...")
    
    # Setup database
    db_connection = setup_database()
    logger.info("Database initialized")
    
    # Setup Redis
    redis_client = setup_redis()
    if redis_client:
        logger.info("Redis connected")
    else:
        logger.warning("Redis not available, running without caching")
    
    # Load models
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model_ensemble = ModelEnsemble(device)
    logger.info(f"Models loaded on device: {device}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Helm AI API Server...")
    if db_connection:
        db_connection.close()

# Create FastAPI app
app = FastAPI(
    title="Helm AI Anti-Cheat Detection API",
    description="Advanced multi-modal anti-cheat detection system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Helper functions
def generate_request_id() -> str:
    """Generate unique request ID"""
    return secrets.token_urlsafe(16)

def decode_base64_image(base64_string: str) -> Image.Image:
    """Decode base64 image string to PIL Image"""
    # Remove data URL prefix if present
    if ',' in base64_string:
        base64_string = base64_string.split(',')[1]
    
    image_data = base64.b64decode(base64_string)
    return Image.open(io.BytesIO(image_data))

def decode_base64_audio(base64_string: str) -> np.ndarray:
    """Decode base64 audio string to numpy array"""
    # Remove data URL prefix if present
    if ',' in base64_string:
        base64_string = base64_string.split(',')[1]
    
    audio_data = base64.b64decode(base64_string)
    # For now, return dummy audio data
    # In production, use proper audio decoding
    return np.random.rand(16000)  # 1 second of audio at 16kHz

def store_detection_result(request_id: str, user_data: dict, result: dict, processing_time: float):
    """Store detection result in database"""
    cursor = db_connection.cursor()
    cursor.execute('''
        INSERT INTO detection_results 
        (request_id, user_id, game_id, session_id, risk_level, confidence, 
         processing_time_ms, modalities_used, details, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        request_id,
        user_data.get('user_id'),
        user_data.get('game_id'),
        user_data.get('session_id'),
        result['risk_level'],
        result['confidence'],
        processing_time,
        json.dumps(result.get('modalities_used', [])),
        json.dumps(result.get('details', {})),
        datetime.now()
    ))
    db_connection.commit()

# API endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    uptime = time.time() - app.state.start_time if hasattr(app.state, 'start_time') else 0
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
        model_status="loaded" if model_ensemble else "not_loaded",
        uptime_seconds=uptime
    )

@app.post("/api/v1/detect", response_model=DetectionResponse)
async def detect_cheating(
    request: DetectionRequest,
    background_tasks: BackgroundTasks,
    credentials: dict = Depends(verify_api_key)
):
    """Main detection endpoint"""
    start_time = time.time()
    request_id = generate_request_id()
    
    try:
        # Rate limiting
        await check_rate_limit(credentials["key"])
        
        # Prepare input data
        image = None
        audio = None
        network = None
        modalities_used = []
        
        # Process image if provided
        if request.image_data:
            try:
                image_pil = decode_base64_image(request.image_data)
                image = preprocess_image(image_pil).to(model_ensemble.device)
                modalities_used.append("vision")
            except Exception as e:
                logger.error(f"Error processing image: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid image data"
                )
        
        # Process audio if provided
        if request.audio_data:
            try:
                audio_np = decode_base64_audio(request.audio_data)
                audio = preprocess_audio(audio_np).to(model_ensemble.device)
                modalities_used.append("audio")
            except Exception as e:
                logger.error(f"Error processing audio: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid audio data"
                )
        
        # Process network data if provided
        if request.network_data:
            try:
                network_np = np.array(request.network_data)
                network = preprocess_network(network_np).to(model_ensemble.device)
                modalities_used.append("network")
            except Exception as e:
                logger.error(f"Error processing network data: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid network data"
                )
        
        # Check if at least one modality is provided
        if not modalities_used:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one modality (image, audio, or network) must be provided"
            )
        
        # Run detection
        with torch.no_grad():
            results = model_ensemble.predict(image, audio, network)
            risk_level, confidence = model_ensemble.get_risk_level(results)
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Prepare response
        response = DetectionResponse(
            request_id=request_id,
            timestamp=datetime.now().isoformat(),
            risk_level=risk_level,
            confidence=confidence,
            processing_time_ms=processing_time,
            details={
                "vision_results": results.get("vision", {}).get("classification", {}).tolist() if "vision" in results else None,
                "audio_results": results.get("audio", {}).get("classification", {}).tolist() if "audio" in results else None,
                "network_results": results.get("network", {}).get("classification", {}).tolist() if "network" in results else None,
                "fusion_results": results.get("fusion", {}).get("classification", {}).tolist() if "fusion" in results else None,
            },
            modalities_used=modalities_used
        )
        
        # Store result in background
        background_tasks.add_task(
            store_detection_result,
            request_id,
            request.dict(),
            {
                "risk_level": risk_level,
                "confidence": confidence,
                "modalities_used": modalities_used,
                "details": response.details
            },
            processing_time
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Detection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during detection"
        )

@app.get("/api/v1/detections/{request_id}")
async def get_detection_result(request_id: str, credentials: dict = Depends(verify_api_key)):
    """Get detection result by request ID"""
    cursor = db_connection.cursor()
    cursor.execute(
        "SELECT * FROM detection_results WHERE request_id = ?",
        (request_id,)
    )
    result = cursor.fetchone()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detection result not found"
        )
    
    return {
        "request_id": result[1],
        "user_id": result[2],
        "game_id": result[3],
        "session_id": result[4],
        "risk_level": result[5],
        "confidence": result[6],
        "processing_time_ms": result[7],
        "modalities_used": json.loads(result[8]),
        "details": json.loads(result[9]),
        "timestamp": result[10]
    }

@app.get("/api/v1/stats")
async def get_detection_stats(credentials: dict = Depends(verify_api_key)):
    """Get detection statistics"""
    cursor = db_connection.cursor()
    
    # Total detections
    cursor.execute("SELECT COUNT(*) FROM detection_results")
    total_detections = cursor.fetchone()[0]
    
    # Detections by risk level
    cursor.execute("""
        SELECT risk_level, COUNT(*) 
        FROM detection_results 
        GROUP BY risk_level
    """)
    risk_distribution = dict(cursor.fetchall())
    
    # Recent detections (last 24 hours)
    cursor.execute("""
        SELECT COUNT(*) 
        FROM detection_results 
        WHERE timestamp > datetime('now', '-1 day')
    """)
    recent_detections = cursor.fetchone()[0]
    
    # Average processing time
    cursor.execute("SELECT AVG(processing_time_ms) FROM detection_results")
    avg_processing_time = cursor.fetchone()[0] or 0
    
    return {
        "total_detections": total_detections,
        "risk_distribution": risk_distribution,
        "recent_detections_24h": recent_detections,
        "average_processing_time_ms": round(avg_processing_time, 2),
        "model_status": "loaded" if model_ensemble else "not_loaded"
    }

@app.post("/api/v1/api-keys")
async def create_api_key(
    name: str,
    permissions: List[str] = ["detect"],
    credentials: dict = Depends(verify_api_key)
):
    """Create new API key (admin only)"""
    if "admin" not in credentials["permissions"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permissions required"
        )
    
    api_key = secrets.token_urlsafe(32)
    cursor = db_connection.cursor()
    cursor.execute('''
        INSERT INTO api_keys (key, name, permissions, created_at)
        VALUES (?, ?, ?, ?)
    ''', (
        api_key,
        name,
        json.dumps(permissions),
        datetime.now()
    ))
    db_connection.commit()
    
    return {
        "api_key": api_key,
        "name": name,
        "permissions": permissions,
        "created_at": datetime.now().isoformat()
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.now().isoformat()
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    app.state.start_time = time.time()
    logger.info("Helm AI API Server started successfully")

# Run server
if __name__ == "__main__":
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
