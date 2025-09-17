"""
Minimal Supabase client that bypasses authentication for local development
"""
import os
import logging
from typing import Optional, Dict, Any, Union

logger = logging.getLogger(__name__)

class SupabaseConfig:
    """Minimal configuration for local development"""
    
    URL = os.getenv("SUPABASE_URL", "https://kehpwxdkpdxapfxwhfwn.supabase.co")
    SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY", "")
    PUBLISHABLE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY", "")
    JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "development_secret")
    
    @classmethod
    def validate(cls) -> bool:
        logger.info("Using minimal Supabase config for local development")
        return True
    
    @classmethod
    def get_jwt_secret(cls) -> Union[str, bytes]:
        return cls.JWT_SECRET or "development_secret"

# Simple in-memory storage for local development
conversion_records = {}

class LocalSupabaseClient:
    """Local storage client for development"""
    
    def __init__(self):
        logger.info("Using local storage client for development")
    
    def table(self, table_name):
        return LocalTable(table_name)

class LocalTable:
    def __init__(self, table_name):
        self.table_name = table_name
    
    def insert(self, data):
        record_id = f"local_{len(conversion_records) + 1}"
        conversion_records[record_id] = {**data, "id": record_id}
        logger.info(f"Local insert to {self.table_name}: {data}")
        return LocalResponse(conversion_records[record_id])
    
    def update(self, data):
        logger.info(f"Local update to {self.table_name}: {data}")
        return LocalResponse(data)
    
    def select(self, columns="*"):
        return LocalQueryBuilder(self.table_name)

class LocalQueryBuilder:
    def __init__(self, table_name):
        self.table_name = table_name
        self.filters = {}
    
    def eq(self, column, value):
        self.filters[column] = value
        return self
    
    def single(self):
        """Return a single result, similar to Supabase's single() method"""
        results = []
        for record in conversion_records.values():
            match = True
            for col, val in self.filters.items():
                if record.get(col) != val:
                    match = False
                    break
            if match:
                results.append(record)
        
        logger.info(f"Local single query on {self.table_name} returned {len(results)} results")
        
        if len(results) == 0:
            return LocalResponse(None)
        elif len(results) == 1:
            return LocalResponse(results[0])
        else:
            logger.warning(f"Multiple records found for single() query on {self.table_name}")
            return LocalResponse(results[0])  # Return first result
    
    def execute(self):
        # Simple filter logic
        results = []
        for record in conversion_records.values():
            match = True
            for col, val in self.filters.items():
                if record.get(col) != val:
                    match = False
                    break
            if match:
                results.append(record)
        
        logger.info(f"Local query on {self.table_name} returned {len(results)} results")
        return LocalResponse(results)

class LocalResponse:
    def __init__(self, data):
        self.data = data
    
    def execute(self):
        """Return self to maintain compatibility with Supabase API"""
        return self

# Create local client
supabase = LocalSupabaseClient()

def verify_supabase_token(token: str) -> Optional[Dict[str, Any]]:
    """Local token verification - accepts any token for development"""
    logger.info("Local token verification - accepting token for development")
    return {"sub": "local_user", "email": "developer@localhost"}

def create_conversion_record(user_id: str, filename: str, task_id: str, status: str = "pending") -> Optional[str]:
    """Create conversion record in local storage"""
    record = {
        "user_id": user_id,
        "filename": filename,
        "task_id": task_id,
        "status": status,
        "created_at": "2025-01-16T00:00:00Z"
    }
    result = supabase.table("conversions").insert(record)
    return result.data.get("id")

def update_conversion_status(task_id: str, status: str, **kwargs) -> bool:
    """Update conversion status in local storage"""
    # Find and update record
    for record_id, record in conversion_records.items():
        if record.get("task_id") == task_id:
            record["status"] = status
            for key, value in kwargs.items():
                record[key] = value
            logger.info(f"Updated conversion {task_id}: {status}")
            return True
    
    logger.warning(f"Conversion record not found: {task_id}")
    return False

def get_user_conversions(user_id: str, limit: int = 10) -> list:
    """Get user conversions from local storage"""
    results = []
    for record in conversion_records.values():
        if record.get("user_id") == user_id:
            results.append(record)
        if len(results) >= limit:
            break
    
    logger.info(f"Retrieved {len(results)} conversions for user {user_id}")
    return results

def get_conversion_by_task_id(task_id: str) -> Optional[Dict[str, Any]]:
    """Get conversion by task ID from local storage"""
    for record in conversion_records.values():
        if record.get("task_id") == task_id:
            logger.info(f"Found conversion for task {task_id}")
            return record
    
    logger.warning(f"Conversion not found for task {task_id}")
    return None