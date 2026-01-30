"""
Predictive Analytics for User Behavior for Helm AI
=================================================

This module provides comprehensive predictive analytics capabilities for user behavior:
- User behavior pattern analysis
- Churn prediction and prevention
- User engagement forecasting
- Personalized recommendation predictions
- User journey optimization
- Behavioral segmentation
- Predictive user scoring
- Actionable insights generation
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from pathlib import Path
import numpy as np
import pandas as pd

# Third-party imports
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.cluster import KMeans
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, Boolean, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID, JSONB
import redis

# Local imports
from src.monitoring.structured_logging import StructuredLogger
from src.database.database_manager import DatabaseManager
from src.data_lake.data_lake_manager import DataLakeManager
from src.analytics.user_behavior import BehaviorAnalytics

logger = StructuredLogger("predictive_analytics")

Base = declarative_base()


class PredictionType(str, Enum):
    """Types of predictions"""
    CHURN = "churn"
    ENGAGEMENT = "engagement"
    CONVERSION = "conversion"
    RETENTION = "retention"
    LIFETIME_VALUE = "lifetime_value"
    PRODUCT_USAGE = "product_usage"
    FEATURE_ADOPTION = "feature_adoption"
    SUPPORT_NEED = "support_need"


class ModelType(str, Enum):
    """Types of ML models"""
    LOGISTIC_REGRESSION = "logistic_regression"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    NEURAL_NETWORK = "neural_network"
    CLUSTERING = "clustering"
    TIME_SERIES = "time_series"


class UserSegment(str, Enum):
    """User segmentation categories"""
    POWER_USERS = "power_users"
    REGULAR_USERS = "regular_users"
    CASUAL_USERS = "casual_users"
    AT_RISK = "at_risk"
    NEW_USERS = "new_users"
    DORMANT = "dormant"
    CHURNED = "churned"


@dataclass
class UserBehaviorEvent:
    """User behavior event data"""
    id: str
    user_id: str
    event_type: str
    event_name: str
    timestamp: datetime
    properties: Dict[str, Any] = field(default_factory=dict)
    session_id: Optional[str] = None
    device_type: Optional[str] = None
    location: Optional[str] = None


@dataclass
class PredictionModel:
    """Prediction model configuration"""
    id: str
    name: str
    description: str
    prediction_type: PredictionType
    model_type: ModelType
    features: List[str]
    target_variable: str
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    accuracy_threshold: float = 0.8
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class UserPrediction:
    """User prediction result"""
    id: str
    user_id: str
    model_id: str
    prediction_type: PredictionType
    prediction_value: float
    confidence_score: float
    prediction_label: str
    factors: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


class UserBehaviorEvents(Base):
    """SQLAlchemy model for user behavior events"""
    __tablename__ = "user_behavior_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(String(255), nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    event_type = Column(String(100), nullable=False)
    event_name = Column(String(255), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    session_id = Column(String(255))
    device_type = Column(String(100))
    location = Column(String(255))
    properties = Column(JSONB)


class PredictionModels(Base):
    """SQLAlchemy model for prediction models"""
    __tablename__ = "prediction_models"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(String(255), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    prediction_type = Column(String(50), nullable=False)
    model_type = Column(String(50), nullable=False)
    features = Column(JSONB)
    target_variable = Column(String(100))
    hyperparameters = Column(JSONB)
    accuracy_threshold = Column(Float, default=0.8)
    enabled = Column(Boolean, default=True)
    model_metrics = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserPredictions(Base):
    """SQLAlchemy model for user predictions"""
    __tablename__ = "user_predictions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prediction_id = Column(String(255), nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    model_id = Column(String(255), nullable=False)
    prediction_type = Column(String(50), nullable=False)
    prediction_value = Column(Float, nullable=False)
    confidence_score = Column(Float)
    prediction_label = Column(String(100))
    factors = Column(JSONB)
    recommendations = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)


class PredictiveAnalyticsEngine:
    """Predictive Analytics Engine for User Behavior"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_manager = DatabaseManager(config.get('database', {}))
        self.data_lake = DataLakeManager(config.get('data_lake', {}))
        self.behavior_analytics = BehaviorAnalytics(config.get('behavior_analytics', {}))
        
        # Initialize Redis for caching
        self.redis_client = redis.Redis(**config.get('redis', {}))
        
        # ML models storage
        self.prediction_models: Dict[str, PredictionModel] = {}
        self.trained_models: Dict[str, Any] = {}
        
        logger.info("Predictive Analytics Engine initialized")
    
    async def record_user_event(self, event: UserBehaviorEvent) -> bool:
        """Record a user behavior event"""
        try:
            # Store in database
            event_record = UserBehaviorEvents(
                event_id=event.id,
                user_id=event.user_id,
                event_type=event.event_type,
                event_name=event.event_name,
                timestamp=event.timestamp,
                session_id=event.session_id,
                device_type=event.device_type,
                location=event.location,
                properties=event.properties
            )
            
            session = self.db_manager.get_session()
            try:
                session.add(event_record)
                session.commit()
            finally:
                session.close()
            
            logger.info("User behavior event recorded successfully", 
                       user_id=event.user_id, event_type=event.event_type)
            return True
            
        except Exception as e:
            logger.error("Failed to record user behavior event", 
                        user_id=event.user_id, error=str(e))
            return False
    
    async def create_prediction_model(self, model: PredictionModel) -> bool:
        """Create a new prediction model"""
        try:
            # Validate model configuration
            if not await self._validate_prediction_model(model):
                logger.error("Prediction model validation failed", model_id=model.id)
                return False
            
            # Store model configuration
            self.prediction_models[model.id] = model
            
            # Train model
            await self._train_prediction_model(model)
            
            logger.info("Prediction model created successfully", 
                       model_id=model.id, prediction_type=model.prediction_type.value)
            return True
            
        except Exception as e:
            logger.error("Failed to create prediction model", 
                        model_id=model.id, error=str(e))
            return False
    
    async def _validate_prediction_model(self, model: PredictionModel) -> bool:
        """Validate prediction model configuration"""
        try:
            # Check required fields
            if not model.name or not model.features or not model.target_variable:
                return False
            
            # Validate model type
            if model.model_type not in ModelType:
                return False
            
            # Validate prediction type
            if model.prediction_type not in PredictionType:
                return False
            
            return True
            
        except Exception as e:
            logger.error("Prediction model validation failed", error=str(e))
            return False
    
    async def _train_prediction_model(self, model: PredictionModel):
        """Train prediction model"""
        try:
            # Get training data
            training_data = await self._get_training_data(model)
            
            if training_data.empty:
                raise ValueError("No training data available")
            
            # Prepare features and target
            X = training_data[model.features]
            y = training_data[model.target_variable]
            
            # Handle categorical variables
            X = pd.get_dummies(X, drop_first=True)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train model based on type
            if model.model_type == ModelType.LOGISTIC_REGRESSION:
                trained_model = LogisticRegression(random_state=42)
                trained_model.fit(X_train_scaled, y_train)
            elif model.model_type == ModelType.RANDOM_FOREST:
                trained_model = RandomForestClassifier(
                    n_estimators=100, random_state=42, **model.hyperparameters
                )
                trained_model.fit(X_train_scaled, y_train)
            elif model.model_type == ModelType.GRADIENT_BOOSTING:
                trained_model = GradientBoostingClassifier(
                    random_state=42, **model.hyperparameters
                )
                trained_model.fit(X_train_scaled, y_train)
            else:
                raise ValueError(f"Unsupported model type: {model.model_type}")
            
            # Evaluate model
            y_pred = trained_model.predict(X_test_scaled)
            y_pred_proba = trained_model.predict_proba(X_test_scaled)[:, 1]
            
            metrics = {
                "accuracy": accuracy_score(y_test, y_pred),
                "precision": precision_score(y_test, y_pred, average='weighted'),
                "recall": recall_score(y_test, y_pred, average='weighted'),
                "f1": f1_score(y_test, y_pred, average='weighted'),
                "auc": roc_auc_score(y_test, y_pred_proba)
            }
            
            # Store trained model
            self.trained_models[model.id] = {
                "model": trained_model,
                "scaler": scaler,
                "features": X.columns.tolist(),
                "target_variable": model.target_variable,
                "metrics": metrics,
                "trained_at": datetime.utcnow()
            }
            
            logger.info("Prediction model trained successfully", 
                       model_id=model.id, accuracy=metrics["accuracy"])
            
        except Exception as e:
            logger.error("Failed to train prediction model", 
                        model_id=model.id, error=str(e))
            raise
    
    async def _get_training_data(self, model: PredictionModel) -> pd.DataFrame:
        """Get training data for prediction model"""
        try:
            # Query user behavior events
            session = self.db_manager.get_session()
            try:
                # Get last 6 months of data
                start_date = datetime.utcnow() - timedelta(days=180)
                
                events = session.query(UserBehaviorEvents).filter(
                    UserBehaviorEvents.timestamp >= start_date
                ).all()
            finally:
                session.close()
            
            if not events:
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame([
                {
                    "user_id": e.user_id,
                    "event_type": e.event_type,
                    "event_name": e.event_name,
                    "timestamp": e.timestamp,
                    "device_type": e.device_type,
                    "properties": e.properties
                }
                for e in events
            ])
            
            # Feature engineering based on prediction type
            if model.prediction_type == PredictionType.CHURN:
                df = self._create_churn_features(df)
            elif model.prediction_type == PredictionType.ENGAGEMENT:
                df = self._create_engagement_features(df)
            elif model.prediction_type == PredictionType.CONVERSION:
                df = self._create_conversion_features(df)
            else:
                df = self._create_generic_features(df)
            
            return df
            
        except Exception as e:
            logger.error("Failed to get training data", error=str(e))
            return pd.DataFrame()
    
    def _create_churn_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create features for churn prediction"""
        try:
            # Group by user
            user_features = []
            
            for user_id, user_data in df.groupby('user_id'):
                features = {
                    "user_id": user_id,
                    "total_events": len(user_data),
                    "unique_days": user_data['timestamp'].dt.date.nunique(),
                    "avg_events_per_day": len(user_data) / max(user_data['timestamp'].dt.date.nunique(), 1),
                    "last_event_days": (datetime.utcnow() - user_data['timestamp'].max()).days,
                    "event_types": user_data['event_type'].nunique(),
                    "error_events": len(user_data[user_data['event_type'] == 'error']),
                    "error_rate": len(user_data[user_data['event_type'] == 'error']) / len(user_data)
                }
                
                # Target variable (churned if no activity in last 30 days)
                features["churned"] = 1 if features["last_event_days"] > 30 else 0
                
                user_features.append(features)
            
            return pd.DataFrame(user_features)
            
        except Exception as e:
            logger.error("Failed to create churn features", error=str(e))
            return pd.DataFrame()
    
    def _create_engagement_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create features for engagement prediction"""
        try:
            user_features = []
            
            for user_id, user_data in df.groupby('user_id'):
                features = {
                    "user_id": user_id,
                    "total_events": len(user_data),
                    "unique_event_types": user_data['event_type'].nunique(),
                    "session_diversity": user_data['session_id'].nunique() if 'session_id' in user_data.columns else 1,
                    "weekend_activity": len(user_data[user_data['timestamp'].dt.weekday >= 5]),
                    "business_hours_activity": len(user_data[
                        (user_data['timestamp'].dt.hour >= 9) & 
                        (user_data['timestamp'].dt.hour <= 17)
                    ])
                }
                
                # Engagement level (target variable)
                if len(user_data) >= 50:
                    features["high_engagement"] = 1
                else:
                    features["high_engagement"] = 0
                
                user_features.append(features)
            
            return pd.DataFrame(user_features)
            
        except Exception as e:
            logger.error("Failed to create engagement features", error=str(e))
            return pd.DataFrame()
    
    def _create_conversion_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create features for conversion prediction"""
        try:
            user_features = []
            
            for user_id, user_data in df.groupby('user_id'):
                features = {
                    "user_id": user_id,
                    "total_events": len(user_data),
                    "days_active": user_data['timestamp'].dt.date.nunique(),
                    "feature_events": len(user_data[
                        user_data['event_name'].str.contains('feature_', case=False, na=False)
                    ]),
                    "conversion_events": len(user_data[
                        user_data['event_type'].str.contains('conversion', case=False, na=False)
                    ])
                }
                
                # Conversion target
                features["converted"] = 1 if features["conversion_events"] > 0 else 0
                
                user_features.append(features)
            
            return pd.DataFrame(user_features)
            
        except Exception as e:
            logger.error("Failed to create conversion features", error=str(e))
            return pd.DataFrame()
    
    def _create_generic_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create generic features"""
        try:
            user_features = []
            
            for user_id, user_data in df.groupby('user_id'):
                features = {
                    "user_id": user_id,
                    "total_events": len(user_data),
                    "unique_days": user_data['timestamp'].dt.date.nunique(),
                    "event_types": user_data['event_type'].nunique()
                }
                
                user_features.append(features)
            
            return pd.DataFrame(user_features)
            
        except Exception as e:
            logger.error("Failed to create generic features", error=str(e))
            return pd.DataFrame()
    
    async def predict_user_behavior(self, user_id: str, prediction_type: PredictionType) -> Dict[str, Any]:
        """Predict user behavior"""
        try:
            # Find appropriate model
            model_id = None
            for mid, model in self.prediction_models.items():
                if model.prediction_type == prediction_type and model.enabled:
                    model_id = mid
                    break
            
            if not model_id or model_id not in self.trained_models:
                return {"error": "No trained model available for this prediction type"}
            
            # Get user features
            user_features = await self._get_user_features(user_id, prediction_type)
            
            if user_features.empty:
                return {"error": "No user data available for prediction"}
            
            # Make prediction
            model_data = self.trained_models[model_id]
            model = model_data["model"]
            scaler = model_data["scaler"]
            features = model_data["features"]
            
            # Prepare features
            X = user_features[features].fillna(0)
            X_scaled = scaler.transform(X)
            
            # Predict
            prediction_proba = model.predict_proba(X_scaled)[0]
            prediction = model.predict(X_scaled)[0]
            
            # Get feature importance
            if hasattr(model, 'feature_importances_'):
                feature_importance = dict(zip(features, model.feature_importances_))
            else:
                feature_importance = {}
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                user_id, prediction_type, prediction, prediction_proba[1]
            )
            
            result = {
                "user_id": user_id,
                "prediction_type": prediction_type.value,
                "prediction": prediction,
                "probability": prediction_proba[1],
                "confidence": max(prediction_proba),
                "feature_importance": feature_importance,
                "recommendations": recommendations,
                "predicted_at": datetime.utcnow().isoformat()
            }
            
            logger.info("User behavior prediction completed", 
                       user_id=user_id, prediction_type=prediction_type.value)
            
            return result
            
        except Exception as e:
            logger.error("Failed to predict user behavior", 
                        user_id=user_id, error=str(e))
            return {"error": str(e)}
    
    async def _get_user_features(self, user_id: str, prediction_type: PredictionType) -> pd.DataFrame:
        """Get features for a specific user"""
        try:
            # Get user's behavior events
            session = self.db_manager.get_session()
            try:
                events = session.query(UserBehaviorEvents).filter(
                    UserBehaviorEvents.user_id == user_id
                ).all()
            finally:
                session.close()
            
            if not events:
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame([
                {
                    "user_id": e.user_id,
                    "event_type": e.event_type,
                    "event_name": e.event_name,
                    "timestamp": e.timestamp,
                    "device_type": e.device_type,
                    "properties": e.properties
                }
                for e in events
            ])
            
            # Create features based on prediction type
            if prediction_type == PredictionType.CHURN:
                features_df = self._create_churn_features(df)
            elif prediction_type == PredictionType.ENGAGEMENT:
                features_df = self._create_engagement_features(df)
            elif prediction_type == PredictionType.CONVERSION:
                features_df = self._create_conversion_features(df)
            else:
                features_df = self._create_generic_features(df)
            
            return features_df
            
        except Exception as e:
            logger.error("Failed to get user features", user_id=user_id, error=str(e))
            return pd.DataFrame()
    
    async def _generate_recommendations(self, user_id: str, prediction_type: PredictionType,
                                       prediction: int, probability: float) -> List[str]:
        """Generate recommendations based on prediction"""
        try:
            recommendations = []
            
            if prediction_type == PredictionType.CHURN:
                if probability > 0.7:
                    recommendations.extend([
                        "Immediate intervention required",
                        "Offer retention incentives",
                        "Schedule customer success call"
                    ])
                elif probability > 0.5:
                    recommendations.extend([
                        "Monitor user activity closely",
                        "Send engagement emails",
                        "Offer personalized content"
                    ])
            
            elif prediction_type == PredictionType.ENGAGEMENT:
                if prediction == 0:  # Low engagement predicted
                    recommendations.extend([
                        "Improve onboarding experience",
                        "Send tutorial content",
                        "Highlight key features"
                    ])
                else:  # High engagement predicted
                    recommendations.extend([
                        "Offer advanced features",
                        "Create power user program",
                        "Request feedback and testimonials"
                    ])
            
            elif prediction_type == PredictionType.CONVERSION:
                if probability > 0.7:
                    recommendations.extend([
                        "Push for conversion with limited-time offer",
                        "Show social proof and testimonials",
                        "Remove friction from conversion process"
                    ])
                elif probability > 0.4:
                    recommendations.extend([
                        "Nurture with educational content",
                        "Offer free trial or demo",
                        "Show case studies"
                    ])
            
            return recommendations
            
        except Exception as e:
            logger.error("Failed to generate recommendations", error=str(e))
            return []
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        return {
            "total_models": len(self.prediction_models),
            "trained_models": len(self.trained_models),
            "redis_connected": self.redis_client.ping(),
            "system_uptime": datetime.utcnow().isoformat()
        }


# Configuration
PREDICTIVE_ANALYTICS_CONFIG = {
    "database": {
        "connection_string": os.getenv("DATABASE_URL")
    },
    "data_lake": {
        "s3_bucket": "helm-ai-data-lake"
    },
    "redis": {
        "host": os.getenv("REDIS_HOST", "localhost"),
        "port": int(os.getenv("REDIS_PORT", 6379)),
        "db": 0
    },
    "behavior_analytics": {}
}


# Initialize predictive analytics engine
predictive_analytics_engine = PredictiveAnalyticsEngine(PREDICTIVE_ANALYTICS_CONFIG)

# Export main components
__all__ = [
    'PredictiveAnalyticsEngine',
    'UserBehaviorEvent',
    'PredictionModel',
    'UserPrediction',
    'PredictionType',
    'ModelType',
    'UserSegment',
    'predictive_analytics_engine'
]
