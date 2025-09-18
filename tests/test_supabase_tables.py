#!/usr/bin/env python3
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_supabase_tables():
    """Test what tables exist in Supabase"""
    try:
        print("Testing Supabase tables...")
        
        from app.supabase_client import supabase
        
        # Try different tables that might exist
        tables_to_test = [
            'referrals',  # Suggested by the error message
            'conversions',
            'users',
            'profiles',
            'auth.users',  # Auth table
        ]
        
        for table_name in tables_to_test:
            try:
                print(f"\nTesting table: {table_name}")
                result = supabase.table(table_name).select('*').limit(1).execute()
                print(f"✅ Table '{table_name}' exists")
                print(f"   Data: {result.data}")
                print(f"   Count: {result.count if hasattr(result, 'count') else 'N/A'}")
            except Exception as e:
                print(f"❌ Table '{table_name}' error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to test tables: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_auth_users():
    """Test auth.users table specifically"""
    try:
        print("\n" + "="*50)
        print("Testing auth.users table...")
        
        from app.supabase_client import supabase
        
        # Try to access auth users (this might require service role)
        result = supabase.auth.admin.list_users()
        print(f"✅ Auth users query successful")
        print(f"   Users count: {len(result.users) if hasattr(result, 'users') else 'N/A'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to query auth users: {e}")
        return False

def main():
    print("Supabase Tables Test")
    print("=" * 50)
    
    # Test 1: Check available tables
    tables_ok = test_supabase_tables()
    
    # Test 2: Check auth users
    auth_ok = test_auth_users()
    
    print("\nSummary:")
    print("=" * 30)
    print(f"Tables test: {'✅ OK' if tables_ok else '❌ FAILED'}")
    print(f"Auth test: {'✅ OK' if auth_ok else '❌ FAILED'}")
    
    if tables_ok:
        print("\n✅ Supabase connection is working!")
        return 0
    else:
        print("\n❌ Supabase connection issues!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
