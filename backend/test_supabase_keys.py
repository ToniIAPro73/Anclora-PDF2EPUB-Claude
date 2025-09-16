#!/usr/bin/env python3
"""Test script to verify Supabase API keys"""

import os
import sys
from dotenv import load_dotenv

def test_supabase_keys():
    # Load environment variables
    load_dotenv('../.env')
    
    pub_key = os.getenv('SUPABASE_PUBLISHABLE_KEY', '')
    secret_key = os.getenv('SUPABASE_SECRET_KEY', '')
    url = os.getenv('SUPABASE_URL', '')
    
    print("=== Supabase API Keys Test ===")
    print(f"URL: {url}")
    print(f"Publishable Key: {pub_key}")
    print(f"Secret Key: {secret_key}")
    print(f"Publishable Key length: {len(pub_key)}")
    print(f"Secret Key length: {len(secret_key)}")
    
    # Test connection with actual Supabase client
    try:
        from supabase import create_client
        print("\n=== Testing Connection ===")
        
        # Try with publishable key first (safer)
        print("Testing with publishable key...")
        client_pub = create_client(url, pub_key)
        print("✅ Publishable key connection successful")
        
        # Try with secret key
        print("Testing with secret key...")
        client_secret = create_client(url, secret_key)
        print("✅ Secret key connection successful")
        
        # Test a simple query
        print("\n=== Testing API Access ===")
        result = client_secret.table('_migrations').select("*").limit(1).execute()
        print(f"✅ API query successful: {len(result.data)} results")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("This suggests the keys may be incomplete or invalid")
        
        # Check key format
        if len(pub_key) < 50:
            print("⚠️  Publishable key seems too short")
        if len(secret_key) < 50:
            print("⚠️  Secret key seems too short")

if __name__ == '__main__':
    test_supabase_keys()