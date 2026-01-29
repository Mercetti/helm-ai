"""
Helm AI Data Integrity Management
This module provides data integrity verification, validation, and monitoring
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import hashlib
import hmac
import threading
import time
import sqlite3
from pathlib import Path

from .encryption import encryption_manager

logger = logging.getLogger(__name__)

class IntegrityStatus(Enum):
    """Data integrity status"""
    VALID = "valid"
    CORRUPTED = "corrupted"
    MODIFIED = "modified"
    UNKNOWN = "unknown"
    CHECKING = "checking"

class ValidationType(Enum):
    """Validation types"""
    CHECKSUM = "checksum"
    HASH_CHAIN = "hash_chain"
    DIGITAL_SIGNATURE = "digital_signature"
    MERKLE_TREE = "merkle_tree"

@dataclass
class IntegrityRecord:
    """Data integrity record"""
    record_id: str
    file_path: str
    checksum: str
    algorithm: str
    file_size: int
    modified_time: datetime
    created_at: datetime
    last_verified: Optional[datetime] = None
    status: IntegrityStatus = IntegrityStatus.UNKNOWN
    validation_type: ValidationType = ValidationType.CHECKSUM
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class IntegrityViolation:
    """Data integrity violation"""
    violation_id: str
    record_id: str
    file_path: str
    violation_type: str
    expected_checksum: str
    actual_checksum: str
    detected_at: datetime
    severity: str  # low, medium, high, critical
    resolved: bool = False
    resolution_action: str = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class DataIntegrityManager:
    """Data integrity management system"""
    
    def __init__(self):
        self.records: Dict[str, IntegrityRecord] = {}
        self.violations: Dict[str, IntegrityViolation] = {}
        
        # Configuration
        self.db_path = os.getenv('INTEGRITY_DB_PATH', '/var/lib/helm-ai/integrity.db')
        self.monitor_directories = os.getenv('INTEGRITY_MONITOR_DIRS', '/opt/helm-ai/data,/opt/helm-ai/config').split(',')
        self.check_interval = int(os.getenv('INTEGRITY_CHECK_INTERVAL', '3600'))  # 1 hour
        self.default_algorithm = 'sha256'
        
        # Initialize database
        self._initialize_database()
        
        # Load existing records
        self._load_integrity_records()
        
        # Start monitoring
        self._start_monitoring()
    
    def _initialize_database(self):
        """Initialize integrity database"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create records table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS integrity_records (
                record_id TEXT PRIMARY KEY,
                file_path TEXT UNIQUE,
                checksum TEXT,
                algorithm TEXT,
                file_size INTEGER,
                modified_time TEXT,
                created_at TEXT,
                last_verified TEXT,
                status TEXT,
                validation_type TEXT,
                metadata TEXT
            )
        ''')
        
        # Create violations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS integrity_violations (
                violation_id TEXT PRIMARY KEY,
                record_id TEXT,
                file_path TEXT,
                violation_type TEXT,
                expected_checksum TEXT,
                actual_checksum TEXT,
                detected_at TEXT,
                severity TEXT,
                resolved BOOLEAN,
                resolution_action TEXT,
                metadata TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_integrity_records(self):
        """Load integrity records from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM integrity_records')
        rows = cursor.fetchall()
        
        for row in rows:
            record = IntegrityRecord(
                record_id=row[0],
                file_path=row[1],
                checksum=row[2],
                algorithm=row[3],
                file_size=row[4],
                modified_time=datetime.fromisoformat(row[5]),
                created_at=datetime.fromisoformat(row[6]),
                last_verified=datetime.fromisoformat(row[7]) if row[7] else None,
                status=IntegrityStatus(row[8]),
                validation_type=ValidationType(row[9]),
                metadata=json.loads(row[10]) if row[10] else {}
            )
            self.records[record.record_id] = record
        
        conn.close()
        logger.info(f"Loaded {len(self.records)} integrity records")
    
    def create_integrity_record(self, 
                                file_path: str,
                                algorithm: str = None,
                                validation_type: ValidationType = ValidationType.CHECKSUM) -> IntegrityRecord:
        """Create integrity record for file"""
        if not os.path.exists(file_path):
            raise ValueError(f"File does not exist: {file_path}")
        
        algorithm = algorithm or self.default_algorithm
        record_id = f"record_{hashlib.sha256(file_path.encode()).hexdigest()[:16]}"
        
        # Calculate checksum
        checksum = self._calculate_file_checksum(file_path, algorithm)
        
        # Get file metadata
        stat = os.stat(file_path)
        file_size = stat.st_size
        modified_time = datetime.fromtimestamp(stat.st_mtime)
        
        record = IntegrityRecord(
            record_id=record_id,
            file_path=file_path,
            checksum=checksum,
            algorithm=algorithm,
            file_size=file_size,
            modified_time=modified_time,
            created_at=datetime.now(),
            validation_type=validation_type
        )
        
        # Save to database
        self._save_record(record)
        self.records[record_id] = record
        
        logger.info(f"Created integrity record for: {file_path}")
        return record
    
    def _calculate_file_checksum(self, file_path: str, algorithm: str) -> str:
        """Calculate file checksum"""
        hash_obj = hashlib.new(algorithm)
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
    
    def _save_record(self, record: IntegrityRecord):
        """Save integrity record to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO integrity_records 
            (record_id, file_path, checksum, algorithm, file_size, modified_time, 
             created_at, last_verified, status, validation_type, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            record.record_id,
            record.file_path,
            record.checksum,
            record.algorithm,
            record.file_size,
            record.modified_time.isoformat(),
            record.created_at.isoformat(),
            record.last_verified.isoformat() if record.last_verified else None,
            record.status.value,
            record.validation_type.value,
            json.dumps(record.metadata)
        ))
        
        conn.commit()
        conn.close()
    
    def verify_file_integrity(self, file_path: str) -> Tuple[bool, Optional[IntegrityRecord]]:
        """Verify file integrity"""
        # Find record for file
        record = None
        for r in self.records.values():
            if r.file_path == file_path:
                record = r
                break
        
        if not record:
            # Create new record if file exists
            if os.path.exists(file_path):
                record = self.create_integrity_record(file_path)
                return True, record
            else:
                return False, None
        
        # Check if file still exists
        if not os.path.exists(file_path):
            self._create_violation(record, "file_missing", record.checksum, "")
            return False, record
        
        # Calculate current checksum
        current_checksum = self._calculate_file_checksum(file_path, record.algorithm)
        
        # Compare with stored checksum
        if current_checksum == record.checksum:
            record.status = IntegrityStatus.VALID
            record.last_verified = datetime.now()
            self._save_record(record)
            return True, record
        else:
            record.status = IntegrityStatus.MODIFIED
            self._save_record(record)
            
            # Create violation
            self._create_violation(record, "checksum_mismatch", record.checksum, current_checksum)
            return False, record
    
    def _create_violation(self, record: IntegrityRecord, violation_type: str, expected: str, actual: str):
        """Create integrity violation"""
        violation_id = f"violation_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hashlib.sha256(record.file_path.encode()).hexdigest()[:8]}"
        
        # Determine severity based on file type and violation type
        severity = self._determine_violation_severity(record.file_path, violation_type)
        
        violation = IntegrityViolation(
            violation_id=violation_id,
            record_id=record.record_id,
            file_path=record.file_path,
            violation_type=violation_type,
            expected_checksum=expected,
            actual_checksum=actual,
            detected_at=datetime.now(),
            severity=severity
        )
        
        # Save to database
        self._save_violation(violation)
        self.violations[violation_id] = violation
        
        logger.warning(f"Integrity violation detected: {record.file_path} - {violation_type}")
    
    def _determine_violation_severity(self, file_path: str, violation_type: str) -> str:
        """Determine violation severity"""
        # Critical files
        critical_patterns = ['/etc/', '/var/lib/', 'config', 'key', 'secret', 'password']
        
        for pattern in critical_patterns:
            if pattern in file_path.lower():
                return "critical"
        
        # High severity for certain violation types
        if violation_type in ["file_missing", "checksum_mismatch"]:
            return "high"
        
        # Default to medium
        return "medium"
    
    def _save_violation(self, violation: IntegrityViolation):
        """Save violation to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO integrity_violations 
            (violation_id, record_id, file_path, violation_type, expected_checksum, 
             actual_checksum, detected_at, severity, resolved, resolution_action, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            violation.violation_id,
            violation.record_id,
            violation.file_path,
            violation.violation_type,
            violation.expected_checksum,
            violation.actual_checksum,
            violation.detected_at.isoformat(),
            violation.severity,
            violation.resolved,
            violation.resolution_action,
            json.dumps(violation.metadata)
        ))
        
        conn.commit()
        conn.close()
    
    def scan_directory(self, directory: str, recursive: bool = True) -> Dict[str, Any]:
        """Scan directory for integrity issues"""
        results = {
            "scanned_files": 0,
            "valid_files": 0,
            "violations": 0,
            "new_records": 0,
            "violations_list": []
        }
        
        path = Path(directory)
        
        if recursive:
            files = list(path.rglob('*'))
        else:
            files = list(path.glob('*'))
        
        # Filter only files
        files = [f for f in files if f.is_file()]
        
        for file_path in files:
            results["scanned_files"] += 1
            
            try:
                is_valid, record = self.verify_file_integrity(str(file_path))
                
                if is_valid:
                    results["valid_files"] += 1
                else:
                    if record and record.status == IntegrityStatus.MODIFIED:
                        results["violations"] += 1
                        # Get latest violation
                        recent_violations = [v for v in self.violations.values() 
                                           if v.file_path == str(file_path) and not v.resolved]
                        if recent_violations:
                            results["violations_list"].append({
                                "file_path": str(file_path),
                                "violation_type": recent_violations[-1].violation_type,
                                "severity": recent_violations[-1].severity,
                                "detected_at": recent_violations[-1].detected_at.isoformat()
                            })
                    elif record and record.created_at == record.last_verified:
                        results["new_records"] += 1
                        
            except Exception as e:
                logger.error(f"Failed to verify file {file_path}: {e}")
        
        return results
    
    def verify_all_records(self) -> Dict[str, Any]:
        """Verify all integrity records"""
        results = {
            "total_records": len(self.records),
            "valid": 0,
            "invalid": 0,
            "missing": 0,
            "violations": []
        }
        
        for record in self.records.values():
            try:
                is_valid, _ = self.verify_file_integrity(record.file_path)
                
                if is_valid:
                    results["valid"] += 1
                else:
                    results["invalid"] += 1
                    
                    # Get latest violation
                    recent_violations = [v for v in self.violations.values() 
                                       if v.record_id == record.record_id and not v.resolved]
                    if recent_violations:
                        results["violations"].append({
                            "file_path": record.file_path,
                            "violation_type": recent_violations[-1].violation_type,
                            "severity": recent_violations[-1].severity
                        })
                        
            except Exception as e:
                logger.error(f"Failed to verify record {record.record_id}: {e}")
                results["missing"] += 1
        
        return results
    
    def resolve_violation(self, violation_id: str, resolution_action: str) -> bool:
        """Resolve integrity violation"""
        violation = self.violations.get(violation_id)
        if not violation:
            return False
        
        violation.resolved = True
        violation.resolution_action = resolution_action
        
        # Update database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE integrity_violations 
            SET resolved = ?, resolution_action = ? 
            WHERE violation_id = ?
        ''', (True, resolution_action, violation_id))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Resolved violation {violation_id}: {resolution_action}")
        return True
    
    def create_merkle_tree(self, directory: str) -> Dict[str, Any]:
        """Create Merkle tree for directory integrity"""
        def hash_file(file_path: str) -> str:
            return self._calculate_file_checksum(file_path, 'sha256')
        
        def hash_directory(dir_path: str) -> str:
            path = Path(dir_path)
            hashes = []
            
            for item in sorted(path.iterdir()):
                if item.is_file():
                    hashes.append(hash_file(str(item)))
                elif item.is_dir():
                    hashes.append(hash_directory(str(item)))
            
            if not hashes:
                return hashlib.sha256(b'').hexdigest()
            
            combined = ''.join(hashes).encode()
            return hashlib.sha256(combined).hexdigest()
        
        try:
            root_hash = hash_directory(directory)
            
            return {
                "directory": directory,
                "root_hash": root_hash,
                "algorithm": "sha256",
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to create Merkle tree for {directory}: {e}")
            return {"error": str(e)}
    
    def verify_merkle_tree(self, directory: str, expected_root_hash: str) -> bool:
        """Verify directory integrity using Merkle tree"""
        tree_result = self.create_merkle_tree(directory)
        
        if "error" in tree_result:
            return False
        
        actual_root_hash = tree_result["root_hash"]
        return actual_root_hash == expected_root_hash
    
    def generate_integrity_report(self, days: int = 7) -> Dict[str, Any]:
        """Generate integrity report"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Get recent violations
        recent_violations = [v for v in self.violations.values() 
                           if v.detected_at >= cutoff_date]
        
        # Statistics
        total_violations = len(recent_violations)
        resolved_violations = len([v for v in recent_violations if v.resolved])
        unresolved_violations = total_violations - resolved_violations
        
        # Violations by severity
        severity_counts = {}
        for violation in recent_violations:
            severity = violation.severity
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Violations by type
        type_counts = {}
        for violation in recent_violations:
            vtype = violation.violation_type
            type_counts[vtype] = type_counts.get(vtype, 0) + 1
        
        return {
            "report_period": f"Last {days} days",
            "generated_at": datetime.now().isoformat(),
            "total_records": len(self.records),
            "total_violations": total_violations,
            "resolved_violations": resolved_violations,
            "unresolved_violations": unresolved_violations,
            "resolution_rate": (resolved_violations / total_violations * 100) if total_violations > 0 else 0,
            "violations_by_severity": severity_counts,
            "violations_by_type": type_counts,
            "monitor_directories": self.monitor_directories
        }
    
    def _start_monitoring(self):
        """Start background monitoring"""
        def monitor_directories():
            for directory in self.monitor_directories:
                if os.path.exists(directory):
                    results = self.scan_directory(directory, recursive=True)
                    logger.info(f"Integrity scan for {directory}: {results}")
        
        def run_scheduler():
            while True:
                try:
                    monitor_directories()
                    threading.Event().wait(self.check_interval)
                except Exception as e:
                    logger.error(f"Monitoring error: {e}")
        
        # Start scheduler thread
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        logger.info("Started integrity monitoring")
    
    def get_integrity_status(self) -> Dict[str, Any]:
        """Get overall integrity status"""
        total_records = len(self.records)
        valid_records = len([r for r in self.records.values() if r.status == IntegrityStatus.VALID])
        corrupted_records = len([r for r in self.records.values() if r.status == IntegrityStatus.CORRUPTED])
        modified_records = len([r for r in self.records.values() if r.status == IntegrityStatus.MODIFIED])
        
        total_violations = len(self.violations)
        unresolved_violations = len([v for v in self.violations.values() if not v.resolved])
        
        return {
            "total_records": total_records,
            "valid_records": valid_records,
            "corrupted_records": corrupted_records,
            "modified_records": modified_records,
            "integrity_rate": (valid_records / total_records * 100) if total_records > 0 else 0,
            "total_violations": total_violations,
            "unresolved_violations": unresolved_violations,
            "monitor_directories": self.monitor_directories,
            "check_interval": self.check_interval
        }


# Global instance
data_integrity = DataIntegrityManager()
