"""
Helm AI ML Model Management System
Provides model versioning, training, deployment, and monitoring
"""

import os
import sys
import json
import pickle
import hashlib
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
import uuid

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database.database_manager import get_database_manager
from monitoring.structured_logging import logger

@dataclass
class ModelVersion:
    """ML model version"""
    model_id: str
    version: str
    model_type: str
    framework: str
    created_at: datetime
    created_by: str
    file_path: str
    metadata: Dict[str, Any]
    performance_metrics: Dict[str, float]
    training_data_hash: str
    model_size: int
    status: str = "training"  # training, trained, deployed, deprecated
    deployed_at: Optional[datetime] = None
    deprecated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'model_id': self.model_id,
            'version': self.version,
            'model_type': self.model_type,
            'framework': self.framework,
            'created_at': self.created_at.isoformat(),
            'created_by': self.created_by,
            'file_path': self.file_path,
            'metadata': self.metadata,
            'performance_metrics': self.performance_metrics,
            'training_data_hash': self.training_data_hash,
            'model_size': self.model_size,
            'status': self.status,
            'deployed_at': self.deployed_at.isoformat() if self.deployed_at else None,
            'deprecated_at': self.deprecated_at.isoformat() if self.deprecated_at else None
        }

@dataclass
class ModelTrainingJob:
    """ML model training job"""
    job_id: str
    model_id: str
    version: str
    status: str  # pending, running, completed, failed
    started_at: datetime
    completed_at: Optional[datetime] = None
    progress: float = 0.0
    logs: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    config: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'job_id': self.job_id,
            'model_id': self.model_id,
            'version': self.version,
            'status': self.status,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'progress': self.progress,
            'logs': self.logs,
            'error_message': self.error_message,
            'config': self.config
        }

@dataclass
class ModelDeployment:
    """ML model deployment"""
    deployment_id: str
    model_id: str
    version: str
    environment: str  # staging, production
    endpoint_url: str
    deployed_at: datetime
    deployed_by: str
    status: str  # active, inactive, failed
    config: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'deployment_id': self.deployment_id,
            'model_id': self.model_id,
            'version': self.version,
            'environment': self.environment,
            'endpoint_url': self.endpoint_url,
            'deployed_at': self.deployed_at.isoformat(),
            'deployed_by': self.deployed_by,
            'status': self.status,
            'config': self.config,
            'metrics': self.metrics
        }

