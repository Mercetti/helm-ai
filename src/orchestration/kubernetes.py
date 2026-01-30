"""
Helm AI Kubernetes Orchestration and Scaling System
Provides comprehensive Kubernetes deployment, scaling, and management
"""

import os
import sys
import json
import time
import yaml
import asyncio
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
import subprocess
import kubernetes
from kubernetes import client, config, watch

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from monitoring.structured_logging import logger
from monitoring.distributed_tracing import distributed_tracer

@dataclass
class DeploymentConfig:
    """Kubernetes deployment configuration"""
    name: str
    namespace: str
    image: str
    replicas: int = 3
    resources: Dict[str, Dict[str, str]] = field(default_factory=dict)
    env_vars: Dict[str, str] = field(default_factory=dict)
    ports: List[int] = field(default_factory=list)
    health_checks: Dict[str, Any] = field(default_factory=dict)
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'namespace': self.namespace,
            'image': self.image,
            'replicas': self.replicas,
            'resources': self.resources,
            'env_vars': self.env_vars,
            'ports': self.ports,
            'health_checks': self.health_checks,
            'labels': self.labels,
            'annotations': self.annotations
        }

@dataclass
class ScalingPolicy:
    """Auto-scaling policy configuration"""
    deployment_name: str
    namespace: str
    min_replicas: int = 1
    max_replicas: int = 10
    target_cpu_utilization: int = 70
    target_memory_utilization: int = 80
    scale_up_cooldown: int = 60
    scale_down_cooldown: int = 300
    scale_up_factor: float = 1.5
    scale_down_factor: float = 0.8
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'deployment_name': self.deployment_name,
            'namespace': self.namespace,
            'min_replicas': self.min_replicas,
            'max_replicas': self.max_replicas,
            'target_cpu_utilization': self.target_cpu_utilization,
            'target_memory_utilization': self.target_memory_utilization,
            'scale_up_cooldown': self.scale_up_cooldown,
            'scale_down_cooldown': self.scale_down_cooldown,
            'scale_up_factor': self.scale_up_factor,
            'scale_down_factor': self.scale_down_factor
        }

@dataclass
class ClusterMetrics:
    """Cluster resource metrics"""
    timestamp: datetime
    cpu_usage_percent: float
    memory_usage_percent: float
    pod_count: int
    node_count: int
    pending_pods: int
    failed_pods: int
    namespace_metrics: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'cpu_usage_percent': self.cpu_usage_percent,
            'memory_usage_percent': self.memory_usage_percent,
            'pod_count': self.pod_count,
            'node_count': self.node_count,
            'pending_pods': self.pending_pods,
            'failed_pods': self.failed_pods,
            'namespace_metrics': self.namespace_metrics
        }

