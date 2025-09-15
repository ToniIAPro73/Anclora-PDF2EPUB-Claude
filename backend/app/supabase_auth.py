"""
Supabase authentication decorators and utilities
"""
import logging
from functools import wraps
from flask import request, jsonify, g, current_app
from .supabase_client import verify_supabase_token, get_user_from_token

logger = logging.getLogger(__name__)

def extract_token_from_header(auth_header):
    """
    Extract token from Authorization header
    
    Args:
        auth_header: The Authorization header value
        
    Returns:
        The token or None if not found/invalid
    """
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    # Extract the token
    return auth_header.split(' ', 1)[1]

def supabase_auth_required(f):
    """
    Decorator to require Supabase authentication
    
    This decorator:
    1. Extracts the JWT token from the Authorization header
    2. Verifies the token with Supabase
    3. Stores user info in Flask's g object
    4. Returns 401 if authentication fails
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get the Authorization header
        auth_header = request.headers.get('Authorization', '')
        
        # Extract token
        token = extract_token_from_header(auth_header)
        if not token:
            logger.warning("Missing or invalid authorization header")
            return jsonify({
                'error': 'Authentication required',
                'message': 'Missing or invalid authorization header'
            }), 401
        
        # Verify the token
        try:
            user_info = verify_supabase_token(token)
            if not user_info:
                logger.warning("Invalid or expired token")
                return jsonify({
                    'error': 'Authentication failed',
                    'message': 'Invalid or expired token'
                }), 401

            # Store user info in Flask's g object for use in the route
            g.current_user = user_info
            g.user_id = user_info['user_id']
            
            # Log successful authentication
            logger.debug(f"User authenticated: {g.user_id}")

            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return jsonify({
                'error': 'Authentication error',
                'message': 'An error occurred during authentication'
            }), 500

    return decorated_function

def get_current_user_id():
    """
    Get the current user ID from the request context
    """
    return getattr(g, 'user_id', None)

def get_current_user():
    """
    Get the current user info from the request context
    """
    return getattr(g, 'current_user', None)
