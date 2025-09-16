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
    SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY", "")
    PUBLISHABLE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY", "")
    JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that all required configuration is present"""
        if not cls.URL:
            logger.error("SUPABASE_URL is not set")
            return False
            
        if not cls.SECRET_KEY:
            logger.error("SUPABASE_SECRET_KEY is not set")
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

# Lazy initialization of Supabase client
_supabase_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """Get or create the Supabase client"""
    global _supabase_client
    if _supabase_client is None:
        # Refresh config values in case they were loaded after module import
        from . import config  # This ensures env vars are loaded
        url = os.getenv("SUPABASE_URL", SupabaseConfig.URL)
        secret_key = os.getenv("SUPABASE_SECRET_KEY", SupabaseConfig.SECRET_KEY)
        
        logger.info(f"Initializing Supabase client with URL: {url}")
        logger.info(f"Secret key length: {len(secret_key)}")
        
        try:
            _supabase_client = create_client(url, secret_key)
            logger.info("✅ Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase client: {e}")
            logger.warning("🔄 Falling back to mock client for development")
            from .supabase_client_minimal import LocalSupabaseClient
            _supabase_client = LocalSupabaseClient()
    return _supabase_client

# For backward compatibility, create a property that behaves like the old global variable
class SupabaseClientWrapper:
    def __getattr__(self, name):
        """Forward all attribute access to the actual Supabase client"""
        return getattr(get_supabase_client(), name)

# Create wrapper instance - this won't initialize the client until accessed
supabase = SupabaseClientWrapper()

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
        logger.info(f"Verifying token with JWT secret (length: {len(SupabaseConfig.get_jwt_secret())})")
        # Decode the token with proper error handling
        payload = jwt.decode(
            token,
            SupabaseConfig.get_jwt_secret(),
            algorithms=["HS256"],
            options={"verify_aud": False}  # Don't verify audience claim
        )
        logger.info(f"Token decoded successfully. Issuer: {payload.get('iss')}, User: {payload.get('sub')[:8]}...")
        
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
        result = get_supabase_client().table('conversions').insert({
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

        result = get_supabase_client().table('conversions').update(update_data).eq('task_id', task_id).execute()
        return len(result.data) > 0
    except Exception as e:
        logger.error(f"Error updating conversion status: {e}")
        return False

def get_user_conversions(user_id: str, limit: int = 10, offset: int = 0) -> list:
    """
    Get user's conversion history
    """
    try:
        result = get_supabase_client().table('conversions')\
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
        result = get_supabase_client().table('conversions')\
            .select('*')\
            .eq('task_id', task_id)\
            .single()\
            .execute()

        return result.data
    except Exception as e:
        logger.error(f"Error getting conversion by task ID: {e}")
        return None
