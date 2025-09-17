"""
Configuration management for the Anclora PDF2EPUB application
Enhanced with security validation and secret management
"""
import os
import logging
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecurityConfig:
    """Security-focused configuration validation."""
    
    # Minimum lengths for different types of secrets
    MIN_SECRET_LENGTHS = {
        'SECRET_KEY': 32,
        'JWT_SECRET': 32,
        'REDIS_PASSWORD': 16,
        'SUPABASE_JWT_SECRET': 32,
    }
    
    # Patterns for weak/default values
    WEAK_PATTERNS = [
        r'^(test|demo|example|default|change.*me|your_.*_here)$',
        r'^(123|password|secret|key|admin)$',
        r'^(.)\1+$',  # Repeated characters like 'aaaa'
    ]
    
    @classmethod
    def validate_secret_strength(cls, key: str, value: str) -> Tuple[bool, List[str]]:
        """Validate strength of a secret value."""
        issues = []
        
        if not value:
            issues.append(f"{key} is empty")
            return False, issues
        
        # Check minimum length
        min_length = cls.MIN_SECRET_LENGTHS.get(key, 16)
        if len(value) < min_length:
            issues.append(f"{key} is too short (minimum {min_length} characters)")
        
        # Check for weak patterns
        for pattern in cls.WEAK_PATTERNS:
            if re.match(pattern, value.lower()):
                issues.append(f"{key} appears to be a default or weak value")
                break
        
        # Check for sufficient entropy (basic check for hex secrets)
        if len(set(value)) < min(len(value) * 0.3, 16):  # At least 30% unique chars or 16 unique chars
            issues.append(f"{key} has low entropy (too many repeated characters)")
        
        return len(issues) == 0, issues
    
    @classmethod
    def validate_jwt_token(cls, token: str) -> Tuple[bool, List[str]]:
        """Validate JWT token format."""
        issues = []
        
        if not token:
            issues.append("JWT token is empty")
            return False, issues
        
        # JWT should have 3 parts separated by dots
        parts = token.split('.')
        if len(parts) != 3:
            issues.append("JWT token format is invalid (should have 3 parts)")
        
        # Each part should be base64-encoded (basic check)
        for i, part in enumerate(parts[:2]):  # Header and payload
            if not part or not re.match(r'^[A-Za-z0-9_-]+$', part):
                issues.append(f"JWT token part {i+1} has invalid base64 format")
        
        return len(issues) == 0, issues


