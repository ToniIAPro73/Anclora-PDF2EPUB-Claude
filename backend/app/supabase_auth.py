"""
Supabase authentication decorators and utilities
"""
from functools import wraps
from flask import request, jsonify, g
from .supabase_client import verify_supabase_token, get_user_from_token

def supabase_auth_required(f):
    """
    Decorator to require Supabase authentication
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get the Authorization header
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization header'}), 401
        
        # Extract the token
        token = auth_header.split(' ', 1)[1]
        
        # Verify the token
        user_info = verify_supabase_token(token)
        if not user_info:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Store user info in Flask's g object for use in the route
        g.current_user = user_info
        g.user_id = user_info['user_id']
        
        return f(*args, **kwargs)
    
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
