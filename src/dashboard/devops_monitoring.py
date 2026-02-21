#!/usr/bin/env python3
"""
DevOps Dashboard
CI/CD pipeline monitoring, code quality tracking, bug management, deployment history, and environment status
"""

import os
import sys
import time
import json
import logging
import threading
import subprocess
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from enum import Enum

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

class PipelineStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"

class EnvStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"

class CodeQualityLevel(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"

class BugSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class PipelineRun:
    """Pipeline run data structure"""
    run_id: str
    pipeline_name: str
    branch: str
    commit_hash: str
    commit_message: str
    author: str
    status: PipelineStatus
    started_at: datetime
    completed_at: Optional[datetime]
    duration_seconds: Optional[float]
    stages: List[Dict[str, Any]]
    artifacts: List[str]
    test_results: Dict[str, Any]
    coverage_percentage: float
    quality_score: float
    environment: str
    triggered_by: str

@dataclass
class CodeQualityMetrics:
    """Code quality metrics data structure"""
    repository: str
    branch: str
    commit_hash: str
    timestamp: datetime
    quality_level: CodeQualityLevel
    overall_score: float
    complexity_score: float
    maintainability_score: float
    reliability_score: float
    security_score: float
    test_coverage: float
    duplicate_code_percentage: float
    lines_of_code: int
    technical_debt_ratio: float
    code_smells: int
    vulnerabilities: int
    hotspots: int

@dataclass
class BugReport:
    """Bug report data structure"""
    bug_id: str
    title: str
    description: str
    severity: BugSeverity
    priority: str
    status: str  # open, in_progress, resolved, closed, wont_fix
    assigned_to: str
    reported_by: str
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]
    environment: str
    component: str
    reproduction_steps: List[str]
    expected_behavior: str
    actual_behavior: str
    attachments: List[str]
    labels: List[str]

@dataclass
class Deployment:
    """Deployment data structure"""
    deployment_id: str
    application: str
    version: str
    environment: str
    status: str  # in_progress, success, failed, rolled_back
    started_at: datetime
    completed_at: Optional[datetime]
    duration_seconds: Optional[float]
    deployed_by: str
    commit_hash: str
    branch: str
    rollback_version: Optional[str]
    health_check_status: str
    rollback_reason: Optional[str]
    deployment_strategy: str  # blue_green, canary, rolling
    affected_services: List[str]

@dataclass
class EnvironmentStatus:
    """Environment status data structure"""
    environment_name: str
    status: EnvStatus
    health_score: float
    uptime_percentage: float
    response_time_ms: float
    error_rate: float
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_throughput: float
    active_connections: int
    last_health_check: datetime
    services: List[Dict[str, Any]]
    incidents: List[Dict[str, Any]]

