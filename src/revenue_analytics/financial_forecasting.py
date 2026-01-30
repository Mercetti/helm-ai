"""
Revenue Analytics and Financial Forecasting for Helm AI
======================================================

This module provides comprehensive revenue analytics and financial forecasting capabilities:
- Revenue tracking and analysis
- Financial forecasting with ML models
- Customer lifetime value (CLV) calculation
- Churn prediction and prevention
- Revenue recognition and reporting
- Financial KPIs and metrics
- Budget vs actual analysis
- Cash flow forecasting
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
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
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
from src.billing.subscription_manager import SubscriptionManager

logger = StructuredLogger("revenue_analytics")

Base = declarative_base()


class RevenueType(str, Enum):
    """Types of revenue"""
    SUBSCRIPTION = "subscription"
    ONE_TIME = "one_time"
    USAGE_BASED = "usage_based"
    ENTERPRISE = "enterprise"
    API_CALLS = "api_calls"
    SUPPORT = "support"
    TRAINING = "training"


class ForecastPeriod(str, Enum):
    """Forecast periods"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class ForecastModel(str, Enum):
    """Forecasting models"""
    LINEAR_REGRESSION = "linear_regression"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    ARIMA = "arima"
    PROPHET = "prophet"
    LSTM = "lstm"


@dataclass
class RevenueMetric:
    """Revenue metric definition"""
    id: str
    name: str
    description: str
    revenue_type: RevenueType
    amount: float
    currency: str = "USD"
    period: str = "monthly"
    customer_id: Optional[str] = None
    subscription_id: Optional[str] = None
    product_id: Optional[str] = None
    region: Optional[str] = None
    recorded_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class FinancialKPI:
    """Financial KPI definition"""
    id: str
    name: str
    description: str
    value: float
    unit: str
    target: Optional[float] = None
    period: str = "monthly"
    category: str = "revenue"
    calculated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ForecastConfiguration:
    """Forecast configuration"""
    id: str
    name: str
    description: str
    model_type: ForecastModel
    target_variable: str
    features: List[str]
    forecast_period: ForecastPeriod
    forecast_horizon: int  # number of periods to forecast
    confidence_interval: float = 0.95
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CLVModel:
    """Customer Lifetime Value model configuration"""
    id: str
    name: str
    description: str
    churn_probability: float
    average_monthly_revenue: float
    customer_lifetime_months: int
    discount_rate: float = 0.1
    created_at: datetime = field(default_factory=datetime.utcnow)


class RevenueData(Base):
    """SQLAlchemy model for revenue data"""
    __tablename__ = "revenue_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    metric_id = Column(String(255), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    revenue_type = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    period = Column(String(20), default="monthly")
    customer_id = Column(String(255))
    subscription_id = Column(String(255))
    product_id = Column(String(255))
    region = Column(String(100))
    recorded_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSONB)


class FinancialForecast(Base):
    """SQLAlchemy model for financial forecasts"""
    __tablename__ = "financial_forecasts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    forecast_id = Column(String(255), nullable=False, index=True)
    model_type = Column(String(50), nullable=False)
    target_variable = Column(String(100), nullable=False)
    forecast_period = Column(String(20), nullable=False)
    forecast_values = Column(JSONB)
    confidence_intervals = Column(JSONB)
    model_metrics = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(255))


class CustomerCLV(Base):
    """SQLAlchemy model for customer CLV"""
    __tablename__ = "customer_clv"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(String(255), nullable=False, unique=True, index=True)
    clv_value = Column(Float, nullable=False)
    churn_probability = Column(Float)
    average_monthly_revenue = Column(Float)
    predicted_lifetime_months = Column(Integer)
    discount_rate = Column(Float, default=0.1)
    calculated_at = Column(DateTime, default=datetime.utcnow)
    model_version = Column(String(50))


