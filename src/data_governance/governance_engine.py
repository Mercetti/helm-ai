"""
Data Governance and Catalog System for Helm AI
===============================================

This module provides comprehensive data governance and cataloging capabilities:
- Data catalog with metadata management
- Data lineage tracking and visualization
- Data quality monitoring and scoring
- Access control and permissions
- Data classification and tagging
- Compliance monitoring and reporting
- Data discovery and search
- Governance policies and workflows
"""

import asyncio
import json
import logging
import uuid
import hashlib
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from pathlib import Path
import re

# Third-party imports
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, Boolean, Float, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import redis
from pydantic import BaseModel, Field, validator
import networkx as nx
from elasticsearch import Elasticsearch
import great_expectations as ge

# Local imports
from src.monitoring.structured_logging import StructuredLogger
from src.database.database_manager import DatabaseManager
from src.data_lake.data_lake_manager import DataLakeManager
from src.security.audit_logger import AuditLogger

logger = StructuredLogger("data_governance")

Base = declarative_base()


class DataClassification(str, Enum):
    """Data classification levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    PII = "pii"
    PHI = "phi"


class DataQualityStatus(str, Enum):
    """Data quality status levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


class AccessLevel(str, Enum):
    """Data access levels"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"


class GovernanceStatus(str, Enum):
    """Governance status"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING_REVIEW = "pending_review"
    UNDER_INVESTIGATION = "under_investigation"


@dataclass
class DataTag:
    """Data tag definition"""
    id: str
    name: str
    description: str
    category: str
    color: str = "#1f77b4"
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DataQualityRule:
    """Data quality rule definition"""
    id: str
    name: str
    description: str
    type: str  # completeness, accuracy, consistency, validity, uniqueness
    parameters: Dict[str, Any]
    threshold: float
    severity: str = "medium"
    enabled: bool = True


@dataclass
class GovernancePolicy:
    """Data governance policy"""
    id: str
    name: str
    description: str
    type: str  # retention, privacy, security, quality, access
    rules: List[Dict[str, Any]]
    classification: DataClassification
    enforcement_level: str  # advisory, warning, blocking
    created_by: str
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DataAsset:
    """Data asset metadata"""
    id: str
    name: str
    description: str
    type: str  # table, file, view, api, stream
    source_system: str
    location: str
    format: str
    size_bytes: Optional[int] = None
    row_count: Optional[int] = None
    classification: DataClassification = DataClassification.INTERNAL
    tags: Set[str] = field(default_factory=set)
    owner: str = ""
    steward: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: Optional[datetime] = None
    quality_score: float = 0.0
    lineage_upstream: List[str] = field(default_factory=list)
    lineage_downstream: List[str] = field(default_factory=list)


class DataCatalog(Base):
    """SQLAlchemy model for data catalog"""
    __tablename__ = "data_catalog"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(String(255), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    type = Column(String(50), nullable=False)
    source_system = Column(String(255))
    location = Column(String(1000))
    format = Column(String(50))
    size_bytes = Column(BigInteger)
    row_count = Column(BigInteger)
    classification = Column(String(50), nullable=False)
    tags = Column(JSONB)
    owner = Column(String(255))
    steward = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_accessed = Column(DateTime)
    quality_score = Column(Float)
    schema_definition = Column(JSONB)
    metadata = Column(JSONB)


class DataLineage(Base):
    """SQLAlchemy model for data lineage"""
    __tablename__ = "data_lineage"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_asset_id = Column(String(255), nullable=False, index=True)
    target_asset_id = Column(String(255), nullable=False, index=True)
    transformation_type = Column(String(100))
    transformation_logic = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(255))


class DataQualityAssessment(Base):
    """SQLAlchemy model for data quality assessments"""
    __tablename__ = "data_quality_assessments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(String(255), nullable=False, index=True)
    rule_id = Column(String(255), nullable=False)
    assessment_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), nullable=False)
    score = Column(Float)
    details = Column(JSONB)
    assessed_by = Column(String(255))


