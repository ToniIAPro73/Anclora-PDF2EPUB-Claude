"""
Temporary Supabase client with disabled functionality for testing
"""
import os
import logging
from typing import Optional, Dict, Any, Union

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
        """Temporarily return True to skip validation"""
        logger.warning("Using temporary Supabase client - authentication disabled")
        return True
    
    @classmethod
    def get_jwt_secret(cls) -> Union[str, bytes]:
        """Get the JWT secret, ensuring it's properly formatted"""
        return cls.JWT_SECRET or "temp_secret"

# Mock Supabase client for testing
class MockSupabaseClient:
    def __init__(self):
        logger.warning("Using mock Supabase client - no database operations will work")
    
    def table(self, table_name):
        return MockTable()

class MockTable:
    def insert(self, data):
        logger.info(f"Mock insert: {data}")
        return MockResponse({"id": "mock_id"})
    
    def update(self, data):
        logger.info(f"Mock update: {data}")
        return MockResponse({"id": "mock_id"})
    
    def select(self, columns="*"):
        logger.info(f"Mock select: {columns}")
        return MockQueryBuilder()

class MockQueryBuilder:
    def eq(self, column, value):
        logger.info(f"Mock filter: {column} = {value}")
        return self
    
    def execute(self):
        return MockResponse([])

class MockResponse:
    def __init__(self, data):
        self.data = data

# Create mock client
supabase = MockSupabaseClient()

def verify_supabase_token(token: str) -> Optional[Dict[str, Any]]:
    """Mock token verification - always returns valid user"""
    logger.warning("Mock token verification - returning test user")
    return {"sub": "mock_user_id", "email": "test@example.com"}

# Mock functions
def create_conversion_record(user_id: str, task_id: str, input_filename: str) -> Dict[str, Any]:
    logger.info(f"Mock create_conversion_record: {input_filename}")
    return {"id": "mock_record_id", "task_id": task_id, "status": "PENDING"}

def update_conversion_status(task_id: str, status: str, **kwargs) -> bool:
    logger.info(f"Mock update_conversion_status: {task_id} -> {status}")
    return True

def get_user_conversions(user_id: str, limit: int = 10) -> list:
    logger.info(f"Mock get_user_conversions: {user_id}")
    return []

def get_conversion_by_task_id(task_id: str) -> Optional[Dict[str, Any]]:
    logger.info(f"Mock get_conversion_by_task_id: {task_id}")
    return {"id": "mock_id", "status": "completed"}