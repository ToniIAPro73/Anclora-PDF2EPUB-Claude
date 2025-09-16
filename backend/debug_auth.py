#!/usr/bin/env python3
"""
Debug script to test authentication flow
"""

import os
import sys
import jwt
import base64
from dotenv import load_dotenv

# Load environment
load_dotenv('.env')
load_dotenv('../.env')

def test_jwt_secret():
    """Test the JWT secret configuration"""
    jwt_secret = os.getenv('SUPABASE_JWT_SECRET', '')
    
    print("=== JWT Secret Debug ===")
    print(f"Raw secret: {jwt_secret}")
    print(f"Length: {len(jwt_secret)}")
    
    # Test different ways to decode the secret
    print("\n=== Testing secret formats ===")
    
    # 1. Raw secret
    try:
        test_token = "test.payload.signature"
        print("1. Testing raw secret...")
        print(f"   Secret type: {type(jwt_secret)}")
    except Exception as e:
        print(f"   Error with raw: {e}")
    
    # 2. Base64 decode
    try:
        print("2. Testing base64 decode...")
        decoded = base64.b64decode(jwt_secret)
        print(f"   Decoded length: {len(decoded)}")
        print(f"   Decoded type: {type(decoded)}")
    except Exception as e:
        print(f"   Error with base64: {e}")
    
    # 3. Test with PyJWT
    try:
        print("3. Testing JWT library compatibility...")
        # Create a test token
        test_payload = {"test": "data", "iss": "supabase"}
        token = jwt.encode(test_payload, jwt_secret, algorithm="HS256")
        print(f"   Test token created: {token[:50]}...")
        
        # Try to decode it
        decoded_payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
        print(f"   ✓ JWT encode/decode works!")
        print(f"   Decoded payload: {decoded_payload}")
        
    except Exception as e:
        print(f"   ✗ JWT error: {e}")

def test_with_real_token():
    """Test with a real token from frontend"""
    print("\n=== Real Token Test ===")
    print("To test with a real token:")
    print("1. Open browser dev tools")
    print("2. Go to Application/Storage > Local Storage")
    print("3. Look for Supabase session data")
    print("4. Copy the access_token value")
    print("5. Paste it here to test validation")

if __name__ == "__main__":
    test_jwt_secret()
    test_with_real_token()