class KubernetesOrchestrator:
    """Kubernetes deployment and scaling orchestrator"""
    
    def __init__(self):
        self.deployments = {}
        self.scaling_policies = {}
        self.cluster_metrics = deque(maxlen=1000)
        self.scaling_events = deque(maxlen=500)
        self.lock = threading.RLock()
        
        # Initialize Kubernetes client
        self._init_kubernetes_client()
        
        # Configuration
        self.config = {
            'default_namespace': 'helm-ai',
            'health_check_interval': 30,
            'metrics_interval': 60,
            'scaling_interval': 120,
            'max_concurrent_deployments': 5
        }
        
        # Start monitoring threads
        self._start_monitoring()
    
    def _init_kubernetes_client(self):
        """Initialize Kubernetes client"""
        try:
            # Try to load in-cluster config first
            config.load_incluster_config()
        except:
            try:
                # Fall back to kubeconfig
                config.load_kube_config()
            except:
                logger.error("Could not initialize Kubernetes client")
                raise
        
        self.v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.autoscaling_v1 = client.AutoscalingV1Api()
        self.custom_api = client.CustomObjectsApi()
    
    def _start_monitoring(self):
        """Start monitoring threads"""
        # Health check thread
        health_thread = threading.Thread(
            target=self._health_check_loop,
            daemon=True,
            name="k8s-health-check"
        )
        health_thread.start()
        
        # Metrics collection thread
        metrics_thread = threading.Thread(
            target=self._metrics_collection_loop,
            daemon=True,
            name="k8s-metrics"
        )
        metrics_thread.start()
        
        # Auto-scaling thread
        scaling_thread = threading.Thread(
            target=self._auto_scaling_loop,
            daemon=True,
            name="k8s-auto-scaling"
        )
        scaling_thread.start()
    
    def deploy_application(self, deployment_config: DeploymentConfig) -> bool:
        """Deploy application to Kubernetes"""
        try:
            with distributed_tracer.trace_span("deploy_application", "kubernetes-orchestrator"):
                logger.info(f"Deploying application: {deployment_config.name}")
                
                # Create namespace if it doesn't exist
                self._ensure_namespace(deployment_config.namespace)
                
                # Create deployment
                deployment = self._create_deployment_manifest(deployment_config)
                
                # Apply deployment
                self.apps_v1.create_namespaced_deployment(
                    namespace=deployment_config.namespace,
                    body=deployment
                )
                
                # Create service if ports are specified
                if deployment_config.ports:
                    self._create_service(deployment_config)
                
                # Store deployment config
                with self.lock:
                    self.deployments[deployment_config.name] = deployment_config
                
                logger.info(f"Successfully deployed: {deployment_config.name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to deploy {deployment_config.name}: {e}")
            return False
    
    def _ensure_namespace(self, namespace: str):
        """Ensure namespace exists"""
        try:
            self.v1.read_namespace(name=namespace)
        except client.ApiException as e:
            if e.status == 404:
                # Create namespace
                namespace_manifest = client.V1Namespace(
                    metadata=client.V1ObjectMeta(
                        name=namespace,
                        labels={'app': 'helm-ai', 'managed-by': 'kubernetes-orchestrator'}
                    )
                )
                self.v1.create_namespace(body=namespace_manifest)
                logger.info(f"Created namespace: {namespace}")
            else:
                raise
    
    def _create_deployment_manifest(self, config: DeploymentConfig) -> client.V1Deployment:
        """Create Kubernetes deployment manifest"""
        # Container specification
        container = client.V1Container(
            name=config.name,
            image=config.image,
            ports=[
                client.V1ContainerPort(container_port=port)
                for port in config.ports
            ],
            env=[
                client.V1EnvVar(name=key, value=value)
                for key, value in config.env_vars.items()
            ],
            resources=client.V1ResourceRequirements(
                limits=config.resources.get('limits', {}),
                requests=config.resources.get('requests', {})
            )
        )
        
        # Add health checks if specified
        if config.health_checks:
            if 'liveness' in config.health_checks:
                container.liveness_probe = client.V1Probe(
                    http_get=client.V1HTTPGetAction(
                        path=config.health_checks['liveness'].get('path', '/health'),
                        port=config.health_checks['liveness'].get('port', 8000)
                    ),
                    initial_delay_seconds=config.health_checks['liveness'].get('initial_delay', 30),
                    period_seconds=config.health_checks['liveness'].get('period', 10)
                )
            
            if 'readiness' in config.health_checks:
                container.readiness_probe = client.V1Probe(
                    http_get=client.V1HTTPGetAction(
                        path=config.health_checks['readiness'].get('path', '/ready'),
                        port=config.health_checks['readiness'].get('port', 8000)
                    ),
                    initial_delay_seconds=config.health_checks['readiness'].get('initial_delay', 5),
                    period_seconds=config.health_checks['readiness'].get('period', 5)
                )
        
        # Pod template
        pod_template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(
                labels=config.labels,
                annotations=config.annotations
            ),
            spec=client.V1PodSpec(
                containers=[container],
                security_context=client.V1PodSecurityContext(
                    run_as_non_root=True,
                    run_as_user=1000,
                    fs_group=2000
                )
            )
        )
        
        # Deployment spec
        deployment_spec = client.V1DeploymentSpec(
            replicas=config.replicas,
            template=pod_template,
            selector=client.V1LabelSelector(
                match_labels={'app': config.name}
            )
        )
        
        # Deployment
        deployment = client.V1Deployment(
            api_version="apps/v1",
            kind="Deployment",
            metadata=client.V1ObjectMeta(
                name=config.name,
                namespace=config.namespace,
                labels={'app': config.name, 'managed-by': 'kubernetes-orchestrator'}
            ),
            spec=deployment_spec
        )
        
        return deployment
    
    def _create_service(self, config: DeploymentConfig):
        """Create Kubernetes service"""
        service = client.V1Service(
            api_version="v1",
            kind="Service",
            metadata=client.V1ObjectMeta(
                name=f"{config.name}-service",
                namespace=config.namespace,
                labels={'app': config.name, 'managed-by': 'kubernetes-orchestrator'}
            ),
            spec=client.V1ServiceSpec(
                selector={'app': config.name},
                ports=[
                    client.V1ServicePort(
                        port=port,
                        target_port=port,
                        protocol="TCP"
                    )
                    for port in config.ports
                ],
                type="ClusterIP"
            )
        )
        
        self.v1.create_namespaced_service(
            namespace=config.namespace,
            body=service
        )
    
    def scale_deployment(self, deployment_name: str, namespace: str, replicas: int) -> bool:
        """Scale deployment to specified replica count"""
        try:
            with distributed_tracer.trace_span("scale_deployment", "kubernetes-orchestrator"):
                logger.info(f"Scaling {deployment_name} to {replicas} replicas")
                
                # Get current deployment
                deployment = self.apps_v1.read_namespaced_deployment(
                    name=deployment_name,
                    namespace=namespace
                )
                
                # Update replica count
                deployment.spec.replicas = replicas
                
                # Apply update
                self.apps_v1.patch_namespaced_deployment(
                    name=deployment_name,
                    namespace=namespace,
                    body=deployment
                )
                
                # Log scaling event
                scaling_event = {
                    'deployment_name': deployment_name,
                    'namespace': namespace,
                    'old_replicas': deployment.spec.replicas,
                    'new_replicas': replicas,
                    'timestamp': datetime.now(),
                    'reason': 'manual_scale'
                }
                
                with self.lock:
                    self.scaling_events.append(scaling_event)
                
                logger.info(f"Successfully scaled {deployment_name} to {replicas} replicas")
                return True
                
        except Exception as e:
            logger.error(f"Failed to scale {deployment_name}: {e}")
            return False
    
    def create_horizontal_pod_autoscaler(self, scaling_policy: ScalingPolicy) -> bool:
        """Create Horizontal Pod Autoscaler"""
        try:
            with distributed_tracer.trace_span("create_hpa", "kubernetes-orchestrator"):
                logger.info(f"Creating HPA for {scaling_policy.deployment_name}")
                
                hpa = client.V1HorizontalPodAutoscaler(
                    api_version="autoscaling/v1",
                    kind="HorizontalPodAutoscaler",
                    metadata=client.V1ObjectMeta(
                        name=f"{scaling_policy.deployment_name}-hpa",
                        namespace=scaling_policy.namespace
                    ),
                    spec=client.V1HorizontalPodAutoscalerSpec(
                        scale_target_ref=client.V1CrossVersionObjectReference(
                            api_version="apps/v1",
                            kind="Deployment",
                            name=scaling_policy.deployment_name
                        ),
                        min_replicas=scaling_policy.min_replicas,
                        max_replicas=scaling_policy.max_replicas,
                        target_cpu_utilization_percentage=scaling_policy.target_cpu_utilization
                    )
                )
                
                self.autoscaling_v1.create_namespaced_horizontal_pod_autoscaler(
                    namespace=scaling_policy.namespace,
                    body=hpa
                )
                
                # Store scaling policy
                with self.lock:
                    self.scaling_policies[scaling_policy.deployment_name] = scaling_policy
                
                logger.info(f"Successfully created HPA for {scaling_policy.deployment_name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to create HPA for {scaling_policy.deployment_name}: {e}")
            return False
    
    def _health_check_loop(self):
        """Health check monitoring loop"""
        while True:
            try:
                with distributed_tracer.trace_span("health_check_loop", "kubernetes-orchestrator"):
                    self._check_deployment_health()
                
                time.sleep(self.config['health_check_interval'])
                
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                time.sleep(30)
    
    def _check_deployment_health(self):
        """Check health of all deployments"""
        with self.lock:
            deployments_to_check = list(self.deployments.values())
        
        for deployment_config in deployments_to_check:
            try:
                # Get deployment status
                deployment = self.apps_v1.read_namespaced_deployment(
                    name=deployment_config.name,
                    namespace=deployment_config.namespace
                )
                
                # Check replica status
                desired_replicas = deployment.spec.replicas
                ready_replicas = deployment.status.ready_replicas or 0
                
                if ready_replicas < desired_replicas:
                    logger.warning(
                        f"Deployment {deployment_config.name} not healthy: "
                        f"{ready_replicas}/{desired_replicas} replicas ready"
                    )
                
                # Check pod status
                pods = self.v1.list_namespaced_pod(
                    namespace=deployment_config.namespace,
                    label_selector=f"app={deployment_config.name}"
                )
                
                failed_pods = [
                    pod for pod in pods.items
                    if pod.status.phase in ['Failed', 'Error', 'CrashLoopBackOff']
                ]
                
                if failed_pods:
                    logger.error(
                        f"Deployment {deployment_config.name} has {len(failed_pods)} failed pods"
                    )
                
            except Exception as e:
                logger.error(f"Error checking health for {deployment_config.name}: {e}")
    
    def _metrics_collection_loop(self):
        """Metrics collection loop"""
        while True:
            try:
                with distributed_tracer.trace_span("metrics_collection_loop", "kubernetes-orchestrator"):
                    metrics = self._collect_cluster_metrics()
                    
                    with self.lock:
                        self.cluster_metrics.append(metrics)
                
                time.sleep(self.config['metrics_interval'])
                
            except Exception as e:
                logger.error(f"Metrics collection loop error: {e}")
                time.sleep(30)
    
    def _collect_cluster_metrics(self) -> ClusterMetrics:
        """Collect cluster resource metrics"""
        try:
            # Get node metrics
            nodes = self.v1.list_node()
            node_count = len(nodes.items)
            
            # Calculate CPU and memory usage
            total_cpu_capacity = 0
            total_memory_capacity = 0
            total_cpu_usage = 0
            total_memory_usage = 0
            
            for node in nodes.items:
                if node.status.allocatable:
                    total_cpu_capacity += self._parse_cpu(node.status.allocatable.get('cpu', '0'))
                    total_memory_capacity += self._parse_memory(node.status.allocatable.get('memory', '0'))
                
                if node.status.capacity:
                    total_cpu_usage += self._parse_cpu(node.status.capacity.get('cpu', '0'))
                    total_memory_usage += self._parse_memory(node.status.capacity.get('memory', '0'))
            
            cpu_usage_percent = (total_cpu_usage / total_cpu_capacity * 100) if total_cpu_capacity > 0 else 0
            memory_usage_percent = (total_memory_usage / total_memory_capacity * 100) if total_memory_capacity > 0 else 0
            
            # Get pod metrics
            pods = self.v1.list_pod_for_all_namespaces()
            pod_count = len(pods.items)
            
            pending_pods = len([
                pod for pod in pods.items
                if pod.status.phase == 'Pending'
            ])
            
            failed_pods = len([
                pod for pod in pods.items
                if pod.status.phase in ['Failed', 'Error']
            ])
            
            # Get namespace metrics
            namespace_metrics = {}
            for pod in pods.items:
                namespace = pod.metadata.namespace
                if namespace not in namespace_metrics:
                    namespace_metrics[namespace] = {
                        'pod_count': 0,
                        'pending_pods': 0,
                        'failed_pods': 0
                    }
                
                namespace_metrics[namespace]['pod_count'] += 1
                if pod.status.phase == 'Pending':
                    namespace_metrics[namespace]['pending_pods'] += 1
                elif pod.status.phase in ['Failed', 'Error']:
                    namespace_metrics[namespace]['failed_pods'] += 1
            
            return ClusterMetrics(
                timestamp=datetime.now(),
                cpu_usage_percent=cpu_usage_percent,
                memory_usage_percent=memory_usage_percent,
                pod_count=pod_count,
                node_count=node_count,
                pending_pods=pending_pods,
                failed_pods=failed_pods,
                namespace_metrics=namespace_metrics
            )
            
        except Exception as e:
            logger.error(f"Error collecting cluster metrics: {e}")
            return ClusterMetrics(
                timestamp=datetime.now(),
                cpu_usage_percent=0,
                memory_usage_percent=0,
                pod_count=0,
                node_count=0,
                pending_pods=0,
                failed_pods=0
            )
    
    def _parse_cpu(self, cpu_str: str) -> float:
        """Parse CPU string to millicores"""
        if cpu_str.endswith('m'):
            return float(cpu_str[:-1])
        else:
            return float(cpu_str) * 1000
    
    def _parse_memory(self, memory_str: str) -> float:
        """Parse memory string to MB"""
        if memory_str.endswith('Ki'):
            return float(memory_str[:-2]) / 1024
        elif memory_str.endswith('Mi'):
            return float(memory_str[:-2])
        elif memory_str.endswith('Gi'):
            return float(memory_str[:-2]) * 1024
        else:
            return float(memory_str) / 1024 / 1024
    
    def _auto_scaling_loop(self):
        """Auto-scaling decision loop"""
        while True:
            try:
                with distributed_tracer.trace_span("auto_scaling_loop", "kubernetes-orchestrator"):
                    self._evaluate_scaling_decisions()
                
                time.sleep(self.config['scaling_interval'])
                
            except Exception as e:
                logger.error(f"Auto-scaling loop error: {e}")
                time.sleep(60)
    
    def _evaluate_scaling_decisions(self):
        """Evaluate and execute scaling decisions"""
        with self.lock:
            policies = list(self.scaling_policies.values())
        
        for policy in policies:
            try:
                # Get current deployment
                deployment = self.apps_v1.read_namespaced_deployment(
                    name=policy.deployment_name,
                    namespace=policy.namespace
                )
                
                current_replicas = deployment.spec.replicas
                
                # Check if scaling is needed based on metrics
                scale_decision = self._calculate_scale_decision(policy, deployment)
                
                if scale_decision != current_replicas:
                    logger.info(
                        f"Auto-scaling {policy.deployment_name}: "
                        f"{current_replicas} -> {scale_decision} replicas"
                    )
                    
                    self.scale_deployment(
                        policy.deployment_name,
                        policy.namespace,
                        scale_decision
                    )
                
            except Exception as e:
                logger.error(f"Error evaluating scaling for {policy.deployment_name}: {e}")
    
    def _calculate_scale_decision(self, policy: ScalingPolicy, deployment) -> int:
        """Calculate optimal replica count"""
        current_replicas = deployment.spec.replicas
        
        # Get resource usage metrics
        try:
            # Get pod metrics (simplified - in production would use metrics server)
            pods = self.v1.list_namespaced_pod(
                namespace=policy.namespace,
                label_selector=f"app={policy.deployment_name}"
            )
            
            # Calculate average CPU and memory usage
            total_cpu_usage = 0
            total_memory_usage = 0
            running_pods = 0
            
            for pod in pods.items:
                if pod.status.phase == 'Running':
                    running_pods += 1
                    # In production, would get actual usage from metrics server
                    # For now, use placeholder logic
                    total_cpu_usage += 50  # Placeholder: 50% average CPU
                    total_memory_usage += 60  # Placeholder: 60% average memory
            
            if running_pods > 0:
                avg_cpu_usage = total_cpu_usage / running_pods
                avg_memory_usage = total_memory_usage / running_pods
            else:
                avg_cpu_usage = 0
                avg_memory_usage = 0
            
            # Scaling logic
            if avg_cpu_usage > policy.target_cpu_utilization or avg_memory_usage > policy.target_memory_utilization:
                # Scale up
                new_replicas = min(
                    int(current_replicas * policy.scale_up_factor),
                    policy.max_replicas
                )
                return max(new_replicas, current_replicas + 1)
            
            elif avg_cpu_usage < policy.target_cpu_utilization * 0.5 and avg_memory_usage < policy.target_memory_utilization * 0.5:
                # Scale down
                new_replicas = max(
                    int(current_replicas * policy.scale_down_factor),
                    policy.min_replicas
                )
                return min(new_replicas, current_replicas - 1)
            
            return current_replicas
            
        except Exception as e:
            logger.error(f"Error calculating scale decision: {e}")
            return current_replicas
    
    def get_deployment_status(self, deployment_name: str, namespace: str) -> Optional[Dict[str, Any]]:
        """Get deployment status"""
        try:
            deployment = self.apps_v1.read_namespaced_deployment(
                name=deployment_name,
                namespace=namespace
            )
            
            pods = self.v1.list_namespaced_pod(
                namespace=namespace,
                label_selector=f"app={deployment_name}"
            )
            
            return {
                'name': deployment_name,
                'namespace': namespace,
                'replicas': deployment.spec.replicas,
                'ready_replicas': deployment.status.ready_replicas or 0,
                'updated_replicas': deployment.status.updated_replicas or 0,
                'available_replicas': deployment.status.available_replicas or 0,
                'total_pods': len(pods.items),
                'running_pods': len([p for p in pods.items if p.status.phase == 'Running']),
                'pending_pods': len([p for p in pods.items if p.status.phase == 'Pending']),
                'failed_pods': len([p for p in pods.items if p.status.phase in ['Failed', 'Error']]),
                'created_at': deployment.metadata.creation_timestamp.isoformat() if deployment.metadata.creation_timestamp else None,
                'conditions': [
                    {
                        'type': condition.type,
                        'status': condition.status,
                        'reason': condition.reason,
                        'message': condition.message
                    }
                    for condition in deployment.status.conditions or []
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting deployment status for {deployment_name}: {e}")
            return None
    
    def get_cluster_status(self) -> Dict[str, Any]:
        """Get overall cluster status"""
        try:
            # Get latest metrics
            with self.lock:
                latest_metrics = list(self.cluster_metrics)[-1] if self.cluster_metrics else None
            
            # Get all deployments
            deployments = []
            with self.lock:
                deployment_configs = list(self.deployments.values())
            
            for config in deployment_configs:
                status = self.get_deployment_status(config.name, config.namespace)
                if status:
                    deployments.append(status)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cluster_metrics': latest_metrics.to_dict() if latest_metrics else None,
                'deployments': deployments,
                'total_deployments': len(deployments),
                'healthy_deployments': len([
                    d for d in deployments
                    if d['ready_replicas'] == d['replicas']
                ]),
                'scaling_policies': len(self.scaling_policies),
                'recent_scaling_events': list(self.scaling_events)[-10:] if self.scaling_events else []
            }
            
        except Exception as e:
            logger.error(f"Error getting cluster status: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }

# Global orchestrator instance
kubernetes_orchestrator = KubernetesOrchestrator()

def deploy_application(name: str, namespace: str, image: str,
                      replicas: int = 3, resources: Dict[str, Dict[str, str]] = None,
                      env_vars: Dict[str, str] = None, ports: List[int] = None) -> bool:
    """Deploy application to Kubernetes"""
    config = DeploymentConfig(
        name=name,
        namespace=namespace,
        image=image,
        replicas=replicas,
        resources=resources or {},
        env_vars=env_vars or {},
        ports=ports or [],
        labels={'app': name, 'managed-by': 'kubernetes-orchestrator'}
    )
    
    return kubernetes_orchestrator.deploy_application(config)

def scale_deployment(deployment_name: str, namespace: str, replicas: int) -> bool:
    """Scale deployment to specified replica count"""
    return kubernetes_orchestrator.scale_deployment(deployment_name, namespace, replicas)

def create_autoscaler(deployment_name: str, namespace: str,
                     min_replicas: int = 1, max_replicas: int = 10,
                     target_cpu_utilization: int = 70) -> bool:
    """Create Horizontal Pod Autoscaler"""
    policy = ScalingPolicy(
        deployment_name=deployment_name,
        namespace=namespace,
        min_replicas=min_replicas,
        max_replicas=max_replicas,
        target_cpu_utilization=target_cpu_utilization
    )
    
    return kubernetes_orchestrator.create_horizontal_pod_autoscaler(policy)

def get_cluster_status() -> Dict[str, Any]:
    """Get cluster status"""
    return kubernetes_orchestrator.get_cluster_status()
