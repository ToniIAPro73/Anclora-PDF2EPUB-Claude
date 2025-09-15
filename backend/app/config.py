"""
Configuration management for the Anclora PDF2EPUB application
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConfigManager:
    """
    Centralized configuration management for the application
    
    This class handles:
    1. Loading environment variables from .env files
    2. Providing access to configuration values
    3. Validating required configuration
    """
    
    _initialized = False
    
    @classmethod
    def initialize(cls):
        """Initialize the configuration manager"""
        if cls._initialized:
            return
            
        # Determine the project root directory
        project_root = Path(__file__).parent.parent  # backend directory
        
        # Load environment variables from .env file
        env_path = project_root / '.env'
        logger.info(f"Loading environment variables from: {env_path}")
        
        # Check if .env file exists
        if not env_path.exists():
            logger.warning(f".env file not found at {env_path}")
        
        # Load the .env file
        load_dotenv(dotenv_path=env_path)
        
        # Validate critical configuration
        cls._validate_critical_config()
        
        cls._initialized = True
    
    @staticmethod
    def _validate_critical_config():
        """Validate that critical configuration values are present"""
        critical_vars = [
            "SUPABASE_URL",
            "SUPABASE_SERVICE_ROLE_KEY",
            "SUPABASE_JWT_SECRET"
        ]
        
        missing = [var for var in critical_vars if not os.getenv(var)]
        
        if missing:
            logger.error(f"Missing critical environment variables: {', '.join(missing)}")
            logger.error("Authentication and database operations may fail!")
        else:
            logger.info("All critical environment variables are set")
            
        # Log the status of important variables
        logger.info(f"SUPABASE_URL: {'Set' if os.getenv('SUPABASE_URL') else 'Not set'}")
        logger.info(f"SUPABASE_JWT_SECRET: {'Set' if os.getenv('SUPABASE_JWT_SECRET') else 'Not set'}")

# Initialize configuration on module import
ConfigManager.initialize()
