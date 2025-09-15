# 🔒 Security Migration Guide - Secret Management

## 🚨 **URGENT SECURITY NOTICE**

**Critical vulnerabilities were found in the repository configuration. This guide provides immediate steps to secure your deployment.**

**Status**: 🔴 **CRITICAL** - Immediate action required  
**Date**: January 15, 2025  
**Affected**: All deployments using exposed secrets

---

## 🔓 **Exposed Secrets Identified**

The following secrets were found **EXPOSED IN THE REPOSITORY**:

| Secret | Location | Risk Level | Action Required |
|--------|----------|------------|-----------------|
| `REDIS_PASSWORD` | `.env` | 🔴 CRITICAL | Regenerate immediately |
| `SECRET_KEY` | `.env` | 🔴 CRITICAL | Regenerate immediately |
| `SUPABASE_JWT_SECRET` | `backend/.env` | 🔴 CRITICAL | Rotate in Supabase dashboard |
| `SUPABASE_SERVICE_ROLE_KEY` | `backend/.env` | 🔴 CRITICAL | Regenerate in Supabase |
| `SUPABASE_ANON_KEY` | Multiple files | 🟡 MEDIUM | Regenerate as precaution |

---

## ⚡ **Immediate Actions (Execute NOW)**

### 1. **Generate New Secrets**

```bash
# Generate cryptographically secure secrets
python scripts/generate-secrets.py --output new-secrets.env

# View generated secrets
cat new-secrets.env
```

### 2. **Update Supabase Configuration**

1. **Login to Supabase Dashboard**: https://supabase.com/dashboard
2. **Go to Settings → API**
3. **Regenerate Service Role Key**
4. **Copy new keys to your environment**

### 3. **Update Environment Files**

```bash
# Backup current configuration (DO NOT COMMIT)
cp .env .env.backup

# Copy template
cp .env.example .env

# Edit with your new secrets
nano .env  # or use your preferred editor
```

### 4. **Restart All Services**

```bash
# Stop all services
docker-compose down

# Remove old containers and volumes (if safe)
docker-compose rm -f
docker volume rm $(docker volume ls -q)

# Start with new configuration
docker-compose up -d
```

---

## 🛡️ **Security Measures Implemented**

### ✅ **Enhanced .gitignore**
```gitignore
# Environment files (NEVER COMMIT)
.env
.env.*
!.env.example
backend/.env
backend/.env.*
frontend/.env
frontend/.env.*
supabase/.env*
```

### ✅ **Secret Generation Tool**
- **Location**: `scripts/generate-secrets.py`
- **Features**: Cryptographically secure, configurable lengths, validation
- **Usage**: `python scripts/generate-secrets.py`

### ✅ **Configuration Validation**
- **Location**: `backend/app/config.py`
- **Features**: Startup validation, weak secret detection, health checks
- **Benefits**: Prevents weak passwords, validates JWT format

### ✅ **Secure Templates**
- **Location**: `.env.example`
- **Features**: Placeholder values, documentation, generation commands

---

## 📋 **Complete Migration Checklist**

### 🔥 **Phase 1: Immediate Security (TODAY)**
- [ ] ✅ Generate new secrets using `scripts/generate-secrets.py`
- [ ] ✅ Regenerate Supabase keys in dashboard
- [ ] ✅ Update all `.env` files with new secrets
- [ ] ✅ Restart all services
- [ ] ✅ Test authentication functionality
- [ ] ✅ Verify application startup (check logs for validation errors)

### 🔐 **Phase 2: Repository Cleanup (THIS WEEK)**
- [ ] ⚠️ Remove exposed secrets from Git history (see below)
- [ ] ✅ Verify `.gitignore` is working
- [ ] ✅ Create separate environment files for different stages
- [ ] ✅ Document secret rotation procedures

### 🛡️ **Phase 3: Long-term Security (ONGOING)**
- [ ] ⚠️ Implement secret rotation schedule (every 90 days)
- [ ] ⚠️ Set up monitoring for secret exposure
- [ ] ⚠️ Create backup and recovery procedures
- [ ] ⚠️ Train team on secret management best practices

---

## 🗑️ **Removing Secrets from Git History**

**⚠️ WARNING**: This will rewrite Git history and may require coordination with team.

