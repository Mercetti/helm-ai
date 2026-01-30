"""
AI-Powered Recommendation Engine for Helm AI
===========================================

This module provides comprehensive AI-powered recommendation capabilities:
- Collaborative filtering recommendations
- Content-based recommendations
- Hybrid recommendation systems
- Real-time personalization
- User preference learning
- Item similarity analysis
- Recommendation evaluation and optimization
- A/B testing framework for recommendations
"""

import asyncio
import json
import logging
import uuid
import math
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from pathlib import Path
import numpy as np
import pandas as pd

# Third-party imports
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.neighbors import NearestNeighbors
import scipy.sparse as sp
from scipy.sparse.linalg import svds
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

logger = StructuredLogger("recommendation_engine")

Base = declarative_base()


class RecommendationType(str, Enum):
    """Types of recommendations"""
    COLLABORATIVE = "collaborative"
    CONTENT_BASED = "content_based"
    HYBRID = "hybrid"
    POPULARITY_BASED = "popularity_based"
    KNOWLEDGE_BASED = "knowledge_based"
    CONTEXT_AWARE = "context_aware"


class AlgorithmType(str, Enum):
    """Types of recommendation algorithms"""
    USER_BASED_CF = "user_based_cf"
    ITEM_BASED_CF = "item_based_cf"
    MATRIX_FACTORIZATION = "matrix_factorization"
    DEEP_LEARNING = "deep_learning"
    KNN = "knn"
    TF_IDF = "tfidf"
    WORD2VEC = "word2vec"


class FeedbackType(str, Enum):
    """Types of user feedback"""
    IMPLICIT = "implicit"  # clicks, views, time spent
    EXPLICIT = "explicit"  # ratings, likes, dislikes
    BEHAVIORAL = "behavioral"  # purchase, add to cart
    CONTEXTUAL = "contextual"  # time, location, device


@dataclass
class UserInteraction:
    """User interaction data"""
    id: str
    user_id: str
    item_id: str
    interaction_type: str
    rating: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ItemFeature:
    """Item feature data"""
    id: str
    item_id: str
    feature_name: str
    feature_value: Any
    feature_type: str  # categorical, numerical, text
    weight: float = 1.0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Recommendation:
    """Recommendation result"""
    id: str
    user_id: str
    item_id: str
    score: float
    algorithm: str
    explanation: str
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RecommendationModel:
    """Recommendation model configuration"""
    id: str
    name: str
    description: str
    recommendation_type: RecommendationType
    algorithm_type: AlgorithmType
    parameters: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


class UserInteractions(Base):
    """SQLAlchemy model for user interactions"""
    __tablename__ = "user_interactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    interaction_id = Column(String(255), nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    item_id = Column(String(255), nullable=False, index=True)
    interaction_type = Column(String(100), nullable=False)
    rating = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    context = Column(JSONB)
    metadata = Column(JSONB)


class ItemFeatures(Base):
    """SQLAlchemy model for item features"""
    __tablename__ = "item_features"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    feature_id = Column(String(255), nullable=False, index=True)
    item_id = Column(String(255), nullable=False, index=True)
    feature_name = Column(String(255), nullable=False)
    feature_value = Column(Text)
    feature_type = Column(String(50), nullable=False)
    weight = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class Recommendations(Base):
    """SQLAlchemy model for recommendations"""
    __tablename__ = "recommendations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recommendation_id = Column(String(255), nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    item_id = Column(String(255), nullable=False, index=True)
    score = Column(Float, nullable=False)
    algorithm = Column(String(100), nullable=False)
    explanation = Column(Text)
    context = Column(JSONB)
    metadata = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    clicked = Column(Boolean, default=False)
    converted = Column(Boolean, default=False)


