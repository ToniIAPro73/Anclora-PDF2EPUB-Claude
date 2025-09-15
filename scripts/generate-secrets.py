#!/usr/bin/env python3
"""
Secure Secret Generator for Anclora PDF2EPUB
============================================

This script generates cryptographically secure secrets for the application.
Run this script to generate new secrets when setting up the application
or when secrets have been compromised.

Usage:
    python scripts/generate-secrets.py
    python scripts/generate-secrets.py --format env
    python scripts/generate-secrets.py --format json
    python scripts/generate-secrets.py --rotate-all

Security Features:
- Uses cryptographically secure random generation
- Generates keys of appropriate length for each use case
- Outputs in multiple formats for different deployment scenarios
- Includes validation of generated secrets

Author: Anclora Security Team
Date: January 2025
"""

import secrets
import string
import json
import argparse
import sys
from datetime import datetime, timezone
from typing import Dict, Any

# Ensure proper encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')


class SecretGenerator:
    """Cryptographically secure secret generator."""
    
    # Minimum lengths for different types of secrets
    SECRET_LENGTHS = {
        'SECRET_KEY': 64,      # Flask session encryption
        'JWT_SECRET': 64,      # JWT token signing
        'REDIS_PASSWORD': 32,  # Redis authentication
        'API_KEY': 32,         # General API keys
        'ENCRYPTION_KEY': 32,  # General encryption
    }
    
    @staticmethod
    def generate_hex_secret(length: int = 32) -> str:
        """Generate a hex-encoded secret of specified length."""
        return secrets.token_hex(length)
    
    @staticmethod
    def generate_urlsafe_secret(length: int = 32) -> str:
        """Generate a URL-safe base64-encoded secret."""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def generate_alphanumeric_secret(length: int = 32) -> str:
        """Generate an alphanumeric secret."""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def generate_password(length: int = 24, include_symbols: bool = True) -> str:
        """Generate a strong password."""
        alphabet = string.ascii_letters + string.digits
        if include_symbols:
            alphabet += "!@#$%^&*-_=+"
        
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        
        # Ensure password contains at least one character from each category
        if include_symbols:
            while not (any(c.islower() for c in password) and
                      any(c.isupper() for c in password) and
                      any(c.isdigit() for c in password) and
                      any(c in "!@#$%^&*-_=+" for c in password)):
                password = ''.join(secrets.choice(alphabet) for _ in range(length))
        
        return password
    
    def generate_all_secrets(self) -> Dict[str, str]:
        """Generate all required secrets for the application."""
        secrets_dict = {
            # Flask application secrets
            'SECRET_KEY': self.generate_hex_secret(self.SECRET_LENGTHS['SECRET_KEY']),
            'JWT_SECRET': self.generate_hex_secret(self.SECRET_LENGTHS['JWT_SECRET']),
            
            # Database and cache
            'REDIS_PASSWORD': self.generate_urlsafe_secret(self.SECRET_LENGTHS['REDIS_PASSWORD']),
            
            # Additional security tokens
            'API_KEY': self.generate_urlsafe_secret(self.SECRET_LENGTHS['API_KEY']),
            'ENCRYPTION_KEY': self.generate_hex_secret(self.SECRET_LENGTHS['ENCRYPTION_KEY']),
            
            # Metadata
            'GENERATED_AT': datetime.now(timezone.utc).isoformat(),
            'GENERATOR_VERSION': '1.0.0',
        }
        
        return secrets_dict


