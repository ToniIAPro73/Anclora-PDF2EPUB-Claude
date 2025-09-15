"""
Supabase client configuration for Anclora PDF2EPUB backend
"""
import os
import logging
from supabase import create_client, Client
from typing import Optional, Dict, Any, Union
import jwt

# Configure logging
logger = logging.getLogger(__name__)

class SupabaseConfig:
    """Centralized configuration for Supabase connections and authentication"""
    
    # Base configuration
    URL = os.getenv("SUPABASE_URL", "https://kehpwxdkpdxapfxwhfwn.supabase.co")
    SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtlaHB3eGRrcGR4YXBmeHdoZnduIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTI5NTg3OCwiZXhwIjoyMDY2ODcxODc4fQ.ZRYM0R46-qDniCRbLsVlbwRDP0Ra087eOlpvT9FlGHQ")
    ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
    JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that all required configuration is present"""
        if not cls.URL:
            logger.error("SUPABASE_URL is not set")
            return False
            
        if not cls.SERVICE_ROLE_KEY:
            logger.error("SUPABASE_SERVICE_ROLE_KEY is not set")
            return False
            
        if not cls.JWT_SECRET:
            logger.error("SUPABASE_JWT_SECRET is not set")
            return False
            
        return True
    
    @classmethod
    def get_jwt_secret(cls) -> Union[str, bytes]:
        """Get the JWT secret, ensuring it's properly formatted"""
        if not cls.JWT_SECRET:
            logger.error("JWT Secret is not set!")
            return ""
        
        # Return the raw secret - PyJWT will handle the encoding
        return cls.JWT_SECRET

# Validate configuration on module load
is_valid = SupabaseConfig.validate()
if not is_valid:
    logger.warning("Supabase configuration is incomplete - authentication may fail")

# Create Supabase client with service role key (for backend operations)
supabase: Client = create_client(SupabaseConfig.URL, SupabaseConfig.SERVICE_ROLE_KEY)

def verify_supabase_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify a Supabase JWT token and return user information
    
    Args:
        token: The JWT token to verify
        
    Returns:
        Dictionary with user information or None if verification fails
    """
    if not SupabaseConfig.JWT_SECRET:
        logger.error("JWT Secret is not set! Cannot verify token.")
        return None
    
    try:
        # Decode the token with proper error handling
        payload = jwt.decode(
            token,
            SupabaseConfig.get_jwt_secret(),
            algorithms=["HS256"],
            options={"verify_aud": False}  # Don't verify audience claim
        )
        
        # Validate the token is from Supabase
        if payload.get('iss') != 'supabase':
            logger.warning(f"Token issuer is not Supabase: {payload.get('iss')}")
            return None

        # Extract and return user information
        return {
            'user_id': payload.get('sub'),
            'email': payload.get('email'),
            'role': payload.get('role', 'authenticated')
        }
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {str(e)}")
        return None

def get_user_from_token(token: str) -> Optional[str]:
    """
    Extract user ID from Supabase token
    """
    user_info = verify_supabase_token(token)
    return user_info.get('user_id') if user_info else None

def create_conversion_record(user_id: str, task_id: str, input_filename: str) -> Dict[str, Any]:
    """
    Create a new conversion record in Supabase
    """
    try:
        result = supabase.table('conversions').insert({
            'task_id': task_id,
            'user_id': user_id,
            'status': 'PENDING',
            'input_filename': input_filename
        }).execute()

        return result.data[0] if result.data else {}
    except Exception as e:
        logger.error(f"Error creating conversion record: {e}")
        return {}

def update_conversion_status(task_id: str, status: str, **kwargs) -> bool:
    """
    Update conversion status and other fields
    """
    try:
        update_data = {'status': status}
        update_data.update(kwargs)

        result = supabase.table('conversions').update(update_data).eq('task_id', task_id).execute()
        return len(result.data) > 0
    except Exception as e:
        logger.error(f"Error updating conversion status: {e}")
        return False

def get_user_conversions(user_id: str, limit: int = 10, offset: int = 0) -> list:
    """
    Get user's conversion history
    """
    try:
        result = supabase.table('conversions')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('created_at', desc=True)\
            .limit(limit)\
            .offset(offset)\
            .execute()

        return result.data
    except Exception as e:
        logger.error(f"Error getting user conversions: {e}")
        return []

def get_conversion_by_task_id(task_id: str) -> Optional[Dict[str, Any]]:
    """
    Get conversion by task ID
    """
    try:
        result = supabase.table('conversions')\
            .select('*')\
            .eq('task_id', task_id)\
            .single()\
            .execute()

        return result.data
    except Exception as e:
        logger.error(f"Error getting conversion by task ID: {e}")
        return None