class DataAccessLog(Base):
    """SQLAlchemy model for data access logs"""
    __tablename__ = "data_access_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(String(255), nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    access_type = Column(String(50), nullable=False)
    access_time = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    success = Column(Boolean, default=True)
    error_message = Column(Text)


class GovernancePolicyRecord(Base):
    """SQLAlchemy model for governance policies"""
    __tablename__ = "governance_policies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    policy_id = Column(String(255), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    type = Column(String(100), nullable=False)
    classification = Column(String(50), nullable=False)
    rules = Column(JSONB)
    enforcement_level = Column(String(50))
    created_by = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    enabled = Column(Boolean, default=True)


class DataGovernanceEngine:
    """Data Governance and Catalog Engine"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_manager = DatabaseManager(config.get('database', {}))
        self.data_lake = DataLakeManager(config.get('data_lake', {}))
        self.audit_logger = AuditLogger(config.get('audit', {}))
        
        # Initialize Redis for caching
        self.redis_client = redis.Redis(**config.get('redis', {}))
        
        # Initialize Elasticsearch for search
        self.es_client = Elasticsearch(**config.get('elasticsearch', {}))
        
        # Initialize NetworkX for lineage
        self.lineage_graph = nx.DiGraph()
        
        # Governance storage
        self.assets: Dict[str, DataAsset] = {}
        self.tags: Dict[str, DataTag] = {}
        self.policies: Dict[str, GovernancePolicy] = {}
        self.quality_rules: Dict[str, DataQualityRule] = {}
        
        logger.info("Data Governance Engine initialized")
    
    async def register_data_asset(self, asset: DataAsset) -> bool:
        """Register a new data asset in the catalog"""
        try:
            # Validate asset
            if not await self._validate_asset(asset):
                logger.error("Asset validation failed", asset_id=asset.id)
                return False
            
            # Store asset
            self.assets[asset.id] = asset
            
            # Save to database
            catalog_record = DataCatalog(
                asset_id=asset.id,
                name=asset.name,
                description=asset.description,
                type=asset.type,
                source_system=asset.source_system,
                location=asset.location,
                format=asset.format,
                size_bytes=asset.size_bytes,
                row_count=asset.row_count,
                classification=asset.classification.value,
                tags=list(asset.tags),
                owner=asset.owner,
                steward=asset.steward,
                quality_score=asset.quality_score,
                metadata={
                    "lineage_upstream": asset.lineage_upstream,
                    "lineage_downstream": asset.lineage_downstream
                }
            )
            
            session = self.db_manager.get_session()
            try:
                session.add(catalog_record)
                session.commit()
            finally:
                session.close()
            
            # Index in Elasticsearch
            await self._index_asset(asset)
            
            # Update lineage graph
            self._update_lineage_graph(asset)
            
            # Log to audit
            await self.audit_logger.log_event(
                "data_asset_registered",
                asset_id=asset.id,
                asset_type=asset.type,
                classification=asset.classification.value
            )
            
            logger.info("Data asset registered successfully", 
                       asset_id=asset.id, asset_type=asset.type)
            return True
            
        except Exception as e:
            logger.error("Failed to register data asset", 
                        asset_id=asset.id, error=str(e))
            return False
    
    async def _validate_asset(self, asset: DataAsset) -> bool:
        """Validate data asset"""
        try:
            # Check required fields
            if not asset.name or not asset.location:
                return False
            
            # Validate classification
            if asset.classification not in DataClassification:
                return False
            
            # Check if asset exists at location
            if asset.location.startswith("s3://"):
                # Validate S3 location
                bucket = asset.location.split("/")[2]
                key = "/".join(asset.location.split("/")[3:])
                
                s3_client = boto3.client('s3')
                try:
                    s3_client.head_object(Bucket=bucket, Key=key)
                except:
                    return False
            
            return True
            
        except Exception as e:
            logger.error("Asset validation failed", asset_id=asset.id, error=str(e))
            return False
    
    async def _index_asset(self, asset: DataAsset):
        """Index asset in Elasticsearch for search"""
        try:
            doc = {
                "asset_id": asset.id,
                "name": asset.name,
                "description": asset.description,
                "type": asset.type,
                "source_system": asset.source_system,
                "classification": asset.classification.value,
                "tags": list(asset.tags),
                "owner": asset.owner,
                "steward": asset.steward,
                "quality_score": asset.quality_score,
                "created_at": asset.created_at.isoformat(),
                "updated_at": asset.updated_at.isoformat()
            }
            
            self.es_client.index(
                index="data_catalog",
                id=asset.id,
                body=doc
            )
            
        except Exception as e:
            logger.error("Failed to index asset", asset_id=asset.id, error=str(e))
    
    def _update_lineage_graph(self, asset: DataAsset):
        """Update lineage graph with asset relationships"""
        # Add asset node
        self.lineage_graph.add_node(
            asset.id,
            name=asset.name,
            type=asset.type,
            classification=asset.classification.value
        )
        
        # Add upstream relationships
        for upstream_id in asset.lineage_upstream:
            self.lineage_graph.add_edge(upstream_id, asset.id)
        
        # Add downstream relationships
        for downstream_id in asset.lineage_downstream:
            self.lineage_graph.add_edge(asset.id, downstream_id)
    
    async def search_assets(self, query: str, filters: Optional[Dict[str, Any]] = None,
                          limit: int = 100) -> List[Dict[str, Any]]:
        """Search data assets using Elasticsearch"""
        try:
            # Build search query
            search_body = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "multi_match": {
                                    "query": query,
                                    "fields": ["name", "description", "tags"],
                                    "fuzziness": "AUTO"
                                }
                            }
                        ]
                    }
                },
                "size": limit
            }
            
            # Add filters
            if filters:
                filter_clauses = []
                
                if "classification" in filters:
                    filter_clauses.append({
                        "term": {"classification": filters["classification"]}
                    })
                
                if "type" in filters:
                    filter_clauses.append({
                        "term": {"type": filters["type"]}
                    })
                
                if "tags" in filters:
                    filter_clauses.append({
                        "terms": {"tags": filters["tags"]}
                    })
                
                if "owner" in filters:
                    filter_clauses.append({
                        "term": {"owner": filters["owner"]}
                    })
                
                if filter_clauses:
                    search_body["query"]["bool"]["filter"] = filter_clauses
            
            # Execute search
            response = self.es_client.search(
                index="data_catalog",
                body=search_body
            )
            
            # Process results
            results = []
            for hit in response["hits"]["hits"]:
                results.append({
                    "asset_id": hit["_source"]["asset_id"],
                    "name": hit["_source"]["name"],
                    "description": hit["_source"]["description"],
                    "type": hit["_source"]["type"],
                    "classification": hit["_source"]["classification"],
                    "tags": hit["_source"]["tags"],
                    "owner": hit["_source"]["owner"],
                    "quality_score": hit["_source"]["quality_score"],
                    "score": hit["_score"]
                })
            
            logger.info("Asset search completed", 
                       query=query, results_count=len(results))
            
            return results
            
        except Exception as e:
            logger.error("Asset search failed", query=query, error=str(e))
            return []
    
    async def get_asset_lineage(self, asset_id: str, direction: str = "both",
                              depth: int = 3) -> Dict[str, Any]:
        """Get data lineage for an asset"""
        try:
            if asset_id not in self.assets:
                return {"error": "Asset not found"}
            
            asset = self.assets[asset_id]
            
            # Build lineage based on direction
            lineage = {
                "asset": {
                    "id": asset.id,
                    "name": asset.name,
                    "type": asset.type
                },
                "upstream": [],
                "downstream": []
            }
            
            if direction in ["upstream", "both"]:
                # Get upstream assets
                for upstream_id in asset.lineage_upstream[:depth]:
                    if upstream_id in self.assets:
                        upstream_asset = self.assets[upstream_id]
                        lineage["upstream"].append({
                            "id": upstream_asset.id,
                            "name": upstream_asset.name,
                            "type": upstream_asset.type,
                            "transformation": "ETL"  # Would be stored in lineage table
                        })
            
            if direction in ["downstream", "both"]:
                # Get downstream assets
                for downstream_id in asset.lineage_downstream[:depth]:
                    if downstream_id in self.assets:
                        downstream_asset = self.assets[downstream_id]
                        lineage["downstream"].append({
                            "id": downstream_asset.id,
                            "name": downstream_asset.name,
                            "type": downstream_asset.type,
                            "transformation": "ETL"  # Would be stored in lineage table
                        })
            
            return lineage
            
        except Exception as e:
            logger.error("Failed to get asset lineage", 
                        asset_id=asset_id, error=str(e))
            return {"error": str(e)}
    
    async def assess_data_quality(self, asset_id: str) -> Dict[str, Any]:
        """Assess data quality for an asset"""
        try:
            if asset_id not in self.assets:
                return {"error": "Asset not found"}
            
            asset = self.assets[asset_id]
            
            # Get data from data lake
            data = await self.data_lake.query_data(f"SELECT * FROM {asset.name} LIMIT 10000")
            
            if data.empty:
                return {"error": "No data available for quality assessment"}
            
            # Run quality rules
            quality_results = {}
            total_score = 0.0
            rule_count = 0
            
            for rule_id, rule in self.quality_rules.items():
                if not rule.enabled:
                    continue
                
                try:
                    score = await self._apply_quality_rule(data, rule)
                    quality_results[rule_id] = {
                        "rule_name": rule.name,
                        "score": score,
                        "status": self._get_quality_status(score, rule.threshold),
                        "details": {}
                    }
                    
                    total_score += score
                    rule_count += 1
                    
                except Exception as e:
                    quality_results[rule_id] = {
                        "rule_name": rule.name,
                        "score": 0.0,
                        "status": "error",
                        "error": str(e)
                    }
            
            # Calculate overall quality score
            overall_score = total_score / rule_count if rule_count > 0 else 0.0
            
            # Update asset quality score
            asset.quality_score = overall_score
            asset.updated_at = datetime.utcnow()
            
            # Save assessment results
            await self._save_quality_assessment(asset_id, quality_results, overall_score)
            
            # Update catalog
            await self._update_asset_quality(asset_id, overall_score)
            
            logger.info("Data quality assessment completed", 
                       asset_id=asset_id, score=overall_score)
            
            return {
                "asset_id": asset_id,
                "overall_score": overall_score,
                "status": self._get_quality_status(overall_score, 0.7),
                "rule_results": quality_results,
                "assessed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Data quality assessment failed", 
                        asset_id=asset_id, error=str(e))
            return {"error": str(e)}
    
    async def _apply_quality_rule(self, data: pd.DataFrame, rule: DataQualityRule) -> float:
        """Apply a quality rule to data"""
        if rule.type == "completeness":
            # Check for null values
            null_percentage = data.isnull().sum().sum() / (len(data) * len(data.columns))
            return 1.0 - null_percentage
        
        elif rule.type == "uniqueness":
            # Check for duplicate rows
            duplicate_percentage = data.duplicated().sum() / len(data)
            return 1.0 - duplicate_percentage
        
        elif rule.type == "validity":
            # Check data format validity (simplified)
            valid_count = 0
            total_count = 0
            
            for col in data.columns:
                if data[col].dtype == 'object':
                    # Check for empty strings
                    valid_count += (data[col] != '').sum()
                else:
                    valid_count += data[col].notna().sum()
                total_count += len(data)
            
            return valid_count / total_count if total_count > 0 else 0.0
        
        elif rule.type == "accuracy":
            # Simplified accuracy check (would need reference data)
            return 0.85  # Placeholder
        
        elif rule.type == "consistency":
            # Check for consistent values across related columns
            consistency_score = 0.9  # Placeholder
            return consistency_score
        
        else:
            return 0.0
    
    def _get_quality_status(self, score: float, threshold: float) -> str:
        """Get quality status based on score"""
        if score >= 0.9:
            return DataQualityStatus.EXCELLENT.value
        elif score >= 0.8:
            return DataQualityStatus.GOOD.value
        elif score >= 0.6:
            return DataQualityStatus.FAIR.value
        elif score >= 0.4:
            return DataQualityStatus.POOR.value
        else:
            return DataQualityStatus.CRITICAL.value
    
    async def _save_quality_assessment(self, asset_id: str, results: Dict[str, Any], 
                                     overall_score: float):
        """Save quality assessment results"""
        session = self.db_manager.get_session()
        try:
            for rule_id, result in results.items():
                assessment = DataQualityAssessment(
                    asset_id=asset_id,
                    rule_id=rule_id,
                    status=result["status"],
                    score=result["score"],
                    details=result
                )
                session.add(assessment)
            
            session.commit()
        finally:
            session.close()
    
    async def _update_asset_quality(self, asset_id: str, quality_score: float):
        """Update asset quality score in catalog"""
        session = self.db_manager.get_session()
        try:
            catalog_record = session.query(DataCatalog).filter(
                DataCatalog.asset_id == asset_id
            ).first()
            
            if catalog_record:
                catalog_record.quality_score = quality_score
                catalog_record.updated_at = datetime.utcnow()
                session.commit()
        finally:
            session.close()
    
    async def create_governance_policy(self, policy: GovernancePolicy) -> bool:
        """Create a new governance policy"""
        try:
            # Validate policy
            if not await self._validate_policy(policy):
                logger.error("Policy validation failed", policy_id=policy.id)
                return False
            
            # Store policy
            self.policies[policy.id] = policy
            
            # Save to database
            policy_record = GovernancePolicyRecord(
                policy_id=policy.id,
                name=policy.name,
                description=policy.description,
                type=policy.type,
                classification=policy.classification.value,
                rules=policy.rules,
                enforcement_level=policy.enforcement_level,
                created_by=policy.created_by
            )
            
            session = self.db_manager.get_session()
            try:
                session.add(policy_record)
                session.commit()
            finally:
                session.close()
            
            logger.info("Governance policy created successfully", 
                       policy_id=policy.id, policy_type=policy.type)
            return True
            
        except Exception as e:
            logger.error("Failed to create governance policy", 
                        policy_id=policy.id, error=str(e))
            return False
    
    async def _validate_policy(self, policy: GovernancePolicy) -> bool:
        """Validate governance policy"""
        try:
            # Check required fields
            if not policy.name or not policy.type or not policy.rules:
                return False
            
            # Validate classification
            if policy.classification not in DataClassification:
                return False
            
            # Validate enforcement level
            valid_enforcement = ["advisory", "warning", "blocking"]
            if policy.enforcement_level not in valid_enforcement:
                return False
            
            return True
            
        except Exception as e:
            logger.error("Policy validation failed", policy_id=policy.id, error=str(e))
            return False
    
    async def check_compliance(self, asset_id: str) -> Dict[str, Any]:
        """Check asset compliance against governance policies"""
        try:
            if asset_id not in self.assets:
                return {"error": "Asset not found"}
            
            asset = self.assets[asset_id]
            
            # Get applicable policies
            applicable_policies = []
            for policy in self.policies.values():
                if not policy.enabled:
                    continue
                
                # Check if policy applies to asset classification
                if self._policy_applies_to_asset(policy, asset):
                    applicable_policies.append(policy)
            
            # Check compliance for each policy
            compliance_results = []
            overall_compliant = True
            
            for policy in applicable_policies:
                compliance_result = await self._check_policy_compliance(policy, asset)
                compliance_results.append(compliance_result)
                
                if not compliance_result["compliant"]:
                    overall_compliant = False
            
            # Log compliance check
            await self.audit_logger.log_event(
                "compliance_check",
                asset_id=asset_id,
                overall_compliant=overall_compliant,
                policies_checked=len(applicable_policies)
            )
            
            logger.info("Compliance check completed", 
                       asset_id=asset_id, compliant=overall_compliant)
            
            return {
                "asset_id": asset_id,
                "overall_compliant": overall_compliant,
                "compliance_results": compliance_results,
                "checked_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Compliance check failed", 
                        asset_id=asset_id, error=str(e))
            return {"error": str(e)}
    
    def _policy_applies_to_asset(self, policy: GovernancePolicy, asset: DataAsset) -> bool:
        """Check if policy applies to asset"""
        # Check classification match
        if policy.classification != asset.classification:
            return False
        
        # Additional policy-specific logic would go here
        # For now, assume all policies of the same classification apply
        
        return True
    
    async def _check_policy_compliance(self, policy: GovernancePolicy, 
                                     asset: DataAsset) -> Dict[str, Any]:
        """Check compliance against a specific policy"""
        try:
            compliant = True
            violations = []
            
            for rule in policy.rules:
                rule_result = await self._apply_policy_rule(rule, asset)
                
                if not rule_result["compliant"]:
                    compliant = False
                    violations.append({
                        "rule": rule["name"],
                        "description": rule["description"],
                        "violation": rule_result["violation"]
                    })
            
            return {
                "policy_id": policy.id,
                "policy_name": policy.name,
                "compliant": compliant,
                "violations": violations,
                "enforcement_level": policy.enforcement_level
            }
            
        except Exception as e:
            logger.error("Policy compliance check failed", 
                        policy_id=policy.id, asset_id=asset.id, error=str(e))
            return {
                "policy_id": policy.id,
                "compliant": False,
                "error": str(e)
            }
    
    async def _apply_policy_rule(self, rule: Dict[str, Any], asset: DataAsset) -> Dict[str, Any]:
        """Apply a policy rule to an asset"""
        rule_type = rule.get("type")
        
        if rule_type == "retention":
            # Check retention policy
            max_age_days = rule.get("max_age_days", 365)
            asset_age = (datetime.utcnow() - asset.created_at).days
            
            return {
                "compliant": asset_age <= max_age_days,
                "violation": f"Asset age ({asset_age} days) exceeds retention limit ({max_age_days} days)"
            }
        
        elif rule_type == "access_control":
            # Check access control requirements
            required_tags = rule.get("required_tags", [])
            missing_tags = set(required_tags) - asset.tags
            
            return {
                "compliant": len(missing_tags) == 0,
                "violation": f"Missing required tags: {list(missing_tags)}"
            }
        
        elif rule_type == "quality_threshold":
            # Check quality threshold
            min_quality = rule.get("min_quality", 0.8)
            
            return {
                "compliant": asset.quality_score >= min_quality,
                "violation": f"Quality score ({asset.quality_score}) below threshold ({min_quality})"
            }
        
        elif rule_type == "data_classification":
            # Check classification requirements
            allowed_classifications = rule.get("allowed_classifications", [])
            
            return {
                "compliant": asset.classification.value in allowed_classifications,
                "violation": f"Classification ({asset.classification.value}) not in allowed list"
            }
        
        else:
            return {
                "compliant": True,
                "violation": "Unknown rule type"
            }
    
    async def log_data_access(self, asset_id: str, user_id: str, access_type: AccessLevel,
                            ip_address: str = "", user_agent: str = "", success: bool = True):
        """Log data access for audit trail"""
        try:
            access_log = DataAccessLog(
                asset_id=asset_id,
                user_id=user_id,
                access_type=access_type.value,
                ip_address=ip_address,
                user_agent=user_agent,
                success=success
            )
            
            session = self.db_manager.get_session()
            try:
                session.add(access_log)
                session.commit()
            finally:
                session.close()
            
            # Update last accessed time
            if asset_id in self.assets and success:
                self.assets[asset_id].last_accessed = datetime.utcnow()
                await self._update_last_accessed(asset_id)
            
            logger.info("Data access logged", 
                       asset_id=asset_id, user_id=user_id, access_type=access_type.value)
            
        except Exception as e:
            logger.error("Failed to log data access", 
                        asset_id=asset_id, user_id=user_id, error=str(e))
    
    async def _update_last_accessed(self, asset_id: str):
        """Update last accessed time in catalog"""
        session = self.db_manager.get_session()
        try:
            catalog_record = session.query(DataCatalog).filter(
                DataCatalog.asset_id == asset_id
            ).first()
            
            if catalog_record:
                catalog_record.last_accessed = datetime.utcnow()
                session.commit()
        finally:
            session.close()
    
    async def get_governance_dashboard(self) -> Dict[str, Any]:
        """Get governance dashboard metrics"""
        try:
            # Get asset counts by classification
            classification_counts = {}
            for asset in self.assets.values():
                classification = asset.classification.value
                classification_counts[classification] = classification_counts.get(classification, 0) + 1
            
            # Get quality distribution
            quality_distribution = {
                "excellent": 0,
                "good": 0,
                "fair": 0,
                "poor": 0,
                "critical": 0
            }
            
            for asset in self.assets.values():
                status = self._get_quality_status(asset.quality_score, 0.7)
                quality_distribution[status] = quality_distribution.get(status, 0) + 1
            
            # Get compliance metrics
            total_policies = len(self.policies)
            enabled_policies = len([p for p in self.policies.values() if p.enabled])
            
            # Get recent access patterns
            session = self.db_manager.get_session()
            try:
                recent_access = session.query(DataAccessLog).filter(
                    DataAccessLog.access_time >= datetime.utcnow() - timedelta(days=7)
                ).count()
            finally:
                session.close()
            
            return {
                "total_assets": len(self.assets),
                "classification_distribution": classification_counts,
                "quality_distribution": quality_distribution,
                "total_policies": total_policies,
                "enabled_policies": enabled_policies,
                "recent_access_count": recent_access,
                "average_quality_score": np.mean([a.quality_score for a in self.assets.values()]) if self.assets else 0.0,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Failed to get governance dashboard", error=str(e))
            return {"error": str(e)}
    
    def get_governance_metrics(self) -> Dict[str, Any]:
        """Get governance system metrics"""
        return {
            "total_assets": len(self.assets),
            "total_policies": len(self.policies),
            "total_quality_rules": len(self.quality_rules),
            "total_tags": len(self.tags),
            "lineage_nodes": self.lineage_graph.number_of_nodes(),
            "lineage_edges": self.lineage_graph.number_of_edges(),
            "es_documents": self._get_es_document_count(),
            "redis_connected": self.redis_client.ping(),
            "system_uptime": datetime.utcnow().isoformat()
        }
    
    def _get_es_document_count(self) -> int:
        """Get Elasticsearch document count"""
        try:
            response = self.es_client.count(index="data_catalog")
            return response["count"]
        except:
            return 0


# Configuration
GOVERNANCE_CONFIG = {
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
    "elasticsearch": {
        "hosts": [os.getenv("ELASTICSEARCH_HOST", "localhost:9200")]
    },
    "audit": {
        "log_level": "INFO",
        "storage_path": "logs/governance_audit.log"
    }
}


# Initialize data governance engine
data_governance_engine = DataGovernanceEngine(GOVERNANCE_CONFIG)

# Export main components
__all__ = [
    'DataGovernanceEngine',
    'DataAsset',
    'DataTag',
    'DataQualityRule',
    'GovernancePolicy',
    'DataClassification',
    'DataQualityStatus',
    'AccessLevel',
    'GovernanceStatus',
    'data_governance_engine'
]