class DevOpsMonitoringSystem:
    """DevOps Monitoring System"""
    
    def __init__(self):
        self.logger = logging.getLogger("devops_monitoring_system")
        self.pipeline_runs = deque(maxlen=1000)  # Last 1000 pipeline runs
        self.code_quality_metrics = {}
        self.bug_reports = {}
        self.deployments = {}
        self.environment_statuses = {}
        self.monitoring_active = False
        self.monitoring_thread = None
        self.check_interval = 60  # 1 minute
        
        # CI/CD pipeline configuration
        self.pipelines = {
            "main_application": {
                "name": "Main Application Pipeline",
                "stages": ["build", "test", "security_scan", "quality_gate", "deploy"],
                "environments": ["development", "staging", "production"],
                "triggers": ["push", "pull_request", "scheduled"]
            },
            "microservices": {
                "name": "Microservices Pipeline",
                "stages": ["build", "unit_test", "integration_test", "security_scan", "deploy"],
                "environments": ["development", "staging", "production"],
                "triggers": ["push", "pull_request"]
            },
            "infrastructure": {
                "name": "Infrastructure Pipeline",
                "stages": ["validate", "plan", "apply", "test"],
                "environments": ["development", "staging", "production"],
                "triggers": ["push", "manual"]
            }
        }
        
        # Initialize with sample data
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize with sample DevOps data"""
        import random
        
        # Generate sample pipeline runs
        pipeline_names = list(self.pipelines.keys())
        branches = ["main", "develop", "feature/new-dashboard", "bugfix/security-patch", "hotfix/critical-bug"]
        statuses = [PipelineStatus.PENDING, PipelineStatus.RUNNING, PipelineStatus.SUCCESS, PipelineStatus.FAILED, PipelineStatus.CANCELLED]
        
        for i in range(50):
            pipeline_name = random.choice(pipeline_names)
            branch = random.choice(branches)
            status = random.choice(statuses)
            
            # Generate commit info
            commit_hash = hashlib.sha256(f"commit_{i}".encode()).hexdigest()[:8]
            commit_message = random.choice([
                "Add new dashboard features",
                "Fix security vulnerability",
                "Update dependencies",
                "Improve performance",
                "Add unit tests",
                "Refactor authentication module"
            ])
            
            # Calculate timing
            started_at = datetime.now() - timedelta(hours=random.randint(1, 168))  # Last week
            duration = random.uniform(300, 1800)  # 5-30 minutes
            
            if status in [PipelineStatus.SUCCESS, PipelineStatus.FAILED, PipelineStatus.CANCELLED]:
                completed_at = started_at + timedelta(seconds=duration)
            else:
                completed_at = None
                duration = None
            
            # Generate stages
            stages = []
            for stage in self.pipelines[pipeline_name]["stages"]:
                stage_status = random.choice(["success", "failed", "skipped"])
                stage_duration = random.uniform(30, 300)
                stages.append({
                    "name": stage,
                    "status": stage_status,
                    "duration_seconds": stage_duration,
                    "started_at": (started_at + timedelta(seconds=random.randint(0, 600))).isoformat(),
                    "completed_at": (started_at + timedelta(seconds=stage_duration)).isoformat()
                })
            
            pipeline_run = PipelineRun(
                run_id=f"run_{i+1}",
                pipeline_name=pipeline_name,
                branch=branch,
                commit_hash=commit_hash,
                commit_message=commit_message,
                author=f"developer_{random.randint(1, 20)}",
                status=status,
                started_at=started_at,
                completed_at=completed_at,
                duration_seconds=duration,
                stages=stages,
                artifacts=[f"artifact_{j}" for j in range(random.randint(1, 5))],
                test_results={
                    "total_tests": random.randint(100, 1000),
                    "passed_tests": random.randint(80, 950),
                    "failed_tests": random.randint(0, 50),
                    "skipped_tests": random.randint(0, 20)
                },
                coverage_percentage=random.uniform(60, 95),
                quality_score=random.uniform(70, 95),
                environment=random.choice(["development", "staging", "production"]),
                triggered_by=random.choice(["push", "pull_request", "scheduled", "manual"])
            )
            
            self.pipeline_runs.append(pipeline_run)
        
        # Generate sample code quality metrics
        repositories = ["main_application", "microservices", "infrastructure"]
        quality_levels = [CodeQualityLevel.EXCELLENT, CodeQualityLevel.GOOD, CodeQualityLevel.FAIR, CodeQualityLevel.POOR, CodeQualityLevel.CRITICAL]
        
        for repo in repositories:
            for i in range(10):
                commit_hash = hashlib.sha256(f"quality_{repo}_{i}".encode()).hexdigest()[:8]
                
                quality_metrics = CodeQualityMetrics(
                    repository=repo,
                    branch=random.choice(branches),
                    commit_hash=commit_hash,
                    timestamp=datetime.now() - timedelta(days=random.randint(1, 30)),
                    quality_level=random.choice(quality_levels),
                    overall_score=random.uniform(60, 95),
                    complexity_score=random.uniform(20, 80),
                    maintainability_score=random.uniform(60, 95),
                    reliability_score=random.uniform(70, 95),
                    security_score=random.uniform(80, 100),
                    test_coverage=random.uniform(60, 90),
                    duplicate_code_percentage=random.uniform(0, 15),
                    lines_of_code=random.randint(10000, 100000),
                    technical_debt_ratio=random.uniform(0, 10),
                    code_smells=random.randint(0, 50),
                    vulnerabilities=random.randint(0, 10),
                    hotspots=random.randint(0, 5)
                )
                
                self.code_quality_metrics[f"{repo}_{commit_hash}"] = quality_metrics
        
        # Generate sample bug reports
        components = ["authentication", "dashboard", "api", "database", "ui", "security"]
        bug_statuses = ["open", "in_progress", "resolved", "closed"]
        severities = [BugSeverity.LOW, BugSeverity.MEDIUM, BugSeverity.HIGH, BugSeverity.CRITICAL]
        
        for i in range(30):
            bug_id = f"BUG-{i+1:04d}"
            
            bug_report = BugReport(
                bug_id=bug_id,
                title=random.choice([
                    "Login fails on mobile devices",
                    "Dashboard charts not loading",
                    "API response timeout",
                    "Memory leak in background process",
                    "Security vulnerability in authentication",
                    "Performance degradation under load"
                ]),
                description=f"Detailed description of bug {bug_id}",
                severity=random.choice(severities),
                priority=random.choice(["low", "medium", "high", "critical"]),
                status=random.choice(bug_statuses),
                assigned_to=f"developer_{random.randint(1, 20)}",
                reported_by=f"user_{random.randint(1, 50)}",
                created_at=datetime.now() - timedelta(days=random.randint(1, 60)),
                updated_at=datetime.now() - timedelta(hours=random.randint(1, 168)),
                resolved_at=datetime.now() - timedelta(days=random.randint(1, 30)) if random.choice([True, False]) else None,
                environment=random.choice(["development", "staging", "production"]),
                component=random.choice(components),
                reproduction_steps=[
                    "Step 1: Navigate to login page",
                    "Step 2: Enter credentials",
                    "Step 3: Click login button"
                ],
                expected_behavior="User should be logged in successfully",
                actual_behavior="Login fails with error message",
                attachments=[f"screenshot_{i}.png"] if random.choice([True, False]) else [],
                labels=random.sample(["bug", "urgent", "security", "performance", "ui"], random.randint(1, 3))
            )
            
            self.bug_reports[bug_id] = bug_report
        
        # Generate sample deployments
        applications = ["main_application", "microservices", "infrastructure"]
        deployment_statuses = ["in_progress", "success", "failed", "rolled_back"]
        strategies = ["blue_green", "canary", "rolling"]
        
        for i in range(20):
            deployment_id = f"deploy_{i+1}"
            app = random.choice(applications)
            
            deployment = Deployment(
                deployment_id=deployment_id,
                application=app,
                version=f"v{random.randint(1, 10)}.{random.randint(0, 20)}.{random.randint(0, 50)}",
                environment=random.choice(["development", "staging", "production"]),
                status=random.choice(deployment_statuses),
                started_at=datetime.now() - timedelta(hours=random.randint(1, 168)),
                completed_at=datetime.now() - timedelta(minutes=random.randint(10, 120)) if random.choice([True, False]) else None,
                duration_seconds=random.uniform(300, 1800) if random.choice([True, False]) else None,
                deployed_by=f"deployer_{random.randint(1, 5)}",
                commit_hash=hashlib.sha256(f"deploy_{i}".encode()).hexdigest()[:8],
                branch=random.choice(branches),
                rollback_version=f"v{random.randint(1, 5)}.{random.randint(0, 10)}.{random.randint(0, 20)}" if random.choice([True, False]) else None,
                health_check_status=random.choice(["healthy", "degraded", "unhealthy"]),
                rollback_reason=random.choice(["Performance degradation", "Critical bug", "Security issue"]) if random.choice([True, False]) else None,
                deployment_strategy=random.choice(strategies),
                affected_services=random.sample(["api", "web", "database", "cache"], random.randint(1, 3))
            )
            
            self.deployments[deployment_id] = deployment
        
        # Generate sample environment statuses
        environments = ["development", "staging", "production"]
        env_statuses = [EnvStatus.HEALTHY, EnvStatus.DEGRADED, EnvStatus.UNHEALTHY, EnvStatus.MAINTENANCE]
        
        for env in environments:
            status = EnvStatus.HEALTHY if env == "production" else random.choice(env_statuses)
            
            environment_status = EnvironmentStatus(
                environment_name=env,
                status=status,
                health_score=random.uniform(70, 100) if status == EnvStatus.HEALTHY else random.uniform(30, 70),
                uptime_percentage=random.uniform(95, 100),
                response_time_ms=random.uniform(100, 500),
                error_rate=random.uniform(0, 5),
                cpu_usage=random.uniform(20, 80),
                memory_usage=random.uniform(30, 85),
                disk_usage=random.uniform(40, 90),
                network_throughput=random.uniform(1000000, 10000000),
                active_connections=random.randint(50, 500),
                last_health_check=datetime.now() - timedelta(minutes=random.randint(1, 60)),
                services=[
                    {
                        "name": "web_server",
                        "status": "running",
                        "cpu_usage": random.uniform(10, 60),
                        "memory_usage": random.uniform(20, 70)
                    },
                    {
                        "name": "database",
                        "status": "running",
                        "cpu_usage": random.uniform(20, 80),
                        "memory_usage": random.uniform(40, 90)
                    },
                    {
                        "name": "cache",
                        "status": "running",
                        "cpu_usage": random.uniform(5, 30),
                        "memory_usage": random.uniform(10, 50)
                    }
                ],
                incidents=[
                    {
                        "incident_id": f"incident_{env}_{i}",
                        "type": "performance_degradation",
                        "severity": random.choice(["low", "medium", "high"]),
                        "created_at": (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat(),
                        "resolved_at": (datetime.now() - timedelta(minutes=random.randint(10, 120))).isoformat() if random.choice([True, False]) else None
                    } for i in range(random.randint(0, 3))
                ]
            )
            
            self.environment_statuses[env] = environment_status
        
        self.logger.info(f"Initialized DevOps monitoring system with {len(self.pipeline_runs)} pipeline runs, {len(self.code_quality_metrics)} code quality metrics, {len(self.bug_reports)} bug reports, {len(self.deployments)} deployments, and {len(self.environment_statuses)} environment statuses")
    
    def start_monitoring(self):
        """Start DevOps monitoring"""
        if self.monitoring_active:
            self.logger.warning("DevOps monitoring is already running")
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        self.logger.info("DevOps monitoring started")
    
    def stop_monitoring(self):
        """Stop DevOps monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=10)
        self.logger.info("DevOps monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Update environment statuses
                self._update_environment_statuses()
                
                # Simulate pipeline runs
                self._simulate_pipeline_runs()
                
                # Update code quality metrics
                self._update_code_quality_metrics()
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                self.logger.error(f"Error in DevOps monitoring loop: {e}")
                time.sleep(30)  # Wait 30 seconds before retrying
    
    def _update_environment_statuses(self):
        """Update environment statuses"""
        import random
        
        for env_name, env_status in self.environment_statuses.items():
            # Simulate health check
            env_status.last_health_check = datetime.now()
            
            # Update metrics with small variations
            env_status.cpu_usage = max(0, min(100, env_status.cpu_usage + random.uniform(-5, 5)))
            env_status.memory_usage = max(0, min(100, env_status.memory_usage + random.uniform(-3, 3)))
            env_status.response_time_ms = max(0, env_status.response_time_ms + random.uniform(-50, 100))
            env_status.error_rate = max(0, min(100, env_status.error_rate + random.uniform(-0.5, 2)))
            
            # Update service statuses
            for service in env_status.services:
                service["cpu_usage"] = max(0, min(100, service["cpu_usage"] + random.uniform(-10, 10)))
                service["memory_usage"] = max(0, min(100, service["memory_usage"] + random.uniform(-5, 5)))
            
            # Update health score based on metrics
            if env_status.cpu_usage > 90 or env_status.memory_usage > 90 or env_status.error_rate > 10:
                env_status.status = EnvStatus.DEGRADED
                env_status.health_score = max(0, env_status.health_score - 10)
            elif env_status.cpu_usage > 95 or env_status.memory_usage > 95 or env_status.error_rate > 20:
                env_status.status = EnvStatus.UNHEALTHY
                env_status.health_score = max(0, env_status.health_score - 20)
            else:
                env_status.status = EnvStatus.HEALTHY
                env_status.health_score = min(100, env_status.health_score + 5)
    
    def _simulate_pipeline_runs(self):
        """Simulate new pipeline runs"""
        import random
        
        # 10% chance of new pipeline run
        if random.random() > 0.9:
            pipeline_name = random.choice(list(self.pipelines.keys()))
            branches = ["main", "develop", "feature/new-dashboard"]
            
            run_id = f"run_{int(time.time())}"
            branch = random.choice(branches)
            
            # Create new pipeline run
            pipeline_run = PipelineRun(
                run_id=run_id,
                pipeline_name=pipeline_name,
                branch=branch,
                commit_hash=hashlib.sha256(f"commit_{time.time()}".encode()).hexdigest()[:8],
                commit_message="Latest commit",
                author=f"developer_{random.randint(1, 20)}",
                status=PipelineStatus.RUNNING,
                started_at=datetime.now(),
                completed_at=None,
                duration_seconds=None,
                stages=[
                    {
                        "name": stage,
                        "status": "running" if i == 0 else "pending",
                        "duration_seconds": None,
                        "started_at": datetime.now().isoformat() if i == 0 else None,
                        "completed_at": None
                    }
                    for i, stage in enumerate(self.pipelines[pipeline_name]["stages"])
                ],
                artifacts=[],
                test_results={},
                coverage_percentage=0,
                quality_score=0,
                environment="development",
                triggered_by="push"
            )
            
            self.pipeline_runs.append(pipeline_run)
    
    def _update_code_quality_metrics(self):
        """Update code quality metrics"""
        import random
        
        # 5% chance of new code quality metrics
        if random.random() > 0.95:
            repo = random.choice(list(self.pipelines.keys()))
            commit_hash = hashlib.sha256(f"quality_{time.time()}".encode()).hexdigest()[:8]
            
            quality_metrics = CodeQualityMetrics(
                repository=repo,
                branch="main",
                commit_hash=commit_hash,
                timestamp=datetime.now(),
                quality_level=random.choice([CodeQualityLevel.EXCELLENT, CodeQualityLevel.GOOD, CodeQualityLevel.FAIR, CodeQualityLevel.POOR, CodeQualityLevel.CRITICAL]),
                overall_score=random.uniform(70, 95),
                complexity_score=random.uniform(20, 80),
                maintainability_score=random.uniform(60, 95),
                reliability_score=random.uniform(70, 95),
                security_score=random.uniform(80, 100),
                test_coverage=random.uniform(60, 90),
                duplicate_code_percentage=random.uniform(0, 15),
                lines_of_code=random.randint(10000, 100000),
                technical_debt_ratio=random.uniform(0, 10),
                code_smells=random.randint(0, 50),
                vulnerabilities=random.randint(0, 10),
                hotspots=random.randint(0, 5)
            )
            
            self.code_quality_metrics[f"{repo}_{commit_hash}"] = quality_metrics
    
    def get_pipeline_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get pipeline summary for specified time period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_runs = [run for run in self.pipeline_runs if run.started_at >= cutoff_time]
        
        # Count by status
        status_counts = defaultdict(int)
        for run in recent_runs:
            status_counts[run.status.value] += 1
        
        # Count by pipeline
        pipeline_counts = defaultdict(int)
        for run in recent_runs:
            pipeline_counts[run.pipeline_name] += 1
        
        # Calculate success rate
        total_runs = len(recent_runs)
        successful_runs = len([run for run in recent_runs if run.status == PipelineStatus.SUCCESS])
        success_rate = (successful_runs / total_runs * 100) if total_runs > 0 else 0
        
        # Calculate average duration
        completed_runs = [run for run in recent_runs if run.duration_seconds is not None]
        avg_duration = sum(run.duration_seconds for run in completed_runs) / len(completed_runs) if completed_runs else 0
        
        # Get recent failures
        recent_failures = [
            {
                "run_id": run.run_id,
                "pipeline_name": run.pipeline_name,
                "branch": run.branch,
                "commit_hash": run.commit_hash,
                "failed_at": run.completed_at.isoformat() if run.completed_at else None,
                "failure_reason": "Stage failed"  # Would extract from actual failure
            }
            for run in recent_runs
            if run.status == PipelineStatus.FAILED
        ][:10]
        
        return {
            "period_hours": hours,
            "total_runs": total_runs,
            "successful_runs": successful_runs,
            "success_rate": round(success_rate, 2),
            "average_duration_seconds": round(avg_duration, 2),
            "status_distribution": dict(status_counts),
            "pipeline_distribution": dict(pipeline_counts),
            "recent_failures": recent_failures,
            "last_updated": datetime.now().isoformat()
        }
    
    def get_code_quality_summary(self) -> Dict[str, Any]:
        """Get code quality summary"""
        if not self.code_quality_metrics:
            return {
                "total_repositories": 0,
                "overall_quality_score": 0,
                "quality_distribution": {},
                "last_updated": datetime.now().isoformat()
            }
        
        # Get latest metrics for each repository
        latest_metrics = {}
        for key, metrics in self.code_quality_metrics.items():
            repo = metrics.repository
            if repo not in latest_metrics or metrics.timestamp > latest_metrics[repo].timestamp:
                latest_metrics[repo] = metrics
        
        # Calculate overall scores
        total_repos = len(latest_metrics)
        overall_quality_score = sum(m.overall_score for m in latest_metrics.values()) / total_repos if total_repos > 0 else 0
        overall_coverage = sum(m.test_coverage for m in latest_metrics.values()) / total_repos if total_repos > 0 else 0
        
        # Count by quality level
        quality_counts = defaultdict(int)
        for metrics in latest_metrics.values():
            quality_counts[metrics.quality_level.value] += 1
        
        # Calculate totals
        total_vulnerabilities = sum(m.vulnerabilities for m in latest_metrics.values())
        total_code_smells = sum(m.code_smells for m in latest_metrics.values())
        total_hotspots = sum(m.hotspots for m in latest_metrics.values())
        total_lines_of_code = sum(m.lines_of_code for m in latest_metrics.values())
        
        return {
            "total_repositories": total_repos,
            "overall_quality_score": round(overall_quality_score, 2),
            "overall_test_coverage": round(overall_coverage, 2),
            "quality_distribution": dict(quality_counts),
            "total_vulnerabilities": total_vulnerabilities,
            "total_code_smells": total_code_smells,
            "total_hotspots": total_hotspots,
            "total_lines_of_code": total_lines_of_code,
            "repository_scores": {
                repo: {
                    "quality_score": round(metrics.overall_score, 2),
                    "test_coverage": round(metrics.test_coverage, 2),
                    "vulnerabilities": metrics.vulnerabilities,
                    "code_smells": metrics.code_smells
                }
                for repo, metrics in latest_metrics.items()
            },
            "last_updated": datetime.now().isoformat()
        }
    
    def get_bug_summary(self) -> Dict[str, Any]:
        """Get bug summary"""
        total_bugs = len(self.bug_reports)
        
        # Count by status
        status_counts = defaultdict(int)
        for bug in self.bug_reports.values():
            status_counts[bug.status] += 1
        
        # Count by severity
        severity_counts = defaultdict(int)
        for bug in self.bug_reports.values():
            severity_counts[bug.severity.value] += 1
        
        # Count by component
        component_counts = defaultdict(int)
        for bug in self.bug_reports.values():
            component_counts[bug.component] += 1
        
        # Get recent bugs (last 7 days)
        recent_bugs = [
            bug for bug in self.bug_reports.values()
            if datetime.now() - bug.created_at < timedelta(days=7)
        ]
        
        # Get resolved bugs (last 7 days)
        resolved_bugs = [
            bug for bug in self.bug_reports.values()
            if bug.resolved_at and datetime.now() - bug.resolved_at < timedelta(days=7)
        ]
        
        # Calculate average resolution time
        resolved_with_time = [
            bug for bug in self.bug_reports.values()
            if bug.resolved_at
        ]
        
        if resolved_with_time:
            avg_resolution_time = sum(
                (bug.resolved_at - bug.created_at).total_seconds() / 3600
                for bug in resolved_with_time
            ) / len(resolved_with_time)
        else:
            avg_resolution_time = 0
        
        return {
            "total_bugs": total_bugs,
            "open_bugs": status_counts.get("open", 0),
            "in_progress_bugs": status_counts.get("in_progress", 0),
            "resolved_bugs": status_counts.get("resolved", 0),
            "closed_bugs": status_counts.get("closed", 0),
            "recent_bugs": len(recent_bugs),
            "recently_resolved": len(resolved_bugs),
            "average_resolution_hours": round(avg_resolution_time, 2),
            "status_distribution": dict(status_counts),
            "severity_distribution": dict(severity_counts),
            "component_distribution": dict(component_counts),
            "last_updated": datetime.now().isoformat()
        }
    
    def get_deployment_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get deployment summary for specified time period"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_deployments = [
            deploy for deploy in self.deployments.values()
            if deploy.started_at >= cutoff_date
        ]
        
        # Count by status
        status_counts = defaultdict(int)
        for deploy in recent_deployments:
            status_counts[deploy.status] += 1
        
        # Count by environment
        env_counts = defaultdict(int)
        for deploy in recent_deployments:
            env_counts[deploy.environment] += 1
        
        # Count by strategy
        strategy_counts = defaultdict(int)
        for deploy in recent_deployments:
            strategy_counts[deploy.deployment_strategy] += 1
        
        # Calculate success rate
        total_deployments = len(recent_deployments)
        successful_deployments = len([d for d in recent_deployments if d.status == "success"])
        success_rate = (successful_deployments / total_deployments * 100) if total_deployments > 0 else 0
        
        # Calculate average deployment time
        completed_deployments = [d for d in recent_deployments if d.duration_seconds is not None]
        avg_deployment_time = sum(d.duration_seconds for d in completed_deployments) / len(completed_deployments) if completed_deployments else 0
        
        # Get recent deployments
        recent_deployments_list = [
            {
                "deployment_id": deploy.deployment_id,
                "application": deploy.application,
                "version": deploy.version,
                "environment": deploy.environment,
                "status": deploy.status,
                "started_at": deploy.started_at.isoformat(),
                "duration_seconds": deploy.duration_seconds,
                "deployed_by": deploy.deployed_by
            }
            for deploy in sorted(recent_deployments, key=lambda x: x.started_at, reverse=True)
        ][:10]
        
        return {
            "period_days": days,
            "total_deployments": total_deployments,
            "successful_deployments": successful_deployments,
            "success_rate": round(success_rate, 2),
            "average_deployment_time_seconds": round(avg_deployment_time, 2),
            "status_distribution": dict(status_counts),
            "environment_distribution": dict(env_counts),
            "strategy_distribution": dict(strategy_counts),
            "recent_deployments": recent_deployments_list,
            "last_updated": datetime.now().isoformat()
        }
    
    def get_environment_summary(self) -> Dict[str, Any]:
        """Get environment summary"""
        environments = {}
        
        for env_name, env_status in self.environment_statuses.items():
            # Calculate service health
            healthy_services = len([s for s in env_status.services if s["status"] == "running"])
            total_services = len(env_status.services)
            service_health_percentage = (healthy_services / total_services * 100) if total_services > 0 else 0
            
            # Count active incidents
            active_incidents = len([i for i in env_status.incidents if i["resolved_at"] is None])
            
            environments[env_name] = {
                "status": env_status.status.value,
                "health_score": round(env_status.health_score, 2),
                "uptime_percentage": round(env_status.uptime_percentage, 2),
                "response_time_ms": round(env_status.response_time_ms, 2),
                "error_rate": round(env_status.error_rate, 2),
                "cpu_usage": round(env_status.cpu_usage, 2),
                "memory_usage": round(env_status.memory_usage, 2),
                "disk_usage": round(env_status.disk_usage, 2),
                "active_connections": env_status.active_connections,
                "service_health_percentage": round(service_health_percentage, 2),
                "active_incidents": active_incidents,
                "last_health_check": env_status.last_health_check.isoformat(),
                "services": env_status.services
            }
        
        return {
            "environments": environments,
            "total_environments": len(environments),
            "healthy_environments": len([e for e in environments.values() if e["status"] == "healthy"]),
            "last_updated": datetime.now().isoformat()
        }

# Global DevOps monitoring system instance
devops_monitoring_system = DevOpsMonitoringSystem()
