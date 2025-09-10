"""
Enhanced Secrets Management for GenAI Metrics Dashboard
Implements secure secrets handling with encryption and validation
"""
import os
import base64
import secrets
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

logger = logging.getLogger(__name__)

class SecretsManager:
    """Enhanced secrets management with encryption"""
    
    def __init__(self):
        self.master_key = self._get_or_create_master_key()
        self.cipher_suite = Fernet(self.master_key)
        self.secrets_cache = {}
    
    def _get_or_create_master_key(self) -> bytes:
        """Get or create master encryption key"""
        # Try to get from environment variable
        master_key_env = os.getenv("MASTER_ENCRYPTION_KEY")
        if master_key_env:
            try:
                return base64.urlsafe_b64decode(master_key_env.encode())
            except Exception as e:
                logger.warning(f"Invalid master key in environment: {e}")
        
        # Try to get from file
        key_file = os.getenv("MASTER_KEY_FILE", ".master_key")
        if os.path.exists(key_file):
            try:
                with open(key_file, 'rb') as f:
                    return f.read()
            except Exception as e:
                logger.warning(f"Error reading master key file: {e}")
        
        # Generate new master key
        logger.warning("No master key found, generating new one")
        new_key = Fernet.generate_key()
        
        # Save to file
        try:
            with open(key_file, 'wb') as f:
                f.write(new_key)
            os.chmod(key_file, 0o600)  # Restrict permissions
            logger.info(f"New master key saved to {key_file}")
        except Exception as e:
            logger.error(f"Failed to save master key: {e}")
        
        return new_key
    
    def encrypt_secret(self, secret: str) -> str:
        """Encrypt a secret value"""
        try:
            encrypted_bytes = self.cipher_suite.encrypt(secret.encode())
            return base64.urlsafe_b64encode(encrypted_bytes).decode()
        except Exception as e:
            logger.error(f"Error encrypting secret: {e}")
            raise
    
    def decrypt_secret(self, encrypted_secret: str) -> str:
        """Decrypt a secret value"""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_secret.encode())
            decrypted_bytes = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Error decrypting secret: {e}")
            raise
    
    def get_secret(self, key: str, default: Optional[str] = None, encrypted: bool = False) -> Optional[str]:
        """Get a secret value with caching"""
        # Check cache first
        if key in self.secrets_cache:
            return self.secrets_cache[key]
        
        # Get from environment
        value = os.getenv(key, default)
        
        if value and encrypted:
            try:
                value = self.decrypt_secret(value)
            except Exception as e:
                logger.error(f"Failed to decrypt secret {key}: {e}")
                return default
        
        # Cache the value
        if value:
            self.secrets_cache[key] = value
        
        return value
    
    def set_secret(self, key: str, value: str, encrypt: bool = True) -> str:
        """Set a secret value"""
        if encrypt:
            encrypted_value = self.encrypt_secret(value)
            # Store encrypted value in environment or file
            os.environ[key] = encrypted_value
            return encrypted_value
        else:
            os.environ[key] = value
            return value
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate a cryptographically secure token"""
        return secrets.token_urlsafe(length)
    
    def generate_api_key(self, prefix: str = "api") -> str:
        """Generate a secure API key"""
        random_part = secrets.token_urlsafe(32)
        return f"{prefix}_{random_part}"
    
    def hash_password(self, password: str, salt: Optional[bytes] = None) -> Dict[str, str]:
        """Hash a password with salt"""
        if salt is None:
            salt = secrets.token_bytes(32)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        salt_b64 = base64.urlsafe_b64encode(salt).decode()
        
        return {
            "hash": key.decode(),
            "salt": salt_b64
        }
    
    def verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """Verify a password against its hash"""
        try:
            salt_bytes = base64.urlsafe_b64decode(salt.encode())
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt_bytes,
                iterations=100000,
            )
            
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            return key.decode() == password_hash
            
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False
    
    def validate_secret_strength(self, secret: str, min_length: int = 8) -> Dict[str, Any]:
        """Validate secret strength"""
        result = {
            "valid": True,
            "score": 0,
            "issues": []
        }
        
        if len(secret) < min_length:
            result["valid"] = False
            result["issues"].append(f"Password must be at least {min_length} characters")
        
        if not any(c.isupper() for c in secret):
            result["score"] += 1
            result["issues"].append("Should contain uppercase letters")
        
        if not any(c.islower() for c in secret):
            result["score"] += 1
            result["issues"].append("Should contain lowercase letters")
        
        if not any(c.isdigit() for c in secret):
            result["score"] += 1
            result["issues"].append("Should contain numbers")
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in secret):
            result["score"] += 1
            result["issues"].append("Should contain special characters")
        
        # Common weak passwords
        weak_passwords = [
            "password", "123456", "admin", "qwerty", "letmein",
            "welcome", "monkey", "dragon", "master", "hello"
        ]
        
        if secret.lower() in weak_passwords:
            result["valid"] = False
            result["issues"].append("Password is too common")
        
        return result

# Global secrets manager instance
secrets_manager = SecretsManager()

# Convenience functions
def get_secret(key: str, default: Optional[str] = None, encrypted: bool = False) -> Optional[str]:
    """Get a secret value"""
    return secrets_manager.get_secret(key, default, encrypted)

def set_secret(key: str, value: str, encrypt: bool = True) -> str:
    """Set a secret value"""
    return secrets_manager.set_secret(key, value, encrypt)

def generate_api_key(prefix: str = "api") -> str:
    """Generate a secure API key"""
    return secrets_manager.generate_api_key(prefix)

def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure token"""
    return secrets_manager.generate_secure_token(length)

def hash_password(password: str, salt: Optional[bytes] = None) -> Dict[str, str]:
    """Hash a password with salt"""
    return secrets_manager.hash_password(password, salt)

def verify_password(password: str, password_hash: str, salt: str) -> bool:
    """Verify a password against its hash"""
    return secrets_manager.verify_password(password, password_hash, salt)
