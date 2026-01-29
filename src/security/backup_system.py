"""
Helm AI Backup System
This module provides comprehensive backup and restore functionality
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import hashlib
import gzip
import shutil
import subprocess
import threading
import time
import boto3
from botocore.exceptions import ClientError

from .encryption import encryption_manager, DataClassification

logger = logging.getLogger(__name__)

class BackupType(Enum):
    """Backup types"""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"

class BackupStatus(Enum):
    """Backup status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CORRUPTED = "corrupted"

class StorageType(Enum):
    """Storage types"""
    LOCAL = "local"
    S3 = "s3"
    GCS = "gcs"
    AZURE_BLOB = "azure_blob"

@dataclass
class BackupJob:
    """Backup job definition"""
    job_id: str
    name: str
    backup_type: BackupType
    source_paths: List[str]
    destination_type: StorageType
    destination_config: Dict[str, Any]
    schedule: str  # cron expression
    retention_days: int
    encryption_enabled: bool = True
    compression_enabled: bool = True
    classification: DataClassification = DataClassification.INTERNAL
    created_at: datetime = field(default_factory=datetime.now)
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    status: BackupStatus = BackupStatus.PENDING
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BackupResult:
    """Backup execution result"""
    backup_id: str
    job_id: str
    backup_type: BackupType
    status: BackupStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    files_backed_up: int = 0
    total_size_bytes: int = 0
    compressed_size_bytes: int = 0
    backup_path: str = None
    checksum: str = None
    error_message: str = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class BackupManager:
    """Comprehensive backup management system"""
    
    def __init__(self):
        self.jobs: Dict[str, BackupJob] = {}
        self.results: Dict[str, BackupResult] = {}
        self.running_backups: Dict[str, threading.Thread] = {}
        
        # Configuration
        self.backup_dir = os.getenv('BACKUP_DIR', '/var/backups/helm-ai')
        self.max_concurrent_backups = int(os.getenv('MAX_CONCURRENT_BACKUPS', '3'))
        self.default_retention_days = int(os.getenv('DEFAULT_RETENTION_DAYS', '30'))
        
        # Initialize storage backends
        self.s3_client = None
        if os.getenv('AWS_BACKUP_BUCKET'):
            self.s3_client = boto3.client('s3')
            self.s3_bucket = os.getenv('AWS_BACKUP_BUCKET')
        
        # Create backup directory
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Load existing jobs
        self._load_backup_jobs()
        
        # Start scheduler
        self._start_scheduler()
    
    def _load_backup_jobs(self):
        """Load backup jobs from configuration"""
        # Database backup job
        self.create_backup_job(
            name="database_backup",
            backup_type=BackupType.FULL,
            source_paths=["/var/lib/postgresql", "/var/lib/redis"],
            destination_type=StorageType.S3 if self.s3_client else StorageType.LOCAL,
            destination_config={"bucket": self.s3_bucket} if self.s3_client else {"path": f"{self.backup_dir}/database"},
            schedule="0 2 * * *",  # Daily at 2 AM
            retention_days=30,
            classification=DataClassification.CONFIDENTIAL
        )
        
        # Application data backup job
        self.create_backup_job(
            name="application_backup",
            backup_type=BackupType.INCREMENTAL,
            source_paths=["/opt/helm-ai/data", "/opt/helm-ai/config"],
            destination_type=StorageType.S3 if self.s3_client else StorageType.LOCAL,
            destination_config={"bucket": self.s3_bucket} if self.s3_client else {"path": f"{self.backup_dir}/application"},
            schedule="0 3 * * *",  # Daily at 3 AM
            retention_days=14,
            classification=DataClassification.INTERNAL
        )
        
        # User data backup job
        self.create_backup_job(
            name="user_data_backup",
            backup_type=BackupType.FULL,
            source_paths=["/opt/helm-ai/user_data"],
            destination_type=StorageType.S3 if self.s3_client else StorageType.LOCAL,
            destination_config={"bucket": self.s3_bucket} if self.s3_client else {"path": f"{self.backup_dir}/user_data"},
            schedule="0 4 * * 0",  # Weekly on Sunday at 4 AM
            retention_days=90,
            classification=DataClassification.RESTRICTED
        )
    
    def create_backup_job(self, 
                         name: str,
                         backup_type: BackupType,
                         source_paths: List[str],
                         destination_type: StorageType,
                         destination_config: Dict[str, Any],
                         schedule: str,
                         retention_days: int = None,
                         encryption_enabled: bool = True,
                         compression_enabled: bool = True,
                         classification: DataClassification = DataClassification.INTERNAL) -> BackupJob:
        """Create new backup job"""
        job_id = f"job_{name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        job = BackupJob(
            job_id=job_id,
            name=name,
            backup_type=backup_type,
            source_paths=source_paths,
            destination_type=destination_type,
            destination_config=destination_config,
            schedule=schedule,
            retention_days=retention_days or self.default_retention_days,
            encryption_enabled=encryption_enabled,
            compression_enabled=compression_enabled,
            classification=classification
        )
        
        self.jobs[job_id] = job
        
        logger.info(f"Created backup job: {name} ({job_id})")
        return job
    
    def run_backup_job(self, job_id: str) -> BackupResult:
        """Execute backup job"""
        job = self.jobs.get(job_id)
        if not job:
            raise ValueError(f"Backup job {job_id} not found")
        
        # Check concurrent backup limit
        if len(self.running_backups) >= self.max_concurrent_backups:
            raise Exception("Maximum concurrent backups reached")
        
        # Create backup result
        backup_id = f"backup_{job_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        result = BackupResult(
            backup_id=backup_id,
            job_id=job_id,
            backup_type=job.backup_type,
            status=BackupStatus.IN_PROGRESS,
            started_at=datetime.now()
        )
        
        self.results[backup_id] = result
        
        # Update job status
        job.status = BackupStatus.IN_PROGRESS
        job.last_run = datetime.now()
        
        # Run backup in background thread
        backup_thread = threading.Thread(
            target=self._execute_backup,
            args=(job, result),
            daemon=True
        )
        
        self.running_backups[backup_id] = backup_thread
        backup_thread.start()
        
        return result
    
    def _execute_backup(self, job: BackupJob, result: BackupResult):
        """Execute backup operation"""
        try:
            logger.info(f"Starting backup job: {job.name}")
            
            # Create backup directory
            backup_date = datetime.now().strftime('%Y%m%d')
            backup_filename = f"{job.name}_{backup_date}_{result.backup_id}.tar"
            
            if job.destination_type == StorageType.LOCAL:
                backup_path = os.path.join(job.destination_config["path"], backup_filename)
                os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            else:
                backup_path = f"/tmp/{backup_filename}"
            
            # Create tar archive
            tar_command = ["tar", "-cf", backup_path]
            
            # Add source paths
            for source_path in job.source_paths:
                if os.path.exists(source_path):
                    tar_command.append(source_path)
                else:
                    logger.warning(f"Source path does not exist: {source_path}")
            
            # Execute tar command
            subprocess.run(tar_command, check=True)
            
            # Get backup size
            result.total_size_bytes = os.path.getsize(backup_path)
            result.files_backed_up = self._count_files(job.source_paths)
            
            # Compress if enabled
            if job.compression_enabled:
                compressed_path = backup_path + ".gz"
                with open(backup_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                os.remove(backup_path)
                backup_path = compressed_path
                result.compressed_size_bytes = os.path.getsize(backup_path)
            
            # Encrypt if enabled
            if job.encryption_enabled:
                encrypted_path = backup_path + ".enc"
                
                with open(backup_path, 'rb') as f:
                    data = f.read()
                
                encrypt_result = encryption_manager.encrypt_data(
                    data,
                    classification=job.classification
                )
                
                if encrypt_result.success:
                    with open(encrypted_path, 'wb') as f:
                        f.write(encrypt_result.encrypted_data)
                    
                    os.remove(backup_path)
                    backup_path = encrypted_path
                else:
                    raise Exception(f"Encryption failed: {encrypt_result.error}")
            
            # Calculate checksum
            result.checksum = self._calculate_checksum(backup_path)
            
            # Store backup
            if job.destination_type == StorageType.S3:
                self._store_to_s3(backup_path, job, result)
            elif job.destination_type == StorageType.LOCAL:
                result.backup_path = backup_path
            
            # Update result
            result.status = BackupStatus.COMPLETED
            result.completed_at = datetime.now()
            
            # Update job status
            job.status = BackupStatus.COMPLETED
            
            logger.info(f"Backup completed successfully: {result.backup_id}")
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            result.status = BackupStatus.FAILED
            result.error_message = str(e)
            result.completed_at = datetime.now()
            job.status = BackupStatus.FAILED
        
        finally:
            # Clean up running backup
            if result.backup_id in self.running_backups:
                del self.running_backups[result.backup_id]
    
    def _count_files(self, source_paths: List[str]) -> int:
        """Count files in source paths"""
        total_files = 0
        
        for source_path in source_paths:
            if os.path.exists(source_path):
                for root, dirs, files in os.walk(source_path):
                    total_files += len(files)
        
        return total_files
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate SHA-256 checksum of file"""
        hash_sha256 = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    
    def _store_to_s3(self, backup_path: str, job: BackupJob, result: BackupResult):
        """Store backup to S3"""
        try:
            # Create S3 key
            backup_date = datetime.now().strftime('%Y/%m/%d')
            s3_key = f"backups/{job.name}/{backup_date}/{os.path.basename(backup_path)}"
            
            # Upload to S3
            self.s3_client.upload_file(
                backup_path,
                self.s3_bucket,
                s3_key,
                ExtraArgs={
                    'ServerSideEncryption': 'AES256',
                    'Metadata': {
                        'backup_id': result.backup_id,
                        'job_id': job.job_id,
                        'backup_type': job.backup_type.value,
                        'checksum': result.checksum
                    }
                }
            )
            
            result.backup_path = f"s3://{self.s3_bucket}/{s3_key}"
            
            # Clean up local file
            os.remove(backup_path)
            
        except ClientError as e:
            raise Exception(f"S3 upload failed: {e}")
    
    def restore_backup(self, backup_id: str, restore_path: str) -> bool:
        """Restore backup from storage"""
        try:
            result = self.results.get(backup_id)
            if not result:
                raise ValueError(f"Backup {backup_id} not found")
            
            job = self.jobs.get(result.job_id)
            if not job:
                raise ValueError(f"Backup job {result.job_id} not found")
            
            # Download backup if stored remotely
            if result.backup_path.startswith("s3://"):
                local_backup_path = self._download_from_s3(result.backup_path)
            else:
                local_backup_path = result.backup_path
            
            # Verify checksum
            if not self._verify_checksum(local_backup_path, result.checksum):
                raise Exception("Backup checksum verification failed")
            
            # Decrypt if encrypted
            if local_backup_path.endswith(".enc"):
                decrypted_path = local_backup_path[:-4]  # Remove .enc extension
                
                with open(local_backup_path, 'rb') as f:
                    encrypted_data = f.read()
                
                decrypt_result = encryption_manager.decrypt_data(
                    type('DecryptResult', (), {
                        'success': True,
                        'encrypted_data': encrypted_data,
                        'key_id': None,
                        'algorithm': None
                    })()
                )
                
                if decrypt_result.success:
                    with open(decrypted_path, 'wb') as f:
                        f.write(decrypt_result.encrypted_data)
                    
                    os.remove(local_backup_path)
                    local_backup_path = decrypted_path
                else:
                    raise Exception(f"Decryption failed: {decrypt_result.error}")
            
            # Decompress if compressed
            if local_backup_path.endswith(".gz"):
                decompressed_path = local_backup_path[:-3]  # Remove .gz extension
                
                with gzip.open(local_backup_path, 'rb') as f_in:
                    with open(decompressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                os.remove(local_backup_path)
                local_backup_path = decompressed_path
            
            # Extract archive
            os.makedirs(restore_path, exist_ok=True)
            subprocess.run(["tar", "-xf", local_backup_path, "-C", restore_path], check=True)
            
            # Clean up
            if os.path.exists(local_backup_path):
                os.remove(local_backup_path)
            
            logger.info(f"Backup restored successfully: {backup_id} -> {restore_path}")
            return True
            
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False
    
    def _download_from_s3(self, s3_path: str) -> str:
        """Download backup from S3"""
        # Parse S3 path
        if s3_path.startswith("s3://"):
            s3_path = s3_path[5:]  # Remove s3://
        
        bucket, key = s3_path.split("/", 1)
        local_path = f"/tmp/{os.path.basename(key)}"
        
        # Download from S3
        self.s3_client.download_file(bucket, key, local_path)
        
        return local_path
    
    def _verify_checksum(self, file_path: str, expected_checksum: str) -> bool:
        """Verify file checksum"""
        actual_checksum = self._calculate_checksum(file_path)
        return actual_checksum == expected_checksum
    
    def list_backups(self, job_id: str = None, status: BackupStatus = None) -> List[BackupResult]:
        """List backups with optional filters"""
        backups = list(self.results.values())
        
        if job_id:
            backups = [b for b in backups if b.job_id == job_id]
        
        if status:
            backups = [b for b in backups if b.status == status]
        
        # Sort by started_at (most recent first)
        backups.sort(key=lambda x: x.started_at, reverse=True)
        
        return backups
    
    def get_backup_jobs(self) -> List[BackupJob]:
        """Get all backup jobs"""
        return list(self.jobs.values())
    
    def delete_backup(self, backup_id: str) -> bool:
        """Delete backup"""
        try:
            result = self.results.get(backup_id)
            if not result:
                return False
            
            # Delete from storage
            if result.backup_path:
                if result.backup_path.startswith("s3://"):
                    self._delete_from_s3(result.backup_path)
                else:
                    if os.path.exists(result.backup_path):
                        os.remove(result.backup_path)
            
            # Remove from results
            del self.results[backup_id]
            
            logger.info(f"Backup deleted: {backup_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete backup {backup_id}: {e}")
            return False
    
    def _delete_from_s3(self, s3_path: str):
        """Delete backup from S3"""
        if s3_path.startswith("s3://"):
            s3_path = s3_path[5:]
        
        bucket, key = s3_path.split("/", 1)
        self.s3_client.delete_object(Bucket=bucket, Key=key)
    
    def cleanup_old_backups(self):
        """Clean up backups older than retention period"""
        try:
            current_time = datetime.now()
            backups_to_delete = []
            
            for backup_id, result in self.results.items():
                job = self.jobs.get(result.job_id)
                if not job:
                    continue
                
                # Check if backup is older than retention period
                if current_time - result.started_at > timedelta(days=job.retention_days):
                    backups_to_delete.append(backup_id)
            
            # Delete old backups
            for backup_id in backups_to_delete:
                self.delete_backup(backup_id)
            
            logger.info(f"Cleaned up {len(backups_to_delete)} old backups")
            
        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}")
    
    def _start_scheduler(self):
        """Start backup scheduler"""
        def run_scheduler():
            while True:
                try:
                    current_time = datetime.now()
                    
                    # Check each job's schedule
                    for job_id, job in self.jobs.items():
                        if self._should_run_backup(job, current_time):
                            self.run_backup_job(job_id)
                    
                    # Run cleanup at 1 AM daily
                    if current_time.hour == 1 and current_time.minute == 0:
                        self.cleanup_old_backups()
                    
                    # Wait 1 minute before next check
                    time.sleep(60)
                except Exception as e:
                    logger.error(f"Scheduler error: {e}")
                    time.sleep(60)
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
    
    def _should_run_backup(self, job: BackupJob, current_time: datetime) -> bool:
        """Check if backup should run based on schedule"""
        # Simple cron-like parsing for basic schedules
        # Format: "minute hour * * *" (e.g., "0 2 * * *" for daily at 2 AM)
        try:
            cron_parts = job.schedule.split()
            if len(cron_parts) != 5:
                return False
            
            minute, hour, day, month, weekday = cron_parts
            
            # Check if current time matches schedule
            if (minute == "*" or int(minute) == current_time.minute) and \
               (hour == "*" or int(hour) == current_time.hour) and \
               (day == "*" or int(day) == current_time.day) and \
               (month == "*" or int(month) == current_time.month) and \
               (weekday == "*" or int(weekday) == current_time.weekday()):
                
                # Check if backup was already run recently (avoid duplicate runs)
                last_run = job.last_run
                if last_run is None or (current_time - last_run).total_seconds() > 3600:  # At least 1 hour ago
                    return True
            
            return False
        except Exception:
            return False
    
    def test_backup_integrity(self, backup_id: str) -> Dict[str, Any]:
        """Test backup integrity"""
        try:
            result = self.results.get(backup_id)
            if not result:
                return {"valid": False, "error": "Backup not found"}
            
            # Download backup if stored remotely
            if result.backup_path.startswith("s3://"):
                local_backup_path = self._download_from_s3(result.backup_path)
            else:
                local_backup_path = result.backup_path
            
            if not os.path.exists(local_backup_path):
                return {"valid": False, "error": "Backup file not found"}
            
            # Verify checksum
            checksum_valid = self._verify_checksum(local_backup_path, result.checksum)
            
            # Test archive integrity
            try:
                subprocess.run(["tar", "-tf", local_backup_path], check=True, capture_output=True)
                archive_valid = True
            except subprocess.CalledProcessError:
                archive_valid = False
            
            # Clean up
            if result.backup_path.startswith("s3://"):
                os.remove(local_backup_path)
            
            return {
                "valid": checksum_valid and archive_valid,
                "checksum_valid": checksum_valid,
                "archive_valid": archive_valid,
                "backup_id": backup_id
            }
            
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def get_backup_statistics(self) -> Dict[str, Any]:
        """Get backup system statistics"""
        total_backups = len(self.results)
        successful_backups = len([b for b in self.results.values() if b.status == BackupStatus.COMPLETED])
        failed_backups = len([b for b in self.results.values() if b.status == BackupStatus.FAILED])
        
        total_size = sum(b.total_size_bytes for b in self.results.values())
        compressed_size = sum(b.compressed_size_bytes for b in self.results.values() if b.compressed_size_bytes > 0)
        
        return {
            "total_backups": total_backups,
            "successful_backups": successful_backups,
            "failed_backups": failed_backups,
            "success_rate": (successful_backups / total_backups * 100) if total_backups > 0 else 0,
            "total_size_bytes": total_size,
            "compressed_size_bytes": compressed_size,
            "compression_ratio": (compressed_size / total_size) if total_size > 0 else 0,
            "active_jobs": len(self.jobs),
            "running_backups": len(self.running_backups),
            "storage_type": "s3" if self.s3_client else "local"
        }


# Global instance
backup_manager = BackupManager()