class RecommendationModels(Base):
    """SQLAlchemy model for recommendation models"""
    __tablename__ = "recommendation_models"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(String(255), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    recommendation_type = Column(String(50), nullable=False)
    algorithm_type = Column(String(50), nullable=False)
    parameters = Column(JSONB)
    enabled = Column(Boolean, default=True)
    performance_metrics = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RecommendationEngine:
    """AI-Powered Recommendation Engine"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_manager = DatabaseManager(config.get('database', {}))
        self.data_lake = DataLakeManager(config.get('data_lake', {}))
        
        # Initialize Redis for caching
        self.redis_client = redis.Redis(**config.get('redis', {}))
        
        # Storage
        self.models: Dict[str, RecommendationModel] = {}
        self.user_item_matrix: Optional[sp.csr_matrix] = None
        self.item_features_matrix: Optional[sp.csr_matrix] = None
        self.user_similarity_matrix: Optional[np.ndarray] = None
        self.item_similarity_matrix: Optional[np.ndarray] = None
        
        # Algorithm components
        self.tfidf_vectorizer: Optional[TfidfVectorizer] = None
        self.svd_model: Optional[TruncatedSVD] = None
        self.knn_model: Optional[NearestNeighbors] = None
        
        logger.info("Recommendation Engine initialized")
    
    async def record_interaction(self, interaction: UserInteraction) -> bool:
        """Record a user interaction"""
        try:
            # Store in database
            interaction_record = UserInteractions(
                interaction_id=interaction.id,
                user_id=interaction.user_id,
                item_id=interaction.item_id,
                interaction_type=interaction.interaction_type,
                rating=interaction.rating,
                timestamp=interaction.timestamp,
                context=interaction.context,
                metadata=interaction.metadata
            )
            
            session = self.db_manager.get_session()
            try:
                session.add(interaction_record)
                session.commit()
            finally:
                session.close()
            
            # Update matrices asynchronously
            asyncio.create_task(self._update_matrices())
            
            logger.info("User interaction recorded successfully", 
                       user_id=interaction.user_id, item_id=interaction.item_id)
            return True
            
        except Exception as e:
            logger.error("Failed to record user interaction", 
                        user_id=interaction.user_id, error=str(e))
            return False
    
    async def _update_matrices(self):
        """Update recommendation matrices"""
        try:
            # Get all interactions
            session = self.db_manager.get_session()
            try:
                interactions = session.query(UserInteractions).all()
            finally:
                session.close()
            
            if not interactions:
                return
            
            # Convert to DataFrame
            df = pd.DataFrame([
                {
                    "user_id": i.user_id,
                    "item_id": i.item_id,
                    "rating": i.rating or 1.0,  # Default rating for implicit feedback
                    "interaction_type": i.interaction_type
                }
                for i in interactions
            ])
            
            # Create user-item matrix
            self._create_user_item_matrix(df)
            
            # Create item features matrix
            await self._create_item_features_matrix()
            
            # Calculate similarity matrices
            self._calculate_similarity_matrices()
            
        except Exception as e:
            logger.error("Failed to update matrices", error=str(e))
    
    def _create_user_item_matrix(self, df: pd.DataFrame):
        """Create user-item interaction matrix"""
        try:
            # Create user and item mappings
            unique_users = df['user_id'].unique()
            unique_items = df['item_id'].unique()
            
            user_to_idx = {user: idx for idx, user in enumerate(unique_users)}
            item_to_idx = {item: idx for idx, item in enumerate(unique_items)}
            
            # Create sparse matrix
            row_indices = [user_to_idx[user] for user in df['user_id']]
            col_indices = [item_to_idx[item] for item in df['item_id']]
            data = df['rating'].values
            
            self.user_item_matrix = sp.csr_matrix(
                (data, (row_indices, col_indices)),
                shape=(len(unique_users), len(unique_items))
            )
            
            # Store mappings
            self.user_to_idx = user_to_idx
            self.idx_to_user = {idx: user for user, idx in user_to_idx.items()}
            self.item_to_idx = item_to_idx
            self.idx_to_item = {idx: item for item, idx in item_to_idx.items()}
            
            logger.info("User-item matrix created", 
                       shape=self.user_item_matrix.shape)
            
        except Exception as e:
            logger.error("Failed to create user-item matrix", error=str(e))
    
    async def _create_item_features_matrix(self):
        """Create item features matrix"""
        try:
            # Get item features
            session = self.db_manager.get_session()
            try:
                features = session.query(ItemFeatures).all()
            finally:
                session.close()
            
            if not features:
                return
            
            # Convert to DataFrame
            df = pd.DataFrame([
                {
                    "item_id": f.item_id,
                    "feature_name": f.feature_name,
                    "feature_value": f.feature_value,
                    "feature_type": f.feature_type,
                    "weight": f.weight
                }
                for f in features
            ])
            
            # Create TF-IDF matrix for text features
            text_features = df[df['feature_type'] == 'text']
            
            if not text_features.empty:
                # Group text features by item
                item_texts = text_features.groupby('item_id')['feature_value'].apply(' '.join)
                
                # Create TF-IDF matrix
                self.tfidf_vectorizer = TfidfVectorizer(
                    max_features=5000,
                    stop_words='english',
                    ngram_range=(1, 2)
                )
                
                self.item_features_matrix = self.tfidf_vectorizer.fit_transform(item_texts)
                
                logger.info("Item features matrix created", 
                           shape=self.item_features_matrix.shape)
            
        except Exception as e:
            logger.error("Failed to create item features matrix", error=str(e))
    
    def _calculate_similarity_matrices(self):
        """Calculate similarity matrices"""
        try:
            if self.user_item_matrix is not None:
                # Calculate item similarity (item-based collaborative filtering)
                item_similarity = cosine_similarity(self.user_item_matrix.T)
                self.item_similarity_matrix = item_similarity
                
                # Calculate user similarity (user-based collaborative filtering)
                user_similarity = cosine_similarity(self.user_item_matrix)
                self.user_similarity_matrix = user_similarity
                
                logger.info("Similarity matrices calculated")
            
        except Exception as e:
            logger.error("Failed to calculate similarity matrices", error=str(e))
    
    async def create_recommendation_model(self, model: RecommendationModel) -> bool:
        """Create a new recommendation model"""
        try:
            # Validate model configuration
            if not await self._validate_model(model):
                logger.error("Model validation failed", model_id=model.id)
                return False
            
            # Store model
            self.models[model.id] = model
            
            # Train model based on type
            await self._train_model(model)
            
            logger.info("Recommendation model created successfully", 
                       model_id=model.id, algorithm_type=model.algorithm_type.value)
            return True
            
        except Exception as e:
            logger.error("Failed to create recommendation model", 
                        model_id=model.id, error=str(e))
            return False
    
    async def _validate_model(self, model: RecommendationModel) -> bool:
        """Validate model configuration"""
        try:
            # Check required fields
            if not model.name or not model.recommendation_type or not model.algorithm_type:
                return False
            
            # Validate types
            if model.recommendation_type not in RecommendationType:
                return False
            
            if model.algorithm_type not in AlgorithmType:
                return False
            
            return True
            
        except Exception as e:
            logger.error("Model validation failed", error=str(e))
            return False
    
    async def _train_model(self, model: RecommendationModel):
        """Train recommendation model"""
        try:
            if model.algorithm_type == AlgorithmType.MATRIX_FACTORIZATION:
                await self._train_matrix_factorization(model)
            elif model.algorithm_type == AlgorithmType.KNN:
                await self._train_knn_model(model)
            elif model.algorithm_type == AlgorithmType.TF_IDF:
                await self._train_tfidf_model(model)
            else:
                logger.warning(f"Training not implemented for {model.algorithm_type}")
            
        except Exception as e:
            logger.error("Failed to train model", model_id=model.id, error=str(e))
    
    async def _train_matrix_factorization(self, model: RecommendationModel):
        """Train matrix factorization model"""
        try:
            if self.user_item_matrix is None:
                raise ValueError("User-item matrix not available")
            
            # Perform SVD
            n_components = model.parameters.get('n_components', 50)
            U, sigma, Vt = svds(self.user_item_matrix, k=n_components)
            
            # Store model components
            self.svd_model = {
                'U': U,
                'sigma': sigma,
                'Vt': Vt,
                'n_components': n_components
            }
            
            logger.info("Matrix factorization model trained", 
                       n_components=n_components)
            
        except Exception as e:
            logger.error("Failed to train matrix factorization", error=str(e))
    
    async def _train_knn_model(self, model: RecommendationModel):
        """Train KNN model"""
        try:
            if self.item_features_matrix is None:
                raise ValueError("Item features matrix not available")
            
            # Train KNN
            n_neighbors = model.parameters.get('n_neighbors', 10)
            self.knn_model = NearestNeighbors(
                n_neighbors=n_neighbors,
                metric='cosine',
                algorithm='brute'
            )
            self.knn_model.fit(self.item_features_matrix)
            
            logger.info("KNN model trained", n_neighbors=n_neighbors)
            
        except Exception as e:
            logger.error("Failed to train KNN model", error=str(e))
    
    async def _train_tfidf_model(self, model: RecommendationModel):
        """Train TF-IDF model"""
        try:
            # TF-IDF model is already created in _create_item_features_matrix
            logger.info("TF-IDF model ready")
            
        except Exception as e:
            logger.error("Failed to train TF-IDF model", error=str(e))
    
    async def get_recommendations(self, user_id: str, model_id: str, 
                                num_recommendations: int = 10,
                                exclude_seen: bool = True) -> List[Dict[str, Any]]:
        """Get recommendations for a user"""
        try:
            if model_id not in self.models:
                return [{"error": "Model not found"}]
            
            model = self.models[model_id]
            
            # Get recommendations based on algorithm type
            if model.algorithm_type == AlgorithmType.USER_BASED_CF:
                recommendations = await self._user_based_cf_recommendations(
                    user_id, num_recommendations, exclude_seen
                )
            elif model.algorithm_type == AlgorithmType.ITEM_BASED_CF:
                recommendations = await self._item_based_cf_recommendations(
                    user_id, num_recommendations, exclude_seen
                )
            elif model.algorithm_type == AlgorithmType.MATRIX_FACTORIZATION:
                recommendations = await self._matrix_factorization_recommendations(
                    user_id, num_recommendations, exclude_seen
                )
            elif model.algorithm_type == AlgorithmType.CONTENT_BASED:
                recommendations = await self._content_based_recommendations(
                    user_id, num_recommendations, exclude_seen
                )
            elif model.algorithm_type == AlgorithmType.KNN:
                recommendations = await self._knn_recommendations(
                    user_id, num_recommendations, exclude_seen
                )
            else:
                recommendations = await self._popularity_based_recommendations(
                    user_id, num_recommendations, exclude_seen
                )
            
            # Save recommendations
            await self._save_recommendations(user_id, recommendations, model.algorithm_type.value)
            
            return recommendations
            
        except Exception as e:
            logger.error("Failed to get recommendations", 
                        user_id=user_id, model_id=model_id, error=str(e))
            return [{"error": str(e)}]
    
    async def _user_based_cf_recommendations(self, user_id: str, num_recommendations: int,
                                           exclude_seen: bool) -> List[Dict[str, Any]]:
        """User-based collaborative filtering recommendations"""
        try:
            if self.user_similarity_matrix is None or self.user_item_matrix is None:
                return []
            
            if user_id not in self.user_to_idx:
                return []
            
            user_idx = self.user_to_idx[user_id]
            
            # Find similar users
            user_similarities = self.user_similarity_matrix[user_idx]
            similar_user_indices = np.argsort(user_similarities)[::-1][1:50]  # Top 50 similar users
            
            # Get items liked by similar users
            recommendations = {}
            user_seen_items = set()
            
            if exclude_seen:
                # Get items already seen by user
                user_items = self.user_item_matrix[user_idx].nonzero()[1]
                user_seen_items = set(self.idx_to_item[idx] for idx in user_items)
            
            for similar_user_idx in similar_user_indices:
                similar_user_items = self.user_item_matrix[similar_user_idx].nonzero()[1]
                
                for item_idx in similar_user_items:
                    item_id = self.idx_to_item[item_idx]
                    
                    if exclude_seen and item_id in user_seen_items:
                        continue
                    
                    if item_id not in recommendations:
                        recommendations[item_id] = 0
                    
                    # Weight by similarity and rating
                    rating = self.user_item_matrix[similar_user_idx, item_idx]
                    similarity = user_similarities[similar_user_idx]
                    recommendations[item_id] += rating * similarity
            
            # Sort and return top recommendations
            sorted_recommendations = sorted(
                recommendations.items(), key=lambda x: x[1], reverse=True
            )[:num_recommendations]
            
            return [
                {
                    "item_id": item_id,
                    "score": float(score),
                    "algorithm": "user_based_cf",
                    "explanation": f"Recommended based on similar users' preferences"
                }
                for item_id, score in sorted_recommendations
            ]
            
        except Exception as e:
            logger.error("Failed to generate user-based CF recommendations", error=str(e))
            return []
    
    async def _item_based_cf_recommendations(self, user_id: str, num_recommendations: int,
                                           exclude_seen: bool) -> List[Dict[str, Any]]:
        """Item-based collaborative filtering recommendations"""
        try:
            if self.item_similarity_matrix is None or self.user_item_matrix is None:
                return []
            
            if user_id not in self.user_to_idx:
                return []
            
            user_idx = self.user_to_idx[user_id]
            
            # Get items liked by user
            user_items = self.user_item_matrix[user_idx].nonzero()[1]
            user_seen_items = set(self.idx_to_item[idx] for idx in user_items)
            
            # Calculate recommendations based on similar items
            recommendations = {}
            
            for item_idx in user_items:
                item_similarities = self.item_similarity_matrix[item_idx]
                similar_item_indices = np.argsort(item_similarities)[::-1][1:20]  # Top 20 similar items
                
                for similar_item_idx in similar_item_indices:
                    similar_item_id = self.idx_to_item[similar_item_idx]
                    
                    if exclude_seen and similar_item_id in user_seen_items:
                        continue
                    
                    if similar_item_id not in recommendations:
                        recommendations[similar_item_id] = 0
                    
                    # Weight by similarity and user rating
                    user_rating = self.user_item_matrix[user_idx, item_idx]
                    similarity = item_similarities[similar_item_idx]
                    recommendations[similar_item_id] += user_rating * similarity
            
            # Sort and return top recommendations
            sorted_recommendations = sorted(
                recommendations.items(), key=lambda x: x[1], reverse=True
            )[:num_recommendations]
            
            return [
                {
                    "item_id": item_id,
                    "score": float(score),
                    "algorithm": "item_based_cf",
                    "explanation": f"Recommended because it's similar to items you liked"
                }
                for item_id, score in sorted_recommendations
            ]
            
        except Exception as e:
            logger.error("Failed to generate item-based CF recommendations", error=str(e))
            return []
    
    async def _matrix_factorization_recommendations(self, user_id: str, num_recommendations: int,
                                                   exclude_seen: bool) -> List[Dict[str, Any]]:
        """Matrix factorization recommendations"""
        try:
            if self.svd_model is None or self.user_item_matrix is None:
                return []
            
            if user_id not in self.user_to_idx:
                return []
            
            user_idx = self.user_to_idx[user_id]
            
            # Reconstruct user ratings
            U = self.svd_model['U']
            sigma = self.svd_model['sigma']
            Vt = self.svd_model['Vt']
            
            # Predict ratings for all items
            user_factors = U[user_idx] @ sigma
            item_factors = Vt.T
            predicted_ratings = user_factors @ item_factors
            
            # Get items not yet seen
            user_seen_items = set()
            if exclude_seen:
                seen_items = self.user_item_matrix[user_idx].nonzero()[1]
                user_seen_items = set(self.idx_to_item[idx] for idx in seen_items)
            
            recommendations = []
            for item_idx, rating in enumerate(predicted_ratings):
                item_id = self.idx_to_item[item_idx]
                
                if exclude_seen and item_id in user_seen_items:
                    continue
                
                recommendations.append({
                    "item_id": item_id,
                    "score": float(rating),
                    "algorithm": "matrix_factorization",
                    "explanation": f"Recommended based on latent factor analysis"
                })
            
            # Sort and return top recommendations
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            
            return recommendations[:num_recommendations]
            
        except Exception as e:
            logger.error("Failed to generate matrix factorization recommendations", error=str(e))
            return []
    
    async def _content_based_recommendations(self, user_id: str, num_recommendations: int,
                                            exclude_seen: bool) -> List[Dict[str, Any]]:
        """Content-based recommendations"""
        try:
            if self.knn_model is None or self.item_features_matrix is None:
                return []
            
            # Get user's liked items
            session = self.db_manager.get_session()
            try:
                interactions = session.query(UserInteractions).filter(
                    UserInteractions.user_id == user_id,
                    UserInteractions.rating >= 4.0  # High ratings
                ).all()
            finally:
                session.close()
            
            if not interactions:
                return await self._popularity_based_recommendations(user_id, num_recommendations, exclude_seen)
            
            # Get features of liked items
            liked_item_ids = [i.item_id for i in interactions]
            
            # Calculate average feature vector for liked items
            liked_features = []
            for item_id in liked_item_ids:
                if hasattr(self, 'item_to_idx') and item_id in self.item_to_idx:
                    item_idx = self.item_to_idx[item_id]
                    if item_idx < self.item_features_matrix.shape[0]:
                        liked_features.append(self.item_features_matrix[item_idx].toarray().flatten())
            
            if not liked_features:
                return await self._popularity_based_recommendations(user_id, num_recommendations, exclude_seen)
            
            # Calculate average profile
            avg_profile = np.mean(liked_features, axis=0)
            
            # Find similar items
            distances, indices = self.knn_model.kneighbors(avg_profile.reshape(1, -1))
            
            recommendations = []
            user_seen_items = set(liked_item_ids) if exclude_seen else set()
            
            for idx, distance in zip(indices[0], distances[0]):
                item_id = self.idx_to_item.get(idx)
                
                if item_id and item_id not in user_seen_items:
                    recommendations.append({
                        "item_id": item_id,
                        "score": float(1 - distance),  # Convert distance to similarity
                        "algorithm": "content_based",
                        "explanation": f"Recommended based on content similarity to items you liked"
                    })
            
            return recommendations[:num_recommendations]
            
        except Exception as e:
            logger.error("Failed to generate content-based recommendations", error=str(e))
            return []
    
    async def _knn_recommendations(self, user_id: str, num_recommendations: int,
                               exclude_seen: bool) -> List[Dict[str, Any]]:
        """KNN recommendations"""
        try:
            # This is similar to content-based but uses KNN directly
            return await self._content_based_recommendations(user_id, num_recommendations, exclude_seen)
            
        except Exception as e:
            logger.error("Failed to generate KNN recommendations", error=str(e))
            return []
    
    async def _popularity_based_recommendations(self, user_id: str, num_recommendations: int,
                                                exclude_seen: bool) -> List[Dict[str, Any]]:
        """Popularity-based recommendations"""
        try:
            # Get popular items
            session = self.db_manager.get_session()
            try:
                # Calculate item popularity based on interaction count and average rating
                query = session.query(
                    UserInteractions.item_id,
                    func.count(UserInteractions.id).label('interaction_count'),
                    func.avg(UserInteractions.rating).label('avg_rating')
                ).group_by(UserInteractions.item_id).order_by(
                    func.count(UserInteractions.id).desc(),
                    func.avg(UserInteractions.rating).desc()
                ).limit(num_recommendations * 2)  # Get more to filter
                
                popular_items = query.all()
            finally:
                session.close()
            
            # Get user's seen items
            user_seen_items = set()
            if exclude_seen:
                user_interactions = session.query(UserInteractions).filter(
                    UserInteractions.user_id == user_id
                ).all()
                user_seen_items = set(i.item_id for i in user_interactions)
            
            recommendations = []
            for item in popular_items:
                if item.item_id not in user_seen_items:
                    recommendations.append({
                        "item_id": item.item_id,
                        "score": float(item.interaction_count * item.avg_rating),
                        "algorithm": "popularity_based",
                        "explanation": f"Popular item with {item.interaction_count} interactions and {item.avg_rating:.1f} avg rating"
                    })
                
                if len(recommendations) >= num_recommendations:
                    break
            
            return recommendations[:num_recommendations]
            
        except Exception as e:
            logger.error("Failed to generate popularity-based recommendations", error=str(e))
            return []
    
    async def _save_recommendations(self, user_id: str, recommendations: List[Dict[str, Any]], algorithm: str):
        """Save recommendations to database"""
        try:
            session = self.db_manager.get_session()
            try:
                for rec in recommendations:
                    if 'error' not in rec:
                        recommendation_record = Recommendations(
                            recommendation_id=str(uuid.uuid4()),
                            user_id=user_id,
                            item_id=rec['item_id'],
                            score=rec['score'],
                            algorithm=algorithm,
                            explanation=rec.get('explanation', ''),
                            context=rec.get('context', {}),
                            metadata=rec.get('metadata', {})
                        )
                        session.add(recommendation_record)
                
                session.commit()
            finally:
                session.close()
            
        except Exception as e:
            logger.error("Failed to save recommendations", error=str(e))
    
    async def evaluate_recommendations(self, user_id: str, model_id: str) -> Dict[str, Any]:
        """Evaluate recommendation quality"""
        try:
            # Get recommendations for user
            recommendations = await self.get_recommendations(user_id, model_id, 20)
            
            if 'error' in recommendations[0]:
                return {"error": "Failed to get recommendations"}
            
            # Get actual user interactions after recommendations were generated
            session = self.db_manager.get_session()
            try:
                # Get interactions from last 7 days
                cutoff_date = datetime.utcnow() - timedelta(days=7)
                
                actual_interactions = session.query(UserInteractions).filter(
                    UserInteractions.user_id == user_id,
                    UserInteractions.timestamp >= cutoff_date
                ).all()
            finally:
                session.close()
            
            # Calculate metrics
            recommended_items = set(rec['item_id'] for rec in recommendations)
            interacted_items = set(i.item_id for i in actual_interactions)
            
            # Precision@k
            precision_at_5 = len(recommended_items.intersection(interacted_items)) / min(5, len(recommended_items))
            precision_at_10 = len(recommended_items.intersection(interacted_items)) / min(10, len(recommended_items))
            
            # Recall
            recall = len(recommended_items.intersection(interacted_items)) / len(interacted_items) if interacted_items else 0
            
            # Coverage
            total_items = session.query(UserInteractions.item_id).distinct().count()
            coverage = len(recommended_items) / total_items if total_items > 0 else 0
            
            metrics = {
                "precision_at_5": precision_at_5,
                "precision_at_10": precision_at_10,
                "recall": recall,
                "coverage": coverage,
                "total_recommendations": len(recommendations),
                "actual_interactions": len(actual_interactions),
                "evaluated_at": datetime.utcnow().isoformat()
            }
            
            logger.info("Recommendation evaluation completed", 
                       user_id=user_id, precision_at_5=precision_at_5)
            
            return metrics
            
        except Exception as e:
            logger.error("Failed to evaluate recommendations", user_id=user_id, error=str(e))
            return {"error": str(e)}
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        return {
            "total_models": len(self.models),
            "user_item_matrix_shape": self.user_item_matrix.shape if self.user_item_matrix is not None else None,
            "item_features_matrix_shape": self.item_features_matrix.shape if self.item_features_matrix is not None else None,
            "redis_connected": self.redis_client.ping(),
            "system_uptime": datetime.utcnow().isoformat()
        }


# Configuration
RECOMMENDATION_ENGINE_CONFIG = {
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
    }
}


# Initialize recommendation engine
recommendation_engine = RecommendationEngine(RECOMMENDATION_ENGINE_CONFIG)

# Export main components
__all__ = [
    'RecommendationEngine',
    'UserInteraction',
    'ItemFeature',
    'Recommendation',
    'RecommendationModel',
    'RecommendationType',
    'AlgorithmType',
    'FeedbackType',
    'recommendation_engine'
]