class RevenueAnalyticsEngine:
    """Revenue Analytics and Financial Forecasting Engine"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_manager = DatabaseManager(config.get('database', {}))
        self.data_lake = DataLakeManager(config.get('data_lake', {}))
        self.subscription_manager = SubscriptionManager(config.get('billing', {}))
        
        # Initialize Redis for caching
        self.redis_client = redis.Redis(**config.get('redis', {}))
        
        # ML models storage
        self.forecast_models: Dict[str, Any] = {}
        self.clv_models: Dict[str, Any] = {}
        
        # Configuration storage
        self.forecast_configs: Dict[str, ForecastConfiguration] = {}
        self.clv_configs: Dict[str, CLVModel] = {}
        
        logger.info("Revenue Analytics Engine initialized")
    
    async def record_revenue(self, metric: RevenueMetric) -> bool:
        """Record revenue metric"""
        try:
            # Store in database
            revenue_record = RevenueData(
                metric_id=metric.id,
                name=metric.name,
                revenue_type=metric.revenue_type.value,
                amount=metric.amount,
                currency=metric.currency,
                period=metric.period,
                customer_id=metric.customer_id,
                subscription_id=metric.subscription_id,
                product_id=metric.product_id,
                region=metric.region,
                recorded_at=metric.recorded_at
            )
            
            session = self.db_manager.get_session()
            try:
                session.add(revenue_record)
                session.commit()
            finally:
                session.close()
            
            # Cache in Redis
            await self._cache_revenue_metric(metric)
            
            logger.info("Revenue metric recorded successfully", 
                       metric_id=metric.id, amount=metric.amount)
            return True
            
        except Exception as e:
            logger.error("Failed to record revenue metric", 
                        metric_id=metric.id, error=str(e))
            return False
    
    async def _cache_revenue_metric(self, metric: RevenueMetric):
        """Cache revenue metric in Redis"""
        try:
            key = f"revenue:{metric.id}"
            value = {
                "metric_id": metric.id,
                "name": metric.name,
                "revenue_type": metric.revenue_type.value,
                "amount": metric.amount,
                "currency": metric.currency,
                "period": metric.period,
                "customer_id": metric.customer_id,
                "recorded_at": metric.recorded_at.isoformat()
            }
            
            self.redis_client.setex(key, 86400, json.dumps(value))  # 24 hours TTL
            
        except Exception as e:
            logger.error("Failed to cache revenue metric", error=str(e))
    
    async def get_revenue_analytics(self, start_date: datetime, end_date: datetime,
                                  group_by: str = "month") -> Dict[str, Any]:
        """Get revenue analytics for a date range"""
        try:
            # Query revenue data
            session = self.db_manager.get_session()
            try:
                query = session.query(RevenueData).filter(
                    RevenueData.recorded_at >= start_date,
                    RevenueData.recorded_at <= end_date
                )
                
                revenue_data = query.all()
            finally:
                session.close()
            
            if not revenue_data:
                return {"error": "No revenue data found for the specified period"}
            
            # Convert to DataFrame
            df = pd.DataFrame([
                {
                    "metric_id": r.metric_id,
                    "name": r.name,
                    "revenue_type": r.revenue_type,
                    "amount": r.amount,
                    "currency": r.currency,
                    "period": r.period,
                    "customer_id": r.customer_id,
                    "subscription_id": r.subscription_id,
                    "product_id": r.product_id,
                    "region": r.region,
                    "recorded_at": r.recorded_at
                }
                for r in revenue_data
            ])
            
            # Group by specified period
            if group_by == "day":
                df['period'] = df['recorded_at'].dt.date
            elif group_by == "week":
                df['period'] = df['recorded_at'].dt.to_period('W').dt.start_time
            elif group_by == "month":
                df['period'] = df['recorded_at'].dt.to_period('M').dt.start_time
            elif group_by == "quarter":
                df['period'] = df['recorded_at'].dt.to_period('Q').dt.start_time
            elif group_by == "year":
                df['period'] = df['recorded_at'].dt.to_period('Y').dt.start_time
            
            # Calculate analytics
            analytics = {
                "summary": self._calculate_revenue_summary(df),
                "trends": self._calculate_revenue_trends(df, group_by),
                "by_type": self._calculate_revenue_by_type(df),
                "by_region": self._calculate_revenue_by_region(df),
                "by_customer": self._calculate_revenue_by_customer(df),
                "growth_rates": self._calculate_growth_rates(df, group_by)
            }
            
            logger.info("Revenue analytics generated successfully", 
                       start_date=start_date.isoformat(), end_date=end_date.isoformat())
            
            return analytics
            
        except Exception as e:
            logger.error("Failed to get revenue analytics", error=str(e))
            return {"error": str(e)}
    
    def _calculate_revenue_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate revenue summary statistics"""
        return {
            "total_revenue": df['amount'].sum(),
            "average_revenue": df['amount'].mean(),
            "median_revenue": df['amount'].median(),
            "min_revenue": df['amount'].min(),
            "max_revenue": df['amount'].max(),
            "total_transactions": len(df),
            "unique_customers": df['customer_id'].nunique(),
            "average_transaction_value": df['amount'].mean(),
            "revenue_per_customer": df.groupby('customer_id')['amount'].sum().mean()
        }
    
    def _calculate_revenue_trends(self, df: pd.DataFrame, group_by: str) -> List[Dict[str, Any]]:
        """Calculate revenue trends over time"""
        trends = df.groupby('period').agg({
            'amount': ['sum', 'mean', 'count']
        }).reset_index()
        
        trends.columns = ['period', 'total_revenue', 'average_revenue', 'transaction_count']
        
        return trends.to_dict('records')
    
    def _calculate_revenue_by_type(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate revenue breakdown by type"""
        by_type = df.groupby('revenue_type').agg({
            'amount': ['sum', 'mean', 'count']
        }).reset_index()
        
        by_type.columns = ['revenue_type', 'total_revenue', 'average_revenue', 'transaction_count']
        
        return {
            "breakdown": by_type.to_dict('records'),
            "percentages": (by_type.set_index('revenue_type')['total_revenue'] / 
                          by_type['total_revenue'].sum() * 100).to_dict()
        }
    
    def _calculate_revenue_by_region(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate revenue breakdown by region"""
        if 'region' not in df.columns or df['region'].isna().all():
            return {"breakdown": [], "percentages": {}}
        
        by_region = df.groupby('region').agg({
            'amount': ['sum', 'mean', 'count']
        }).reset_index()
        
        by_region.columns = ['region', 'total_revenue', 'average_revenue', 'transaction_count']
        
        return {
            "breakdown": by_region.to_dict('records'),
            "percentages": (by_region.set_index('region')['total_revenue'] / 
                          by_region['total_revenue'].sum() * 100).to_dict()
        }
    
    def _calculate_revenue_by_customer(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate revenue breakdown by customer"""
        by_customer = df.groupby('customer_id').agg({
            'amount': ['sum', 'mean', 'count']
        }).reset_index()
        
        by_customer.columns = ['customer_id', 'total_revenue', 'average_revenue', 'transaction_count']
        
        # Get top customers
        top_customers = by_customer.nlargest(10, 'total_revenue')
        
        return {
            "total_customers": len(by_customer),
            "top_customers": top_customers.to_dict('records'),
            "average_revenue_per_customer": by_customer['total_revenue'].mean(),
            "customer_distribution": {
                "high_value": len(by_customer[by_customer['total_revenue'] > by_customer['total_revenue'].quantile(0.8)]),
                "medium_value": len(by_customer[(by_customer['total_revenue'] > by_customer['total_revenue'].quantile(0.2)) & 
                                              (by_customer['total_revenue'] <= by_customer['total_revenue'].quantile(0.8))]),
                "low_value": len(by_customer[by_customer['total_revenue'] <= by_customer['total_revenue'].quantile(0.2)])
            }
        }
    
    def _calculate_growth_rates(self, df: pd.DataFrame, group_by: str) -> Dict[str, Any]:
        """Calculate revenue growth rates"""
        trends = df.groupby('period')['amount'].sum().reset_index()
        trends = trends.sort_values('period')
        
        if len(trends) < 2:
            return {"growth_rates": [], "average_growth_rate": 0}
        
        # Calculate period-over-period growth
        trends['growth_rate'] = trends['amount'].pct_change() * 100
        trends['growth_rate'] = trends['growth_rate'].fillna(0)
        
        return {
            "growth_rates": trends[['period', 'growth_rate']].to_dict('records'),
            "average_growth_rate": trends['growth_rate'].mean(),
            "latest_growth_rate": trends['growth_rate'].iloc[-1],
            "growth_volatility": trends['growth_rate'].std()
        }
    
    async def create_forecast_model(self, config: ForecastConfiguration) -> bool:
        """Create a new forecast model"""
        try:
            # Validate configuration
            if not await self._validate_forecast_config(config):
                logger.error("Forecast configuration validation failed", forecast_id=config.id)
                return False
            
            # Store configuration
            self.forecast_configs[config.id] = config
            
            # Train model
            await self._train_forecast_model(config)
            
            logger.info("Forecast model created successfully", 
                       forecast_id=config.id, model_type=config.model_type.value)
            return True
            
        except Exception as e:
            logger.error("Failed to create forecast model", 
                        forecast_id=config.id, error=str(e))
            return False
    
    async def _validate_forecast_config(self, config: ForecastConfiguration) -> bool:
        """Validate forecast configuration"""
        try:
            # Check required fields
            if not config.name or not config.target_variable or not config.features:
                return False
            
            # Validate model type
            if config.model_type not in ForecastModel:
                return False
            
            # Validate forecast period
            if config.forecast_period not in ForecastPeriod:
                return False
            
            return True
            
        except Exception as e:
            logger.error("Forecast configuration validation failed", error=str(e))
            return False
    
    async def _train_forecast_model(self, config: ForecastConfiguration):
        """Train forecast model"""
        try:
            # Get training data
            training_data = await self._get_forecast_training_data(config)
            
            if training_data.empty:
                raise ValueError("No training data available")
            
            # Prepare features and target
            X = training_data[config.features]
            y = training_data[config.target_variable]
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train model based on type
            if config.model_type == ForecastModel.LINEAR_REGRESSION:
                model = LinearRegression()
                model.fit(X_train_scaled, y_train)
            elif config.model_type == ForecastModel.RANDOM_FOREST:
                model = RandomForestRegressor(n_estimators=100, random_state=42)
                model.fit(X_train_scaled, y_train)
            elif config.model_type == ForecastModel.GRADIENT_BOOSTING:
                model = GradientBoostingRegressor(n_estimators=100, random_state=42)
                model.fit(X_train_scaled, y_train)
            else:
                raise ValueError(f"Unsupported model type: {config.model_type}")
            
            # Evaluate model
            y_pred = model.predict(X_test_scaled)
            metrics = {
                "mae": mean_absolute_error(y_test, y_pred),
                "mse": mean_squared_error(y_test, y_pred),
                "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
                "r2": r2_score(y_test, y_pred)
            }
            
            # Store model
            self.forecast_models[config.id] = {
                "model": model,
                "scaler": scaler,
                "features": config.features,
                "target_variable": config.target_variable,
                "metrics": metrics,
                "trained_at": datetime.utcnow()
            }
            
            logger.info("Forecast model trained successfully", 
                       forecast_id=config.id, r2_score=metrics["r2"])
            
        except Exception as e:
            logger.error("Failed to train forecast model", 
                        forecast_id=config.id, error=str(e))
            raise
    
    async def _get_forecast_training_data(self, config: ForecastConfiguration) -> pd.DataFrame:
        """Get training data for forecast model"""
        try:
            # Query historical revenue data
            session = self.db_manager.get_session()
            try:
                # Get last 2 years of data
                start_date = datetime.utcnow() - timedelta(days=730)
                
                query = session.query(RevenueData).filter(
                    RevenueData.recorded_at >= start_date
                )
                
                revenue_data = query.all()
            finally:
                session.close()
            
            if not revenue_data:
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame([
                {
                    "amount": r.amount,
                    "revenue_type": r.revenue_type,
                    "customer_id": r.customer_id,
                    "region": r.region,
                    "recorded_at": r.recorded_at,
                    "day_of_week": r.recorded_at.weekday(),
                    "month": r.recorded_at.month,
                    "quarter": r.recorded_at.quarter,
                    "year": r.recorded_at.year
                }
                for r in revenue_data
            ])
            
            # Add time-based features
            df['days_since_start'] = (df['recorded_at'] - df['recorded_at'].min()).dt.days
            
            # Encode categorical variables
            df = pd.get_dummies(df, columns=['revenue_type', 'region'], drop_first=True)
            
            return df
            
        except Exception as e:
            logger.error("Failed to get forecast training data", error=str(e))
            return pd.DataFrame()
    
    async def calculate_clv(self, customer_id: str) -> Dict[str, Any]:
        """Calculate Customer Lifetime Value"""
        try:
            # Get customer revenue history
            session = self.db_manager.get_session()
            try:
                query = session.query(RevenueData).filter(
                    RevenueData.customer_id == customer_id
                ).order_by(RevenueData.recorded_at.desc())
                
                customer_revenue = query.all()
            finally:
                session.close()
            
            if not customer_revenue:
                return {"error": "No revenue data found for customer"}
            
            # Calculate CLV metrics
            df = pd.DataFrame([
                {
                    "amount": r.amount,
                    "recorded_at": r.recorded_at,
                    "revenue_type": r.revenue_type
                }
                for r in customer_revenue
            ])
            
            # Calculate average monthly revenue
            df['month'] = df['recorded_at'].dt.to_period('M')
            monthly_revenue = df.groupby('month')['amount'].sum()
            avg_monthly_revenue = monthly_revenue.mean()
            
            # Calculate customer tenure in months
            tenure_months = (df['recorded_at'].max() - df['recorded_at'].min()).days / 30.44
            
            # Estimate churn probability (simplified)
            recent_months = 6
            if len(monthly_revenue) >= recent_months:
                recent_revenue = monthly_revenue.tail(recent_months)
                churn_indicators = (recent_revenue == 0).sum()
                churn_probability = min(churn_indicators / recent_months, 1.0)
            else:
                churn_probability = 0.1  # Default assumption
            
            # Calculate CLV using simplified formula
            discount_rate = 0.1  # 10% discount rate
            if churn_probability > 0:
                expected_lifetime = 1 / churn_probability
            else:
                expected_lifetime = 120  # 10 years default
            
            clv = (avg_monthly_revenue * 12 * (1 - churn_probability)) / discount_rate
            
            # Save CLV calculation
            await self._save_customer_clv(customer_id, clv, churn_probability, 
                                         avg_monthly_revenue, int(expected_lifetime))
            
            result = {
                "customer_id": customer_id,
                "clv_value": clv,
                "churn_probability": churn_probability,
                "average_monthly_revenue": avg_monthly_revenue,
                "expected_lifetime_months": int(expected_lifetime),
                "tenure_months": tenure_months,
                "total_revenue_to_date": df['amount'].sum(),
                "calculated_at": datetime.utcnow().isoformat()
            }
            
            logger.info("CLV calculated successfully", 
                       customer_id=customer_id, clv_value=clv)
            
            return result
            
        except Exception as e:
            logger.error("Failed to calculate CLV", customer_id=customer_id, error=str(e))
            return {"error": str(e)}
    
    async def _save_customer_clv(self, customer_id: str, clv_value: float, 
                               churn_probability: float, avg_monthly_revenue: float,
                               predicted_lifetime_months: int):
        """Save customer CLV calculation"""
        try:
            clv_record = CustomerCLV(
                customer_id=customer_id,
                clv_value=clv_value,
                churn_probability=churn_probability,
                average_monthly_revenue=avg_monthly_revenue,
                predicted_lifetime_months=predicted_lifetime_months,
                calculated_at=datetime.utcnow(),
                model_version="1.0"
            )
            
            session = self.db_manager.get_session()
            try:
                # Upsert CLV record
                existing = session.query(CustomerCLV).filter(
                    CustomerCLV.customer_id == customer_id
                ).first()
                
                if existing:
                    existing.clv_value = clv_value
                    existing.churn_probability = churn_probability
                    existing.average_monthly_revenue = avg_monthly_revenue
                    existing.predicted_lifetime_months = predicted_lifetime_months
                    existing.calculated_at = datetime.utcnow()
                else:
                    session.add(clv_record)
                
                session.commit()
            finally:
                session.close()
            
        except Exception as e:
            logger.error("Failed to save customer CLV", error=str(e))
    
    async def get_financial_kpis(self, period: str = "monthly") -> Dict[str, Any]:
        """Get financial KPIs"""
        try:
            # Calculate date range based on period
            end_date = datetime.utcnow()
            if period == "daily":
                start_date = end_date - timedelta(days=1)
            elif period == "weekly":
                start_date = end_date - timedelta(weeks=1)
            elif period == "monthly":
                start_date = end_date - timedelta(days=30)
            elif period == "quarterly":
                start_date = end_date - timedelta(days=90)
            else:  # yearly
                start_date = end_date - timedelta(days=365)
            
            # Get revenue data for the period
            session = self.db_manager.get_session()
            try:
                query = session.query(RevenueData).filter(
                    RevenueData.recorded_at >= start_date,
                    RevenueData.recorded_at <= end_date
                )
                
                revenue_data = query.all()
            finally:
                session.close()
            
            if not revenue_data:
                return {"error": "No revenue data found for the specified period"}
            
            # Convert to DataFrame
            df = pd.DataFrame([
                {
                    "amount": r.amount,
                    "revenue_type": r.revenue_type,
                    "customer_id": r.customer_id,
                    "recorded_at": r.recorded_at
                }
                for r in revenue_data
            ])
            
            # Calculate KPIs
            kpis = {
                "period": period,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_revenue": df['amount'].sum(),
                "average_revenue_per_day": df['amount'].sum() / (end_date - start_date).days,
                "total_transactions": len(df),
                "average_transaction_value": df['amount'].mean(),
                "unique_customers": df['customer_id'].nunique(),
                "revenue_per_customer": df.groupby('customer_id')['amount'].sum().mean(),
                "revenue_by_type": df.groupby('revenue_type')['amount'].sum().to_dict(),
                "daily_revenue_trend": self._calculate_daily_trend(df),
                "top_revenue_days": self._get_top_revenue_days(df, 5),
                "customer_acquisition_rate": self._calculate_customer_acquisition_rate(df)
            }
            
            logger.info("Financial KPIs calculated successfully", period=period)
            
            return kpis
            
        except Exception as e:
            logger.error("Failed to get financial KPIs", error=str(e))
            return {"error": str(e)}
    
    def _calculate_daily_trend(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Calculate daily revenue trend"""
        df['date'] = df['recorded_at'].dt.date
        daily_revenue = df.groupby('date')['amount'].sum().reset_index()
        daily_revenue.columns = ['date', 'revenue']
        
        return daily_revenue.to_dict('records')
    
    def _get_top_revenue_days(self, df: pd.DataFrame, top_n: int) -> List[Dict[str, Any]]:
        """Get top revenue days"""
        df['date'] = df['recorded_at'].dt.date
        daily_revenue = df.groupby('date')['amount'].sum().reset_index()
        daily_revenue.columns = ['date', 'revenue']
        
        return daily_revenue.nlargest(top_n, 'revenue').to_dict('records')
    
    def _calculate_customer_acquisition_rate(self, df: pd.DataFrame) -> float:
        """Calculate customer acquisition rate"""
        # Get first purchase date for each customer
        customer_first_purchase = df.groupby('customer_id')['recorded_at'].min().reset_index()
        customer_first_purchase.columns = ['customer_id', 'first_purchase_date']
        
        # Calculate new customers in the period
        period_start = df['recorded_at'].min()
        new_customers = customer_first_purchase[
            customer_first_purchase['first_purchase_date'] >= period_start
        ]
        
        return len(new_customers)
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        return {
            "total_forecast_models": len(self.forecast_models),
            "total_clv_calculations": len(self.clv_models),
            "forecast_configurations": len(self.forecast_configs),
            "clv_configurations": len(self.clv_configs),
            "redis_connected": self.redis_client.ping(),
            "system_uptime": datetime.utcnow().isoformat()
        }


# Configuration
REVENUE_ANALYTICS_CONFIG = {
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
    "billing": {
        "stripe_secret_key": os.getenv("STRIPE_SECRET_KEY")
    }
}


# Initialize revenue analytics engine
revenue_analytics_engine = RevenueAnalyticsEngine(REVENUE_ANALYTICS_CONFIG)

# Export main components
__all__ = [
    'RevenueAnalyticsEngine',
    'RevenueMetric',
    'FinancialKPI',
    'ForecastConfiguration',
    'CLVModel',
    'RevenueType',
    'ForecastPeriod',
    'ForecastModel',
    'revenue_analytics_engine'
]