class ModelManager:
    """ML model management system"""
    
    def __init__(self):
        self.models = {}
        self.training_jobs = {}
        self.deployments = {}
        self.model_registry = {}
        self.lock = threading.RLock()
        
        # Setup model storage directory
        self.models_dir = os.path.join(os.getcwd(), 'models')
        os.makedirs(self.models_dir, exist_ok=True)
        
    def register_model(self, model_id: str, name: str, description: str, 
                      model_type: str, framework: str, created_by: str,
                      metadata: Dict[str, Any] = None) -> str:
        """Register a new ML model"""
        try:
            model_info = {
                'model_id': model_id,
                'name': name,
                'description': description,
                'model_type': model_type,
                'framework': framework,
                'created_by': created_by,
                'created_at': datetime.now(),
                'metadata': metadata or {},
                'versions': [],
                'latest_version': None,
                'status': 'registered'
            }
            
            with self.lock:
                self.model_registry[model_id] = model_info
            
            logger.info(f"Model registered: {model_id} - {name}")
            return model_id
            
        except Exception as e:
            logger.error(f"Error registering model {model_id}: {e}")
            raise
    
    def create_training_job(self, model_id: str, training_config: Dict[str, Any],
                          created_by: str) -> str:
        """Create a model training job"""
        try:
            job_id = str(uuid.uuid4())
            version = self._generate_next_version(model_id)
            
            job = ModelTrainingJob(
                job_id=job_id,
                model_id=model_id,
                version=version,
                status='pending',
                started_at=datetime.now(),
                config=training_config
            )
            
            with self.lock:
                self.training_jobs[job_id] = job
            
            # Start training in background
            threading.Thread(target=self._run_training_job, args=(job_id,), daemon=True).start()
            
            logger.info(f"Training job created: {job_id} for model {model_id}")
            return job_id
            
        except Exception as e:
            logger.error(f"Error creating training job: {e}")
            raise
    
    def _generate_next_version(self, model_id: str) -> str:
        """Generate next version number for model"""
        with self.lock:
            model_info = self.model_registry.get(model_id, {})
            versions = model_info.get('versions', [])
            
            if not versions:
                return '1.0.0'
            
            # Parse latest version and increment
            latest_version = versions[-1]
            parts = latest_version.split('.')
            patch = int(parts[2]) + 1
            return f"{parts[0]}.{parts[1]}.{patch}"
    
    def _run_training_job(self, job_id: str):
        """Run model training job"""
        try:
            with self.lock:
                job = self.training_jobs.get(job_id)
                if not job:
                    return
                
                job.status = 'running'
                job.logs.append(f"Training started at {datetime.now()}")
            
            # Simulate training process
            self._simulate_training(job_id)
            
            with self.lock:
                job = self.training_jobs.get(job_id)
                if job:
                    job.status = 'completed'
                    job.completed_at = datetime.now()
                    job.progress = 100.0
                    job.logs.append(f"Training completed at {datetime.now()}")
            
            # Create model version
            self._create_model_version(job_id)
            
        except Exception as e:
            with self.lock:
                job = self.training_jobs.get(job_id)
                if job:
                    job.status = 'failed'
                    job.error_message = str(e)
                    job.logs.append(f"Training failed: {str(e)}")
            
            logger.error(f"Training job {job_id} failed: {e}")
    
    def _simulate_training(self, job_id: str):
        """Simulate model training process"""
        # This would contain actual training logic
        # For now, simulate progress updates
        for i in range(10):
            time.sleep(2)  # Simulate training time
            
            with self.lock:
                job = self.training_jobs.get(job_id)
                if job and job.status == 'running':
                    job.progress = (i + 1) * 10
                    job.logs.append(f"Training progress: {job.progress}%")
    
    def _create_model_version(self, job_id: str):
        """Create model version after training"""
        try:
            with self.lock:
                job = self.training_jobs.get(job_id)
                if not job:
                    return
                
                # Create model file (simulated)
                model_data = {
                    'model_id': job.model_id,
                    'version': job.version,
                    'trained_at': datetime.now(),
                    'config': job.config,
                    'weights': 'simulated_model_weights'
                }
                
                file_path = os.path.join(self.models_dir, f"{job.model_id}_{job.version}.pkl")
                with open(file_path, 'wb') as f:
                    pickle.dump(model_data, f)
                
                # Calculate model size
                model_size = os.path.getsize(file_path)
                
                # Create model version
                version = ModelVersion(
                    model_id=job.model_id,
                    version=job.version,
                    model_type='classification',  # Would be determined from model
                    framework='scikit-learn',  # Would be determined from config
                    created_at=datetime.now(),
                    created_by='training_system',
                    file_path=file_path,
                    metadata=job.config,
                    performance_metrics={
                        'accuracy': 0.85,
                        'precision': 0.82,
                        'recall': 0.88,
                        'f1_score': 0.85
                    },
                    training_data_hash='hash_placeholder',
                    model_size=model_size,
                    status='trained'
                )
                
                # Update model registry
                model_info = self.model_registry.get(job.model_id, {})
                model_info['versions'].append(job.version)
                model_info['latest_version'] = job.version
                
                # Store version
                self.models[f"{job.model_id}_{job.version}"] = version
                
                logger.info(f"Model version created: {job.model_id}_{job.version}")
                
        except Exception as e:
            logger.error(f"Error creating model version: {e}")
    
    def deploy_model(self, model_id: str, version: str, environment: str,
                    deployed_by: str, config: Dict[str, Any] = None) -> str:
        """Deploy a model version"""
        try:
            deployment_id = str(uuid.uuid4())
            version_key = f"{model_id}_{version}"
            
            model_version = self.models.get(version_key)
            if not model_version:
                raise ValueError(f"Model version not found: {version_key}")
            
            # Create deployment
            deployment = ModelDeployment(
                deployment_id=deployment_id,
                model_id=model_id,
                version=version,
                environment=environment,
                endpoint_url=f"/api/models/{model_id}/v{version}/predict",
                deployed_at=datetime.now(),
                deployed_by=deployed_by,
                status='active',
                config=config or {}
            )
            
            with self.lock:
                self.deployments[deployment_id] = deployment
                
                # Update model version status
                model_version.status = 'deployed'
                model_version.deployed_at = datetime.now()
            
            logger.info(f"Model deployed: {model_id}_{version} to {environment}")
            return deployment_id
            
        except Exception as e:
            logger.error(f"Error deploying model: {e}")
            raise
    
    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get model information"""
        with self.lock:
            return self.model_registry.get(model_id)
    
    def get_model_versions(self, model_id: str) -> List[ModelVersion]:
        """Get all versions of a model"""
        versions = []
        
        with self.lock:
            model_info = self.model_registry.get(model_id, {})
            version_numbers = model_info.get('versions', [])
            
            for version_num in version_numbers:
                version_key = f"{model_id}_{version_num}"
                version = self.models.get(version_key)
                if version:
                    versions.append(version)
        
        return sorted(versions, key=lambda v: v.created_at, reverse=True)
    
    def get_training_jobs(self, model_id: Optional[str] = None) -> List[ModelTrainingJob]:
        """Get training jobs"""
        with self.lock:
            jobs = list(self.training_jobs.values())
            
            if model_id:
                jobs = [j for j in jobs if j.model_id == model_id]
        
        return sorted(jobs, key=lambda j: j.started_at, reverse=True)
    
    def get_deployments(self, model_id: Optional[str] = None, 
                      environment: Optional[str] = None) -> List[ModelDeployment]:
        """Get model deployments"""
        with self.lock:
            deployments = list(self.deployments.values())
            
            if model_id:
                deployments = [d for d in deployments if d.model_id == model_id]
            
            if environment:
                deployments = [d for d in deployments if d.environment == environment]
        
        return sorted(deployments, key=lambda d: d.deployed_at, reverse=True)
    
    def predict(self, model_id: str, version: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make prediction using deployed model"""
        try:
            version_key = f"{model_id}_{version}"
            model_version = self.models.get(version_key)
            
            if not model_version:
                raise ValueError(f"Model version not found: {version_key}")
            
            # Load model
            with open(model_version.file_path, 'rb') as f:
                model_data = pickle.load(f)
            
            # Simulate prediction
            prediction = {
                'prediction': 'positive',
                'confidence': 0.85,
                'model_id': model_id,
                'version': version,
                'timestamp': datetime.now().isoformat()
            }
            
            # Log prediction
            logger.debug(f"Prediction made: {model_id}_{version}")
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            raise
    
    def get_model_metrics(self, model_id: str, version: str) -> Dict[str, Any]:
        """Get model performance metrics"""
        version_key = f"{model_id}_{version}"
        model_version = self.models.get(version_key)
        
        if not model_version:
            raise ValueError(f"Model version not found: {version_key}")
        
        return {
            'model_id': model_id,
            'version': version,
            'performance_metrics': model_version.performance_metrics,
            'model_size': model_version.model_size,
            'created_at': model_version.created_at.isoformat(),
            'status': model_version.status
        }
    
    def rollback_deployment(self, deployment_id: str, rolled_back_by: str) -> bool:
        """Rollback a model deployment"""
        try:
            with self.lock:
                deployment = self.deployments.get(deployment_id)
                if not deployment:
                    return False
                
                # Mark deployment as inactive
                deployment.status = 'inactive'
                
                # Find previous deployment for same model and environment
                previous_deployments = [
                    d for d in self.deployments.values()
                    if d.model_id == deployment.model_id
                    and d.environment == deployment.environment
                    and d.deployment_id != deployment_id
                    and d.status == 'active'
                ]
                
                # Activate previous deployment if exists
                if previous_deployments:
                    latest_previous = max(previous_deployments, key=lambda d: d.deployed_at)
                    latest_previous.status = 'active'
                
                logger.info(f"Deployment rolled back: {deployment_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error rolling back deployment: {e}")
            return False
    
    def get_model_registry_summary(self) -> Dict[str, Any]:
        """Get model registry summary"""
        with self.lock:
            total_models = len(self.model_registry)
            total_versions = len(self.models)
            total_deployments = len(self.deployments)
            active_training_jobs = len([j for j in self.training_jobs.values() if j.status == 'running'])
            
            # Count by model type
            model_types = defaultdict(int)
            for model_info in self.model_registry.values():
                model_types[model_info.get('model_type', 'unknown')] += 1
            
            # Count by environment
            environments = defaultdict(int)
            for deployment in self.deployments.values():
                environments[deployment.environment] += 1
            
            return {
                'total_models': total_models,
                'total_versions': total_versions,
                'total_deployments': total_deployments,
                'active_training_jobs': active_training_jobs,
                'model_types': dict(model_types),
                'environments': dict(environments),
                'last_updated': datetime.now().isoformat()
            }

# Global model manager instance
model_manager = ModelManager()

def register_model(model_id: str, name: str, description: str, model_type: str,
                  framework: str, created_by: str, metadata: Dict[str, Any] = None) -> str:
    """Register a new ML model"""
    return model_manager.register_model(
        model_id, name, description, model_type, framework, created_by, metadata
    )

def create_training_job(model_id: str, training_config: Dict[str, Any], created_by: str) -> str:
    """Create a model training job"""
    return model_manager.create_training_job(model_id, training_config, created_by)

def deploy_model(model_id: str, version: str, environment: str, deployed_by: str,
                config: Dict[str, Any] = None) -> str:
    """Deploy a model version"""
    return model_manager.deploy_model(model_id, version, environment, deployed_by, config)

def predict(model_id: str, version: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Make prediction using deployed model"""
    return model_manager.predict(model_id, version, data)

def get_model_registry_summary() -> Dict[str, Any]:
    """Get model registry summary"""
    return model_manager.get_model_registry_summary()