### Option 1: Using BFG Repo-Cleaner (Recommended)
```bash
# Install BFG (requires Java)
# Download from: https://github.com/rtyley/bfg-repo-cleaner

# Create a fresh clone
git clone --mirror https://github.com/yourusername/Anclora-PDF2EPUB-Claude.git

# Remove sensitive files
java -jar bfg.jar --delete-files ".env" Anclora-PDF2EPUB-Claude.git
java -jar bfg.jar --delete-files "*.env" Anclora-PDF2EPUB-Claude.git

# Clean up and force push
cd Anclora-PDF2EPUB-Claude.git
git reflog expire --expire=now --all && git gc --prune=now --aggressive
git push --force
```

### Option 2: Using git filter-branch
```bash
# Remove .env files from history
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch .env backend/.env frontend/.env supabase/.env.supabase' \
  --prune-empty --tag-name-filter cat -- --all

# Force push (coordinate with team)
git push origin --force --all
```

---

## 🔧 **Environment Configuration**

### **Production Environment**
```bash
# Required secrets for production
SECRET_KEY=<64-char-hex-secret>
JWT_SECRET=<64-char-hex-secret>
REDIS_PASSWORD=<32-char-urlsafe-secret>

# Supabase configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<service-role-jwt>
SUPABASE_JWT_SECRET=<supabase-jwt-secret>

# Application settings
FLASK_ENV=production
FLASK_DEBUG=false
```

### **Development Environment**
```bash
# Use different secrets for development
SECRET_KEY=<different-64-char-hex-secret>
JWT_SECRET=<different-64-char-hex-secret>
REDIS_PASSWORD=<different-32-char-secret>

# Development settings
FLASK_ENV=development
FLASK_DEBUG=true
```

---

## 🧪 **Testing the Migration**

### 1. **Configuration Validation**
```bash
# Check configuration health
python -c "
from backend.app.config import ConfigManager
import json
status = ConfigManager.get_health_check()
print(json.dumps(status, indent=2))
"
```

### 2. **Authentication Test**
```bash
# Test user registration and login
curl -X POST http://localhost/api/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'

# Should return JWT token
curl -X POST http://localhost/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'
```

### 3. **Service Health Check**
```bash
# Check all services are running
docker-compose ps

# Check application logs
docker-compose logs backend | grep -i "validation\|error"
```

---

## 📊 **Security Monitoring**

### **Add to Your Monitoring**
```yaml
# Prometheus alerts (example)
groups:
  - name: security
    rules:
      - alert: WeakSecretsDetected
        expr: config_validation_errors > 0
        for: 0m
        annotations:
          summary: "Weak secrets detected in configuration"
          
      - alert: ConfigurationErrors
        expr: config_validation_errors > 0
        for: 1m
        annotations:
          summary: "Configuration validation errors detected"
```

### **Regular Security Checks**
```bash
# Weekly secret strength check
python scripts/generate-secrets.py --validate-only

# Monthly dependency audit
cd frontend && npm audit
cd backend && pip-audit

# Quarterly full security review
python scripts/security-audit.py --full-scan
```

---

## 🚨 **Incident Response**

If you discover additional exposed secrets:

1. **IMMEDIATE**: Regenerate the compromised secrets
2. **URGENT**: Update all deployments with new secrets
3. **PRIORITY**: Review access logs for unauthorized usage
4. **FOLLOW-UP**: Document incident and improve detection

### **Emergency Contacts**
- **Security Team**: security@yourcompany.com
- **DevOps Team**: devops@yourcompany.com
- **On-Call**: Use your incident management system

---

## ✅ **Verification Steps**

After completing the migration:

### **Security Checklist**
- [ ] ✅ No secrets in `.env` files are default/weak values
- [ ] ✅ All services start without configuration errors
- [ ] ✅ Authentication works correctly
- [ ] ✅ No secrets appear in application logs
- [ ] ✅ `.gitignore` prevents future secret commits
- [ ] ✅ Team trained on new secret management procedures

### **Functional Testing**
- [ ] ✅ User registration works
- [ ] ✅ User login works
- [ ] ✅ PDF upload and conversion works
- [ ] ✅ File preview works
- [ ] ✅ Conversion history accessible
- [ ] ✅ All API endpoints respond correctly

---

## 📚 **Additional Resources**

- **OWASP Secrets Management**: https://owasp.org/www-project-secrets-management/
- **NIST Guidelines**: https://csrc.nist.gov/publications/detail/sp/800-57-part-1/rev-5/final
- **Supabase Security**: https://supabase.com/docs/guides/platform/security

---

**Migration Guide Version**: 1.0  
**Last Updated**: January 15, 2025  
**Next Review**: February 15, 2025

---

> 🔒 **Remember**: Security is an ongoing process. Regular audits, secret rotation, and team training are essential for maintaining a secure application.