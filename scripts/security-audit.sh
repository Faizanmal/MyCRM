#!/bin/bash
# Security Audit Script for MyCRM
# Checks for common security issues and misconfigurations

echo "=========================================="
echo "MyCRM Security Audit"
echo "=========================================="
echo ""

ISSUES_FOUND=0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_pass() {
    echo -e "${GREEN}✓${NC} $1"
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
}

# Check environment files
echo "1. Checking Environment Configuration..."
if [ -f "backend/.env" ]; then
    check_pass "Environment file exists"
    
    # Check SECRET_KEY
    if grep -q "SECRET_KEY=" backend/.env; then
        SECRET_KEY=$(grep "SECRET_KEY=" backend/.env | cut -d'=' -f2)
        if [ ${#SECRET_KEY} -lt 50 ]; then
            check_fail "SECRET_KEY is too short (should be 50+ characters)"
        else
            check_pass "SECRET_KEY has adequate length"
        fi
    else
        check_fail "SECRET_KEY not set in .env"
    fi
    
    # Check DEBUG setting
    if grep -q "DEBUG=False" backend/.env || grep -q "DEBUG=True" backend/.env; then
        DEBUG_VALUE=$(grep "DEBUG=" backend/.env | cut -d'=' -f2)
        if [ "$DEBUG_VALUE" = "False" ]; then
            check_pass "DEBUG is disabled for production"
        else
            check_warn "DEBUG is enabled - should be False in production"
        fi
    else
        check_warn "DEBUG setting not found in .env"
    fi
    
    # Check ALLOWED_HOSTS
    if grep -q "ALLOWED_HOSTS=" backend/.env; then
        check_pass "ALLOWED_HOSTS is configured"
    else
        check_fail "ALLOWED_HOSTS not configured"
    fi
else
    check_fail "Environment file not found: backend/.env"
fi

echo ""
echo "2. Checking Dependencies..."

# Check for vulnerable dependencies
if command -v safety &> /dev/null; then
    cd backend
    if safety check --json > /tmp/safety_report.json 2>/dev/null; then
        VULNERABILITIES=$(cat /tmp/safety_report.json | grep -c "vulnerabilities")
        if [ "$VULNERABILITIES" -eq 0 ]; then
            check_pass "No known vulnerabilities in dependencies"
        else
            check_fail "Found vulnerable dependencies - run 'safety check' for details"
        fi
    fi
    cd ..
else
    check_warn "safety tool not installed - cannot check dependencies"
fi

# Check for outdated packages
if [ -f "backend/requirements.txt" ]; then
    check_pass "Requirements file found"
else
    check_fail "Requirements file not found"
fi

echo ""
echo "3. Checking Security Headers..."

# Check if security middleware is configured
if grep -q "SecurityHeadersMiddleware" backend/backend/settings.py; then
    check_pass "Security headers middleware configured"
else
    check_warn "Security headers middleware not found"
fi

# Check HSTS settings
if grep -q "SECURE_HSTS_SECONDS" backend/backend/settings.py; then
    check_pass "HSTS is configured"
else
    check_warn "HSTS not configured"
fi

echo ""
echo "4. Checking Database Configuration..."

# Check for database password
if grep -q "DATABASE_PASSWORD=" backend/.env 2>/dev/null; then
    DB_PASSWORD=$(grep "DATABASE_PASSWORD=" backend/.env | cut -d'=' -f2)
    if [ -n "$DB_PASSWORD" ] && [ "$DB_PASSWORD" != "changeme" ] && [ "$DB_PASSWORD" != "password" ]; then
        check_pass "Database password is set"
    else
        check_fail "Database password is weak or using default value"
    fi
else
    check_fail "Database password not configured"
fi

echo ""
echo "5. Checking Redis Configuration..."

# Check Redis password
if grep -q "REDIS_PASSWORD=" backend/.env 2>/dev/null; then
    REDIS_PASSWORD=$(grep "REDIS_PASSWORD=" backend/.env | cut -d'=' -f2)
    if [ -n "$REDIS_PASSWORD" ]; then
        check_pass "Redis password is configured"
    else
        check_warn "Redis password is empty"
    fi
else
    check_warn "Redis password not configured"
fi

echo ""
echo "6. Checking SSL/TLS Configuration..."

# Check SSL settings
if grep -q "SESSION_COOKIE_SECURE.*True" backend/backend/settings.py; then
    check_pass "Secure cookies configured"
else
    check_warn "SESSION_COOKIE_SECURE should be True in production"
fi

if grep -q "CSRF_COOKIE_SECURE.*True" backend/backend/settings.py; then
    check_pass "CSRF cookie security enabled"
else
    check_warn "CSRF_COOKIE_SECURE should be True in production"
fi

echo ""
echo "7. Checking File Permissions..."

# Check for overly permissive files
if [ -f "backend/.env" ]; then
    PERMS=$(stat -c %a backend/.env 2>/dev/null || stat -f %A backend/.env 2>/dev/null)
    if [ "$PERMS" = "600" ] || [ "$PERMS" = "400" ]; then
        check_pass "Environment file has secure permissions"
    else
        check_warn "Environment file permissions should be 600 or 400 (current: $PERMS)"
    fi
fi

echo ""
echo "8. Checking Exposed Secrets..."

# Check for common secret patterns in git
if command -v git &> /dev/null; then
    if git rev-parse --git-dir > /dev/null 2>&1; then
        # Check if .env is in gitignore
        if grep -q "\.env" .gitignore 2>/dev/null; then
            check_pass ".env files are in .gitignore"
        else
            check_fail ".env files not in .gitignore"
        fi
        
        # Check if .env is tracked by git
        if git ls-files --error-unmatch backend/.env 2>/dev/null; then
            check_fail "Environment file is tracked by git - should be removed!"
        else
            check_pass "Environment file not tracked by git"
        fi
    fi
fi

echo ""
echo "9. Checking Monitoring & Logging..."

# Check if Sentry is configured
if grep -q "SENTRY_DSN=" backend/.env 2>/dev/null; then
    SENTRY_DSN=$(grep "SENTRY_DSN=" backend/.env | cut -d'=' -f2)
    if [ -n "$SENTRY_DSN" ]; then
        check_pass "Sentry error tracking configured"
    else
        check_warn "Sentry DSN is empty"
    fi
else
    check_warn "Sentry not configured for error tracking"
fi

# Check if logging directory exists
if [ -d "backend/logs" ]; then
    check_pass "Logging directory exists"
else
    check_warn "Logging directory not found"
fi

echo ""
echo "10. Checking Backup Configuration..."

if [ -f "scripts/backup.sh" ]; then
    check_pass "Backup script exists"
    
    # Check if backup script is executable
    if [ -x "scripts/backup.sh" ]; then
        check_pass "Backup script is executable"
    else
        check_warn "Backup script is not executable - run: chmod +x scripts/backup.sh"
    fi
else
    check_warn "Backup script not found"
fi

echo ""
echo "=========================================="
echo "Audit Summary"
echo "=========================================="

if [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "${GREEN}✓ No security issues found!${NC}"
    echo ""
    echo "Your MyCRM installation appears to be secure."
else
    echo -e "${YELLOW}Found $ISSUES_FOUND potential security issues${NC}"
    echo ""
    echo "Please review the warnings and failures above."
    echo "Refer to SECURITY_CHECKLIST.md for remediation steps."
fi

echo ""
echo "Additional recommendations:"
echo "  - Keep all dependencies up to date"
echo "  - Enable and configure automatic backups"
echo "  - Set up monitoring and alerting"
echo "  - Regularly review access logs"
echo "  - Conduct periodic security audits"
echo "  - Implement rate limiting on all endpoints"
echo ""

exit $ISSUES_FOUND
