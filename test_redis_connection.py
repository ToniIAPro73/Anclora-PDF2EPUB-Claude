#!/usr/bin/env python3
import sys
import os
import redis

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_redis_connection():
    """Test Redis connection with the configured password"""
    try:
        print("Testing Redis connection...")
        
        # Use the same configuration as in the .env file
        redis_password = "XNdpx7I-taa6vZDF3ttieYd1gxs0oE9e9xHt4utbkCQ"
        redis_port = 6379
        redis_host = "localhost"
        
        # Create Redis connection
        r = redis.Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            decode_responses=True
        )
        
        # Test connection
        response = r.ping()
        print(f"✅ Redis connection successful: {response}")
        
        # Test basic operations
        r.set("test_key", "test_value")
        value = r.get("test_key")
        print(f"✅ Redis read/write test successful: {value}")
        
        # Clean up
        r.delete("test_key")
        print("✅ Redis cleanup successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

def test_celery_broker():
    """Test Celery broker URL"""
    try:
        print("\nTesting Celery broker URL...")
        
        broker_url = "redis://:XNdpx7I-taa6vZDF3ttieYd1gxs0oE9e9xHt4utbkCQ@localhost:6379/0"
        
        # Parse the URL and test connection
        import redis
        from urllib.parse import urlparse
        
        parsed = urlparse(broker_url)
        r = redis.Redis(
            host=parsed.hostname,
            port=parsed.port,
            password=parsed.password,
            db=int(parsed.path[1:]) if parsed.path else 0,
            decode_responses=True
        )
        
        response = r.ping()
        print(f"✅ Celery broker connection successful: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Celery broker connection failed: {e}")
        return False

if __name__ == "__main__":
    print("Redis Connection Test")
    print("=" * 50)
    
    redis_ok = test_redis_connection()
    celery_ok = test_celery_broker()
    
    if redis_ok and celery_ok:
        print("\n✅ All Redis tests passed!")
    else:
        print("\n❌ Some Redis tests failed!")
        sys.exit(1)
