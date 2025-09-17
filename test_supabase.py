#!/usr/bin/env python3
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_supabase_config():
    """Test Supabase configuration"""
    try:
        print("Testing Supabase configuration...")
        
        from app.config import Config
        
        print(f"SUPABASE_URL: {Config.SUPABASE_URL}")
        print(f"SUPABASE_PUBLISHABLE_KEY: {Config.SUPABASE_PUBLISHABLE_KEY[:20]}...")
        print(f"SUPABASE_SECRET_KEY: {Config.SUPABASE_SECRET_KEY[:20]}...")
        print(f"SUPABASE_JWT_SECRET length: {len(Config.SUPABASE_JWT_SECRET) if Config.SUPABASE_JWT_SECRET else 0}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to load Supabase config: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_supabase_client():
    """Test Supabase client initialization"""
    try:
        print("\nTesting Supabase client initialization...")
        
        from app.supabase_client import supabase
        
        print(f"Supabase client: {type(supabase)}")
        print(f"Supabase URL: {supabase.supabase_url if hasattr(supabase, 'supabase_url') else 'N/A'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize Supabase client: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_supabase_connection():
    """Test actual connection to Supabase"""
    try:
        print("\nTesting Supabase connection...")
        
        from app.supabase_client import supabase
        
        # Try a simple query to test connection
        # This should work even with invalid credentials (will just return an error)
        result = supabase.table('users').select('*').limit(1).execute()
        
        print(f"Connection test result: {type(result)}")
        print(f"Data: {result.data if hasattr(result, 'data') else 'N/A'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_auth_functions():
    """Test authentication functions"""
    try:
        print("\nTesting authentication functions...")
        
        from app.supabase_auth import get_current_user_id
        
        print("✅ Successfully imported auth functions")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to import auth functions: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("Supabase Connection Test")
    print("=" * 50)
    
    # Test 1: Configuration
    config_ok = test_supabase_config()
    
    # Test 2: Client initialization
    client_ok = test_supabase_client()
    
    # Test 3: Connection test
    connection_ok = test_supabase_connection()
    
    # Test 4: Auth functions
    auth_ok = test_auth_functions()
    
    print("\nSummary:")
    print("=" * 30)
    print(f"Configuration: {'✅ OK' if config_ok else '❌ FAILED'}")
    print(f"Client init: {'✅ OK' if client_ok else '❌ FAILED'}")
    print(f"Connection: {'✅ OK' if connection_ok else '❌ FAILED'}")
    print(f"Auth functions: {'✅ OK' if auth_ok else '❌ FAILED'}")
    
    if all([config_ok, client_ok, connection_ok, auth_ok]):
        print("\n✅ All Supabase tests passed!")
        return 0
    else:
        print("\n❌ Some Supabase tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