class OutputFormatter:
    """Handles different output formats for generated secrets."""
    
    @staticmethod
    def format_env(secrets_dict: Dict[str, str]) -> str:
        """Format secrets as environment variables."""
        lines = [
            "# ==============================================================================",
            "# GENERATED SECRETS - Anclora PDF2EPUB",
            f"# Generated at: {secrets_dict.get('GENERATED_AT', 'Unknown')}",
            "# ==============================================================================",
            "# SECURITY WARNING: Keep these secrets secure and never commit to version control!",
            "# ==============================================================================",
            "",
        ]
        
        # Flask secrets
        lines.extend([
            "# Flask application secrets",
            f"SECRET_KEY={secrets_dict['SECRET_KEY']}",
            f"JWT_SECRET={secrets_dict['JWT_SECRET']}",
            "",
        ])
        
        # Database secrets
        lines.extend([
            "# Database and cache secrets",
            f"REDIS_PASSWORD={secrets_dict['REDIS_PASSWORD']}",
            "",
        ])
        
        # Additional secrets
        lines.extend([
            "# Additional API secrets (optional)",
            f"# API_KEY={secrets_dict['API_KEY']}",
            f"# ENCRYPTION_KEY={secrets_dict['ENCRYPTION_KEY']}",
            "",
        ])
        
        # Instructions
        lines.extend([
            "# ==============================================================================",
            "# SETUP INSTRUCTIONS:",
            "# 1. Copy these values to your .env file",
            "# 2. Update Supabase secrets in your Supabase dashboard",
            "# 3. Restart all services",
            "# 4. Test authentication functionality",
            "# ==============================================================================",
        ])
        
        return "\n".join(lines)
    
    @staticmethod
    def format_json(secrets_dict: Dict[str, str]) -> str:
        """Format secrets as JSON."""
        return json.dumps(secrets_dict, indent=2, sort_keys=True)
    
    @staticmethod
    def format_docker_compose(secrets_dict: Dict[str, str]) -> str:
        """Format secrets for docker-compose environment section."""
        lines = [
            "    environment:",
            f"      - SECRET_KEY={secrets_dict['SECRET_KEY']}",
            f"      - JWT_SECRET={secrets_dict['JWT_SECRET']}",
            f"      - REDIS_PASSWORD={secrets_dict['REDIS_PASSWORD']}",
        ]
        return "\n".join(lines)


def validate_secrets(secrets_dict: Dict[str, str]) -> bool:
    """Validate that generated secrets meet security requirements."""
    required_keys = ['SECRET_KEY', 'JWT_SECRET', 'REDIS_PASSWORD']
    
    for key in required_keys:
        if key not in secrets_dict:
            print(f"ERROR: Missing required secret: {key}", file=sys.stderr)
            return False
        
        value = secrets_dict[key]
        min_length = SecretGenerator.SECRET_LENGTHS.get(key, 32)
        
        if len(value) < min_length:
            print(f"ERROR: Secret {key} is too short: {len(value)} < {min_length}", file=sys.stderr)
            return False
        
        # Check for weak patterns
        if value.lower() in ['test', 'password', 'secret', 'key']:
            print(f"ERROR: Secret {key} contains weak pattern", file=sys.stderr)
            return False
    
    print("SUCCESS: All secrets validation passed")
    return True


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Generate secure secrets for Anclora PDF2EPUB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Generate secrets in env format
  %(prog)s --format json      # Generate secrets in JSON format
  %(prog)s --output secrets.env  # Save to file
  %(prog)s --rotate-all      # Generate new secrets for rotation
        """
    )
    
    parser.add_argument(
        '--format', 
        choices=['env', 'json', 'docker'], 
        default='env',
        help='Output format (default: env)'
    )
    
    parser.add_argument(
        '--output', 
        type=str,
        help='Output file (default: stdout)'
    )
    
    parser.add_argument(
        '--rotate-all',
        action='store_true',
        help='Generate all new secrets for rotation'
    )
    
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate existing secrets in .env file'
    )
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = SecretGenerator()
    formatter = OutputFormatter()
    
    if args.validate_only:
        # TODO: Implement validation of existing .env file
        print("Validation feature not implemented yet")
        return
    
    # Generate secrets
    print("🔐 Generating cryptographically secure secrets...", file=sys.stderr)
    secrets_dict = generator.generate_all_secrets()
    
    # Validate generated secrets
    if not validate_secrets(secrets_dict):
        print("❌ Secret validation failed!", file=sys.stderr)
        sys.exit(1)
    
    # Format output
    if args.format == 'env':
        output = formatter.format_env(secrets_dict)
    elif args.format == 'json':
        output = formatter.format_json(secrets_dict)
    elif args.format == 'docker':
        output = formatter.format_docker_compose(secrets_dict)
    else:
        output = formatter.format_env(secrets_dict)
    
    # Write output
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"✅ Secrets written to {args.output}", file=sys.stderr)
        except IOError as e:
            print(f"❌ Error writing to file {args.output}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(output)
    
    # Security reminder
    if not args.output:
        print("\n" + "="*80, file=sys.stderr)
        print("🔒 SECURITY REMINDER:", file=sys.stderr)
        print("- Keep these secrets secure and never commit to version control", file=sys.stderr)
        print("- Rotate secrets regularly (every 90 days recommended)", file=sys.stderr)
        print("- Use different secrets for different environments", file=sys.stderr)
        print("="*80, file=sys.stderr)


if __name__ == '__main__':
    main()