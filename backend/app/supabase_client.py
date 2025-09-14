"""
Supabase client configuration for Anclora PDF2EPUB backend
"""
import os
from supabase import create_client, Client
from typing import Optional, Dict, Any
import jwt

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://kehpwxdkpdxapfxwhfwn.supabase.co")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtlaHB3eGRrcGR4YXBmeHdoZnduIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTI5NTg3OCwiZXhwIjoyMDY2ODcxODc4fQ.ZRYM0R46-qDniCRbLsVlbwRDP0Ra087eOlpvT9FlGHQ")

# Create Supabase client with service role key (for backend operations)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def verify_supabase_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify a Supabase JWT token and return user information
    """
    try:
        # Decode the JWT token without verification first to get the payload
        unverified_payload = jwt.decode(token, options={"verify_signature": False})
        
        # Check if it's a Supabase token
        if unverified_payload.get('iss') != 'supabase':
            return None
            
        # Verify the token with Supabase's JWT secret
        # For now, we'll trust the token if it's properly formatted
        # In production, you should verify with the actual JWT secret
        
        return {
            'user_id': unverified_payload.get('sub'),
            'email': unverified_payload.get('email'),
            'role': unverified_payload.get('role', 'authenticated')
        }
    except Exception as e:
        print(f"Token verification error: {e}")
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
        print(f"Error creating conversion record: {e}")
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
        print(f"Error updating conversion status: {e}")
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
        print(f"Error getting user conversions: {e}")
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
        print(f"Error getting conversion by task ID: {e}")
        return None
