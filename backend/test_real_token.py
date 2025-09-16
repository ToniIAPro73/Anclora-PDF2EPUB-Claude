#!/usr/bin/env python3
"""
Script para probar la validación con un token real del frontend
"""

import os
import sys
import jwt
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv('.env')
load_dotenv('../.env')

def test_token_validation(token_input):
    """Test validation with a real token from frontend"""
    jwt_secret = os.getenv('SUPABASE_JWT_SECRET', '')
    
    print("=== Test Token Validation ===")
    print(f"JWT Secret length: {len(jwt_secret)}")
    print(f"Token length: {len(token_input)}")
    print(f"Token starts: {token_input[:50]}...")
    
    try:
        # First, decode without verification to see the payload
        print("\n1. Decoding token WITHOUT verification:")
        unverified = jwt.decode(token_input, options={"verify_signature": False})
        print(f"   Issuer: {unverified.get('iss')}")
        print(f"   Subject: {unverified.get('sub')}")
        print(f"   Audience: {unverified.get('aud')}")
        print(f"   Expires: {unverified.get('exp')} ({datetime.fromtimestamp(unverified.get('exp', 0))})")
        print(f"   Algorithm: {jwt.get_unverified_header(token_input).get('alg')}")
        
        # Now try with verification
        print("\n2. Decoding token WITH verification:")
        verified = jwt.decode(
            token_input,
            jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False}
        )
        print("   ✓ Token verification SUCCESSFUL!")
        print(f"   User ID: {verified.get('sub')}")
        print(f"   Email: {verified.get('email')}")
        
        return True
        
    except jwt.ExpiredSignatureError:
        print("   ✗ Token has EXPIRED")
        return False
    except jwt.InvalidSignatureError:
        print("   ✗ Invalid SIGNATURE - JWT secret mismatch")
        return False
    except jwt.InvalidTokenError as e:
        print(f"   ✗ Invalid token: {e}")
        return False
    except Exception as e:
        print(f"   ✗ Unexpected error: {e}")
        return False

def get_token_from_user():
    """Get token from user input"""
    print("\n=== Como obtener el token ===")
    print("1. Ve a http://localhost:5178 y haz login")
    print("2. Abre Developer Tools (F12)")
    print("3. Ve a Application > Local Storage > http://localhost:5178")
    print("4. Busca 'sb-' entries y copia el access_token")
    print("5. O inspecciona las requests en Network tab")
    print("\nPega el token aqui:")
    
    return input().strip()

if __name__ == "__main__":
    print("=== Token Validation Tester ===")
    
    if len(sys.argv) > 1:
        # Token provided as argument
        token = sys.argv[1]
    else:
        # Get token interactively
        token = get_token_from_user()
    
    if token and len(token) > 10:
        success = test_token_validation(token)
        if success:
            print("\n🎉 Token validation SUCCESS! Auth should work.")
        else:
            print("\n❌ Token validation FAILED. This explains the 401 error.")
    else:
        print("❌ No valid token provided")