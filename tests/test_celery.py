#!/usr/bin/env python3
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_celery_creation():
    """Test creating Celery instance"""
    try:
        print("Testing Celery creation...")
        
        from celery import Celery
        
        # Use the same configuration as in tasks.py
        broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
        backend_url = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
        
        print(f"Broker URL: {broker_url}")
        print(f"Backend URL: {backend_url}")
        
        # Create Celery instance
        celery_app = Celery(
            "test_tasks",
            broker=broker_url,
            backend=backend_url,
        )
        
        print("✅ Celery instance created successfully")
        
        # Test basic configuration
        print(f"Broker: {celery_app.conf.broker_url}")
        print(f"Backend: {celery_app.conf.result_backend}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create Celery instance: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tasks_import():
    """Test importing tasks module"""
    try:
        print("\nTesting tasks module import...")
        
        # Load environment variables first
        from app.config import Config
        
        # Try to import tasks
        from app import tasks
        
        print("✅ Successfully imported tasks module")
        print(f"Celery app: {tasks.celery_app}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to import tasks module: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("Celery Diagnostic Test")
    print("=" * 50)
    
    # Test 1: Basic Celery creation
    celery_ok = test_celery_creation()
    
    # Test 2: Tasks module import
    tasks_ok = test_tasks_import()
    
    print("\nSummary:")
    print("=" * 30)
    print(f"Celery creation: {'✅ OK' if celery_ok else '❌ FAILED'}")
    print(f"Tasks import: {'✅ OK' if tasks_ok else '❌ FAILED'}")
    
    if celery_ok and tasks_ok:
        print("\n✅ All Celery tests passed!")
        return 0
    else:
        print("\n❌ Some Celery tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