class ConfigManager:
    """
    Enhanced configuration management with security validation
    
    This class handles:
    1. Loading environment variables from .env files
    2. Validating security of configuration values
    3. Providing secure access to configuration
    4. Startup health checks
    """
    
    _initialized = False
    _validation_errors: List[str] = []
    _validation_warnings: List[str] = []
    
    # Required configuration variables
    REQUIRED_VARS = {
        'basic': [
            'FLASK_ENV',
            'FLASK_APP',
        ],
        'security': [
            'SECRET_KEY',
            'JWT_SECRET',
        ],
        'supabase': [
            'SUPABASE_URL',
            'SUPABASE_SECRET_KEY',
            'SUPABASE_JWT_SECRET',
        ],
        'redis': [
            'REDIS_PASSWORD',
        ],
    }
    
    @classmethod
    def initialize(cls, strict_mode: bool = False):
        """
        Initialize the configuration manager with enhanced validation.
        
        Args:
            strict_mode: If True, exit on validation errors
        """
        if cls._initialized:
            return
        
        cls._validation_errors = []
        cls._validation_warnings = []
        
        # Load environment variables
        cls._load_environment_files()
        
        # Validate configuration
        cls._validate_all_config()
        
        # Handle validation results
        cls._handle_validation_results(strict_mode)
        
        cls._initialized = True
    
    @classmethod
    def _load_environment_files(cls):
        """Load environment variables from multiple possible locations."""
        env_paths = [
            Path(__file__).parent.parent / '.env',  # backend/.env
            Path(__file__).parent.parent.parent / '.env',  # project root/.env
        ]
        
        loaded_any = False
        for env_path in env_paths:
            if env_path.exists():
                logger.info(f"Loading environment variables from: {env_path}")
                load_dotenv(dotenv_path=env_path, override=False)  # Respect runtime env vars
                loaded_any = True
            else:
                logger.debug(f"Environment file not found: {env_path}")
        
        if not loaded_any:
            cls._validation_warnings.append(
                "No .env file found. Using system environment variables only."
            )
    
    @classmethod
    def _validate_all_config(cls):
        """Perform comprehensive configuration validation."""
        # Check required variables
        cls._validate_required_vars()
        
        # Validate security of secrets
        cls._validate_secret_security()
        
        # Validate specific configurations
        cls._validate_supabase_config()
        cls._validate_flask_config()
    
    @classmethod
    def _validate_required_vars(cls):
        """Check that all required variables are present."""
        for category, vars_list in cls.REQUIRED_VARS.items():
            missing_vars = [var for var in vars_list if not os.getenv(var)]
            
            if missing_vars:
                cls._validation_errors.append(
                    f"Missing required {category} variables: {', '.join(missing_vars)}"
                )
    
    @classmethod
    def _validate_secret_security(cls):
        """Validate the security of secret values."""
        secret_vars = [
            'SECRET_KEY', 'JWT_SECRET', 'REDIS_PASSWORD', 'SUPABASE_JWT_SECRET'
        ]
        
        for var in secret_vars:
            value = os.getenv(var)
            if value:
                is_secure, issues = SecurityConfig.validate_secret_strength(var, value)
                if not is_secure:
                    cls._validation_errors.extend([f"{var}: {issue}" for issue in issues])
    
    @classmethod
    def _validate_supabase_config(cls):
        """Validate Supabase-specific configuration."""
        url = os.getenv('SUPABASE_URL')
        if url and not url.startswith('https://'):
            cls._validation_errors.append(
                "SUPABASE_URL should use HTTPS"
            )
        
        # Note: New API keys (sb_publishable_*, sb_secret_*) are not JWTs, so we skip JWT validation
        # Legacy JWT validation is only for SUPABASE_JWT_SECRET
    
    @classmethod
    def _validate_flask_config(cls):
        """Validate Flask-specific configuration."""
        flask_env = os.getenv('FLASK_ENV', 'production')
        
        if flask_env == 'production':
            # Production-specific checks
            if os.getenv('SECRET_KEY') == 'dev':
                cls._validation_errors.append(
                    "Using default SECRET_KEY 'dev' in production environment"
                )
            
            if os.getenv('FLASK_DEBUG', '').lower() in ['1', 'true']:
                cls._validation_warnings.append(
                    "Debug mode is enabled in production environment"
                )
    
    @classmethod
    def _handle_validation_results(cls, strict_mode: bool):
        """Handle validation results and decide whether to continue."""
        # Report warnings
        for warning in cls._validation_warnings:
            logger.warning(f"Configuration Warning: {warning}")
        
        # Report errors
        error_count = len(cls._validation_errors)
        if error_count > 0:
            logger.error(f"Found {error_count} configuration error(s):")
            for error in cls._validation_errors:
                logger.error(f"  - {error}")
            
            if strict_mode:
                logger.critical("Exiting due to configuration errors in strict mode")
                sys.exit(1)
            else:
                logger.warning("Continuing despite configuration errors. This may cause runtime issues.")
        else:
            logger.info("✅ All configuration validation checks passed")
    
    @classmethod
    def get_validation_status(cls) -> Dict[str, any]:
        """Get current validation status."""
        return {
            'initialized': cls._initialized,
            'errors': cls._validation_errors,
            'warnings': cls._validation_warnings,
            'has_errors': len(cls._validation_errors) > 0,
            'has_warnings': len(cls._validation_warnings) > 0,
        }
    
    @classmethod
    def get_health_check(cls) -> Dict[str, any]:
        """Get health check information for monitoring."""
        status = cls.get_validation_status()
        
        health = {
            'status': 'healthy' if not status['has_errors'] else 'unhealthy',
            'timestamp': str(Path(__file__).stat().st_mtime),
            'config_loaded': status['initialized'],
            'error_count': len(status['errors']),
            'warning_count': len(status['warnings']),
        }
        
        # Add environment info (non-sensitive)
        health['environment'] = {
            'flask_env': os.getenv('FLASK_ENV', 'unknown'),
            'has_supabase_config': bool(os.getenv('SUPABASE_URL')),
            'has_redis_config': bool(os.getenv('REDIS_PASSWORD')),
        }
        
        return health


# Initialize configuration on module import (non-strict mode for backwards compatibility)
# Applications can call ConfigManager.initialize(strict_mode=True) for stricter validation
ConfigManager.initialize(strict_mode=False)
