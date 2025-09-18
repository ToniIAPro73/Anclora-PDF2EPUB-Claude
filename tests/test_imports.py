#!/usr/bin/env python3
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_import(module_name):
    """Test importing a module"""
    try:
        print(f"Testing import: {module_name}")
        __import__(module_name)
        print(f"✅ Successfully imported {module_name}")
        return True
    except Exception as e:
        print(f"❌ Failed to import {module_name}: {e}")
        return False

def main():
    print("Testing module imports...")
    print("=" * 50)
    
    # Test basic imports first
    modules_to_test = [
        'app.config',
        'app.test_routes',
        'app.simple_routes',
        'app.credits_routes',
        'app.routes',  # This one might fail
    ]
    
    results = {}
    for module in modules_to_test:
        results[module] = test_import(module)
        print()
    
    print("Summary:")
    print("=" * 50)
    for module, success in results.items():
        status = "✅ OK" if success else "❌ FAILED"
        print(f"{module}: {status}")
    
    # If routes failed, try to import Celery components separately
    if not results.get('app.routes', True):
        print("\nTesting Celery components separately...")
        print("=" * 30)
        
        celery_modules = [
            'app.tasks.celery_app',
            'app.tasks.conversion_tasks',
        ]
        
        for module in celery_modules:
            test_import(module)

if __name__ == "__main__":
    main()
