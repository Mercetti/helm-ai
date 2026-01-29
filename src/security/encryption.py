"""
Helm AI Data Encryption
This module provides comprehensive data encryption for data at rest and in transit
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
import secrets
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class EncryptionType(Enum):
    """Encryption types"""
    SYMMETRIC = "symmetric"
    ASYMMETRIC = "asymmetric"
    AES_256_GCM = "aes_256_gcm"
    RSA_2048 = "rsa_2048"
    RSA_4096 = "rsa_4096"

class KeyType(Enum):
    """Key types for encryption"""
    AES256 = "aes256"
    AES128 = "aes128"
    RSA2048 = "rsa2048"
    RSA4096 = "rsa4096"

class DataClassification(Enum):
    """Data classification levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

@dataclass
class EncryptionKey:
    """Encryption key metadata"""
    key_id: str
    key_type: EncryptionType
    algorithm: str
    key_size: int
    created_at: datetime
    expires_at: Optional[datetime] = None
    classification: DataClassification = DataClassification.INTERNAL
    version: int = 1
    status: str = "active"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EncryptionResult:
    """Encryption operation result"""
    success: bool
    encrypted_data: Optional[bytes] = None
    key_id: str = None
    algorithm: str = None
    iv: Optional[bytes] = None
    tag: Optional[bytes] = None
    error: str = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class EncryptionManager:
    """Comprehensive encryption management system"""
    
    def __init__(self):
        self.keys: Dict[str, EncryptionKey] = {}
        self.symmetric_keys: Dict[str, bytes] = {}
        self.asymmetric_keys: Dict[str, Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]] = {}
        
        # Configuration
        self.use_aws_kms = os.getenv('AWS_KMS_KEY_ID') is not None
        self.key_rotation_days = int(os.getenv('KEY_ROTATION_DAYS', '90'))
        self.default_key_size = int(os.getenv('DEFAULT_KEY_SIZE', '256'))
        
        # Initialize AWS KMS if configured
        if self.use_aws_kms:
            self.kms_client = boto3.client('kms')
            self.kms_key_id = os.getenv('AWS_KMS_KEY_ID')
        
        # Initialize default keys
        self._initialize_default_keys()
        
        # Start key rotation scheduler
        self._schedule_key_rotation()
    
    def _initialize_default_keys(self):
        """Initialize default encryption keys"""
        # Create symmetric key for general use
        self.create_symmetric_key(
            key_id="default_symmetric",
            classification=DataClassification.INTERNAL
        )
        
        # Create symmetric key for confidential data
        self.create_symmetric_key(
            key_id="confidential_symmetric",
            classification=DataClassification.CONFIDENTIAL
        )
        
        # Create RSA key pair for asymmetric encryption
        self.create_asymmetric_key_pair(
            key_id="default_asymmetric",
            key_size=2048,
            classification=DataClassification.INTERNAL
        )
    
    def create_symmetric_key(self, 
                           key_id: str,
                           classification: DataClassification = DataClassification.INTERNAL,
                           key_size: int = None) -> EncryptionKey:
        """Create new symmetric encryption key"""
        key_size = key_size or self.default_key_size
        
        if key_size == 256:
            key = Fernet.generate_key()
            algorithm = "AES-256-CBC"
        else:
            # Generate random key for AES-GCM
            key = os.urandom(key_size // 8)
            algorithm = f"AES-{key_size}-GCM"
        
        # Store key securely
        if self.use_aws_kms:
            encrypted_key = self._encrypt_key_with_kms(key)
            self.symmetric_keys[key_id] = encrypted_key
        else:
            self.symmetric_keys[key_id] = key
        
        # Create key metadata
        encryption_key = EncryptionKey(
            key_id=key_id,
            key_type=EncryptionType.SYMMETRIC,
            algorithm=algorithm,
            key_size=key_size,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=self.key_rotation_days),
            classification=classification
        )
        
        self.keys[key_id] = encryption_key
        
        logger.info(f"Created symmetric key: {key_id}")
        return encryption_key
    
    def create_asymmetric_key_pair(self, 
                                 key_id: str,
                                 key_size: int = 2048,
                                 classification: DataClassification = DataClassification.INTERNAL) -> EncryptionKey:
        """Create new asymmetric key pair"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        
        # Store keys securely
        if self.use_aws_kms:
            encrypted_private = self._encrypt_key_with_kms(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
            )
            self.asymmetric_keys[key_id] = (encrypted_private, public_key)
        else:
            self.asymmetric_keys[key_id] = (private_key, public_key)
        
        # Create key metadata
        encryption_key = EncryptionKey(
            key_id=key_id,
            key_type=EncryptionType.ASYMMETRIC,
            algorithm=f"RSA-{key_size}",
            key_size=key_size,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=self.key_rotation_days * 2),  # Longer for asymmetric
            classification=classification
        )
        
        self.keys[key_id] = encryption_key
        
        logger.info(f"Created asymmetric key pair: {key_id}")
        return encryption_key
    
    def _encrypt_key_with_kms(self, key_data: bytes) -> bytes:
        """Encrypt key using AWS KMS"""
        try:
            response = self.kms_client.encrypt(
                KeyId=self.kms_key_id,
                Plaintext=key_data
            )
            return response['CiphertextBlob']
        except ClientError as e:
            logger.error(f"Failed to encrypt key with KMS: {e}")
            raise
    
    def _decrypt_key_with_kms(self, encrypted_key: bytes) -> bytes:
        """Decrypt key using AWS KMS"""
        try:
            response = self.kms_client.decrypt(
                CiphertextBlob=encrypted_key
            )
            return response['Plaintext']
        except ClientError as e:
            logger.error(f"Failed to decrypt key with KMS: {e}")
            raise
    
    def encrypt_data(self, 
                     data: Union[str, bytes],
                     key_id: str = None,
                     classification: DataClassification = None) -> EncryptionResult:
        """Encrypt data using specified key"""
        try:
            # Determine key to use
            if not key_id:
                if classification == DataClassification.CONFIDENTIAL:
                    key_id = "confidential_symmetric"
                else:
                    key_id = "default_symmetric"
            
            # Get key
            key_metadata = self.keys.get(key_id)
            if not key_metadata:
                return EncryptionResult(
                    success=False,
                    error=f"Key {key_id} not found"
                )
            
            # Prepare data
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # Encrypt based on key type
            if key_metadata.key_type == EncryptionType.SYMMETRIC:
                return self._encrypt_symmetric(data, key_id, key_metadata)
            elif key_metadata.key_type == EncryptionType.ASYMMETRIC:
                return self._encrypt_asymmetric(data, key_id, key_metadata)
            else:
                return EncryptionResult(
                    success=False,
                    error=f"Unsupported key type: {key_metadata.key_type}"
                )
                
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return EncryptionResult(
                success=False,
                error=str(e)
            )
    
    def _encrypt_symmetric(self, data: bytes, key_id: str, key_metadata: EncryptionKey) -> EncryptionResult:
        """Encrypt data using symmetric key"""
        # Get key
        encrypted_key = self.symmetric_keys.get(key_id)
        if not encrypted_key:
            return EncryptionResult(success=False, error="Key not found")
        
        if self.use_aws_kms:
            key = self._decrypt_key_with_kms(encrypted_key)
        else:
            key = encrypted_key
        
        # Encrypt based on algorithm
        if "GCM" in key_metadata.algorithm:
            return self._encrypt_aes_gcm(data, key, key_id, key_metadata)
        else:
            # Use Fernet for AES-CBC
            fernet = Fernet(key)
            encrypted_data = fernet.encrypt(data)
            
            return EncryptionResult(
                success=True,
                encrypted_data=encrypted_data,
                key_id=key_id,
                algorithm=key_metadata.algorithm
            )
    
    def _encrypt_aes_gcm(self, data: bytes, key: bytes, key_id: str, key_metadata: EncryptionKey) -> EncryptionResult:
        """Encrypt data using AES-GCM"""
        # Generate random IV
        iv = os.urandom(12)  # 96-bit IV for GCM
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv),
            backend=default_backend()
        )
        
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()
        
        return EncryptionResult(
            success=True,
            encrypted_data=ciphertext,
            key_id=key_id,
            algorithm=key_metadata.algorithm,
            iv=iv,
            tag=encryptor.tag
        )
    
    def _encrypt_asymmetric(self, data: bytes, key_id: str, key_metadata: EncryptionKey) -> EncryptionResult:
        """Encrypt data using asymmetric key"""
        # Get public key
        key_pair = self.asymmetric_keys.get(key_id)
        if not key_pair:
            return EncryptionResult(success=False, error="Key pair not found")
        
        if self.use_aws_kms:
            private_key_data = key_pair[0]
            private_key = serialization.load_pem_private_key(
                self._decrypt_key_with_kms(private_key_data),
                password=None,
                backend=default_backend()
            )
            public_key = private_key.public_key()
        else:
            private_key, public_key = key_pair
        
        # RSA encryption with OAEP padding
        ciphertext = public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return EncryptionResult(
            success=True,
            encrypted_data=ciphertext,
            key_id=key_id,
            algorithm=key_metadata.algorithm
        )
    
    def decrypt_data(self, encrypted_result: EncryptionResult) -> EncryptionResult:
        """Decrypt data using encryption result metadata"""
        try:
            if not encrypted_result.success:
                return encrypted_result
            
            key_id = encrypted_result.key_id
            key_metadata = self.keys.get(key_id)
            
            if not key_metadata:
                return EncryptionResult(
                    success=False,
                    error=f"Key {key_id} not found"
                )
            
            # Decrypt based on key type
            if key_metadata.key_type == EncryptionType.SYMMETRIC:
                return self._decrypt_symmetric(encrypted_result, key_id, key_metadata)
            elif key_metadata.key_type == EncryptionType.ASYMMETRIC:
                return self._decrypt_asymmetric(encrypted_result, key_id, key_metadata)
            else:
                return EncryptionResult(
                    success=False,
                    error=f"Unsupported key type: {key_metadata.key_type}"
                )
                
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return EncryptionResult(
                success=False,
                error=str(e)
            )
    
    def _decrypt_symmetric(self, encrypted_result: EncryptionResult, key_id: str, key_metadata: EncryptionKey) -> EncryptionResult:
        """Decrypt data using symmetric key"""
        # Get key
        encrypted_key = self.symmetric_keys.get(key_id)
        if not encrypted_key:
            return EncryptionResult(success=False, error="Key not found")
        
        if self.use_aws_kms:
            key = self._decrypt_key_with_kms(encrypted_key)
        else:
            key = encrypted_key
        
        # Decrypt based on algorithm
        if "GCM" in key_metadata.algorithm:
            return self._decrypt_aes_gcm(encrypted_result, key)
        else:
            # Use Fernet for AES-CBC
            fernet = Fernet(key)
            decrypted_data = fernet.decrypt(encrypted_result.encrypted_data)
            
            return EncryptionResult(
                success=True,
                encrypted_data=decrypted_data,
                key_id=key_id,
                algorithm=key_metadata.algorithm
            )
    
    def _decrypt_aes_gcm(self, encrypted_result: EncryptionResult, key: bytes) -> EncryptionResult:
        """Decrypt data using AES-GCM"""
        # Create cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(encrypted_result.iv, encrypted_result.tag),
            backend=default_backend()
        )
        
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(encrypted_result.encrypted_data) + decryptor.finalize()
        
        return EncryptionResult(
            success=True,
            encrypted_data=plaintext,
            key_id=encrypted_result.key_id,
            algorithm=encrypted_result.algorithm
        )
    
    def _decrypt_asymmetric(self, encrypted_result: EncryptionResult, key_id: str, key_metadata: EncryptionKey) -> EncryptionResult:
        """Decrypt data using asymmetric key"""
        # Get private key
        key_pair = self.asymmetric_keys.get(key_id)
        if not key_pair:
            return EncryptionResult(success=False, error="Key pair not found")
        
        if self.use_aws_kms:
            private_key_data = key_pair[0]
            private_key = serialization.load_pem_private_key(
                self._decrypt_key_with_kms(private_key_data),
                password=None,
                backend=default_backend()
            )
        else:
            private_key, _ = key_pair
        
        # RSA decryption with OAEP padding
        plaintext = private_key.decrypt(
            encrypted_result.encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return EncryptionResult(
            success=True,
            encrypted_data=plaintext,
            key_id=key_id,
            algorithm=key_metadata.algorithm
        )
    
    def rotate_key(self, key_id: str) -> bool:
        """Rotate encryption key"""
        try:
            key_metadata = self.keys.get(key_id)
            if not key_metadata:
                return False
            
            # Create new key
            new_key_id = f"{key_id}_v{key_metadata.version + 1}"
            
            if key_metadata.key_type == EncryptionType.SYMMETRIC:
                new_key = self.create_symmetric_key(
                    key_id=new_key_id,
                    classification=key_metadata.classification,
                    key_size=key_metadata.key_size
                )
            elif key_metadata.key_type == EncryptionType.ASYMMETRIC:
                new_key = self.create_asymmetric_key_pair(
                    key_id=new_key_id,
                    key_size=key_metadata.key_size,
                    classification=key_metadata.classification
                )
            
            # Mark old key as deprecated
            key_metadata.status = "deprecated"
            
            logger.info(f"Rotated key {key_id} to {new_key_id}")
            return True
            
        except Exception as e:
            logger.error(f"Key rotation failed: {e}")
            return False
    
    def _schedule_key_rotation(self):
        """Schedule automatic key rotation"""
        import threading
        
        def rotation_scheduler():
            while True:
                try:
                    current_time = datetime.now()
                    
                    # Check for keys that need rotation
                    for key_id, key_metadata in self.keys.items():
                        if (key_metadata.expires_at and 
                            current_time >= key_metadata.expires_at and 
                            key_metadata.status == "active"):
                            self.rotate_key(key_id)
                    
                    # Sleep for 24 hours
                    threading.Event().wait(24 * 60 * 60)
                    
                except Exception as e:
                    logger.error(f"Key rotation scheduler error: {e}")
        
        rotation_thread = threading.Thread(target=rotation_scheduler, daemon=True)
        rotation_thread.start()
    
    def get_key_info(self, key_id: str) -> Optional[Dict[str, Any]]:
        """Get key information"""
        key_metadata = self.keys.get(key_id)
        if not key_metadata:
            return None
        
        return {
            "key_id": key_metadata.key_id,
            "key_type": key_metadata.key_type.value,
            "algorithm": key_metadata.algorithm,
            "key_size": key_metadata.key_size,
            "classification": key_metadata.classification.value,
            "created_at": key_metadata.created_at.isoformat(),
            "expires_at": key_metadata.expires_at.isoformat() if key_metadata.expires_at else None,
            "version": key_metadata.version,
            "status": key_metadata.status
        }
    
    def list_keys(self, classification: DataClassification = None) -> List[Dict[str, Any]]:
        """List all keys"""
        keys = []
        
        for key_id, key_metadata in self.keys.items():
            if classification and key_metadata.classification != classification:
                continue
            
            keys.append(self.get_key_info(key_id))
        
        return keys
    
    def delete_key(self, key_id: str) -> bool:
        """Delete encryption key"""
        try:
            # Remove from storage
            if key_id in self.keys:
                del self.keys[key_id]
            
            if key_id in self.symmetric_keys:
                del self.symmetric_keys[key_id]
            
            if key_id in self.asymmetric_keys:
                del self.asymmetric_keys[key_id]
            
            logger.info(f"Deleted key: {key_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete key {key_id}: {e}")
            return False
    
    def encrypt_field(self, field_value: str, field_name: str, classification: DataClassification = None) -> str:
        """Encrypt a single field value"""
        if not field_value:
            return field_value
        
        result = self.encrypt_data(field_value, classification=classification)
        
        if result.success:
            # Return base64 encoded encrypted data with metadata
            encrypted_data = base64.b64encode(result.encrypted_data).decode('utf-8')
            metadata = {
                "key_id": result.key_id,
                "algorithm": result.algorithm,
                "iv": base64.b64encode(result.iv).decode('utf-8') if result.iv else None,
                "tag": base64.b64encode(result.tag).decode('utf-8') if result.tag else None
            }
            
            return f"ENC:{encrypted_data}:{base64.b64encode(json.dumps(metadata).encode()).decode('utf-8')}"
        
        return field_value  # Return original if encryption fails
    
    def decrypt_field(self, encrypted_field: str) -> str:
        """Decrypt a single field value"""
        if not encrypted_field or not encrypted_field.startswith("ENC:"):
            return encrypted_field
        
        try:
            # Parse encrypted field
            parts = encrypted_field[4:].split(":")  # Remove "ENC:" prefix
            encrypted_data = base64.b64decode(parts[0])
            metadata = json.loads(base64.b64decode(parts[1]))
            
            # Create encryption result
            result = EncryptionResult(
                success=True,
                encrypted_data=encrypted_data,
                key_id=metadata["key_id"],
                algorithm=metadata["algorithm"],
                iv=base64.b64decode(metadata["iv"]) if metadata["iv"] else None,
                tag=base64.b64decode(metadata["tag"]) if metadata["tag"] else None
            )
            
            # Decrypt
            decrypted_result = self.decrypt_data(result)
            
            if decrypted_result.success:
                return decrypted_result.encrypted_data.decode('utf-8')
            
            return encrypted_field
            
        except Exception as e:
            logger.error(f"Field decryption failed: {e}")
            return encrypted_field
    
    def generate_data_hash(self, data: Union[str, bytes], algorithm: str = "sha256") -> str:
        """Generate cryptographic hash of data"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        if algorithm.lower() == "sha256":
            return hashlib.sha256(data).hexdigest()
        elif algorithm.lower() == "sha512":
            return hashlib.sha512(data).hexdigest()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    
    def verify_data_integrity(self, data: Union[str, bytes], expected_hash: str, algorithm: str = "sha256") -> bool:
        """Verify data integrity using hash"""
        actual_hash = self.generate_data_hash(data, algorithm)
        return hmac.compare_digest(actual_hash, expected_hash)
    
    def get_encryption_status(self) -> Dict[str, Any]:
        """Get encryption system status"""
        total_keys = len(self.keys)
        active_keys = len([k for k in self.keys.values() if k.status == "active"])
        expired_keys = len([k for k in self.keys.values() 
                          if k.expires_at and datetime.now() > k.expires_at])
        
        return {
            "total_keys": total_keys,
            "active_keys": active_keys,
            "expired_keys": expired_keys,
            "use_aws_kms": self.use_aws_kms,
            "key_rotation_days": self.key_rotation_days,
            "keys_by_type": {
                "symmetric": len([k for k in self.keys.values() if k.key_type == EncryptionType.SYMMETRIC]),
                "asymmetric": len([k for k in self.keys.values() if k.key_type == EncryptionType.ASYMMETRIC])
            },
            "keys_by_classification": {
                classification.value: len([k for k in self.keys.values() if k.classification == classification])
                for classification in DataClassification
            }
        }


# Global instance
encryption_manager = EncryptionManager()
