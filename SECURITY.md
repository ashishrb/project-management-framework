# Security Implementation Guide

## Overview
This document outlines the security implementations added to the GenAI Metrics Dashboard to address critical security vulnerabilities.

## Implemented Security Features

### 1. Rate Limiting Middleware
- **Location**: `app/middleware/rate_limiting.py`
- **Features**:
  - Redis-based rate limiting
  - Different limits for different endpoint types
  - Per-IP and per-user rate limiting
  - Configurable rate limits
  - Rate limit headers in responses

**Rate Limits**:
- Default: 100 requests/minute
- Auth endpoints: 10 requests/minute
- API endpoints: 200 requests/minute
- Upload endpoints: 20 requests/minute
- Export endpoints: 10 requests/minute
- AI endpoints: 50 requests/minute

### 2. Security Headers Middleware
- **Location**: `app/middleware/security.py`
- **Headers Implemented**:
  - `X-Frame-Options: DENY`
  - `X-Content-Type-Options: nosniff`
  - `X-XSS-Protection: 1; mode=block`
  - `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `X-DNS-Prefetch-Control: off`
  - `Permissions-Policy` with restrictive settings
  - `Cross-Origin-Embedder-Policy: require-corp`
  - `Cross-Origin-Opener-Policy: same-origin`
  - `Cross-Origin-Resource-Policy: same-origin`

### 3. CSRF Protection
- **Location**: `app/middleware/csrf.py`
- **Features**:
  - Token generation and validation
  - HMAC-based token signing
  - Token expiry (1 hour default)
  - Session-based token binding
  - Automatic token refresh

**Usage**:
```javascript
// Get CSRF token
const response = await fetch('/csrf-token');
const { csrf_token } = await response.json();

// Include in requests
fetch('/api/endpoint', {
    method: 'POST',
    headers: {
        'X-CSRF-Token': csrf_token,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
});
```

### 4. Input Validation & Sanitization
- **Location**: `app/middleware/validation.py`
- **Protections**:
  - SQL injection prevention
  - XSS protection
  - Path traversal prevention
  - Command injection prevention
  - File upload validation
  - Input sanitization and length limits

**Validation Features**:
- Email format validation
- URL format validation
- Phone number validation
- Date format validation
- File type and size validation

### 5. Enhanced Error Handling
- **Location**: `app/core/error_handler.py`
- **Features**:
  - Structured error responses
  - Error code standardization
  - Request ID tracking
  - Error monitoring and alerting
  - Detailed error logging

**Error Codes**:
- `AUTH_*`: Authentication errors
- `VAL_*`: Validation errors
- `DB_*`: Database errors
- `EXT_*`: External service errors
- `RATE_*`: Rate limiting errors
- `SEC_*`: Security errors
- `SYS_*`: System errors

### 6. Secrets Management
- **Location**: `app/core/secrets.py`
- **Features**:
  - Encrypted secret storage
  - Secure token generation
  - Password hashing with PBKDF2
  - Secret strength validation
  - Master key management

### 7. Compression Middleware
- **Location**: `app/middleware/compression.py`
- **Features**:
  - Gzip compression
  - Configurable compression levels
  - Size-based compression decisions
  - Content-type filtering

## Configuration

### Environment Variables
```bash
# Security
SECRET_KEY=your-secret-key-here
MASTER_ENCRYPTION_KEY=your-master-key-here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/db

# Redis
REDIS_URL=redis://localhost:6379

# CORS (comma-separated)
BACKEND_CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Rate Limiting
RATE_LIMIT_ENABLED=true
API_RATE_LIMIT_PER_MINUTE=200

# Security Headers
SECURITY_HEADERS_ENABLED=true
HSTS_MAX_AGE=31536000

# CSRF
CSRF_ENABLED=true
CSRF_TOKEN_EXPIRY=3600

# Input Validation
INPUT_VALIDATION_ENABLED=true
MAX_REQUEST_SIZE=10485760

# Compression
COMPRESSION_ENABLED=true
COMPRESSION_MIN_SIZE=1024
```

### Production Configuration
- **Location**: `app/config/production.py`
- **Features**:
  - Production-specific settings
  - Configuration validation
  - Security hardening
  - Performance optimization

## Security Best Practices

### 1. Secrets Management
- Never commit secrets to version control
- Use environment variables for sensitive data
- Rotate secrets regularly
- Use strong, unique secrets

### 2. Rate Limiting
- Monitor rate limit violations
- Adjust limits based on usage patterns
- Implement different limits for different user types
- Consider implementing progressive rate limiting

### 3. Input Validation
- Validate all input data
- Sanitize user input
- Use parameterized queries
- Implement file upload restrictions

### 4. Error Handling
- Don't expose sensitive information in errors
- Log security-related errors
- Monitor error patterns
- Implement alerting for critical errors

### 5. Headers Security
- Keep security headers up to date
- Test header effectiveness
- Monitor header violations
- Adjust CSP policies as needed

## Monitoring and Alerting

### Error Monitoring
- Endpoint: `/error-stats`
- Tracks error counts by type
- Implements alerting thresholds
- Provides error statistics

### Security Monitoring
- Rate limit violations
- CSRF token failures
- Input validation failures
- Security header violations

## Testing Security Features

### 1. Rate Limiting Tests
```bash
# Test rate limiting
for i in {1..110}; do
  curl -X GET http://localhost:8000/api/v1/projects
done
```

### 2. CSRF Protection Tests
```bash
# Test CSRF protection
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Project"}'
```

### 3. Input Validation Tests
```bash
# Test SQL injection protection
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "Test\"; DROP TABLE projects; --"}'
```

## Deployment Checklist

### Pre-Deployment
- [ ] Change default SECRET_KEY
- [ ] Configure CORS origins
- [ ] Set up Redis for rate limiting
- [ ] Configure database connection
- [ ] Test all security features
- [ ] Review security headers
- [ ] Validate input sanitization

### Post-Deployment
- [ ] Monitor error logs
- [ ] Check rate limiting effectiveness
- [ ] Verify security headers
- [ ] Test CSRF protection
- [ ] Monitor performance impact
- [ ] Review security metrics

## Security Incident Response

### 1. Rate Limit Violations
- Check for DDoS attacks
- Review IP addresses
- Adjust rate limits if needed
- Implement IP blocking if necessary

### 2. CSRF Attacks
- Review token validation logs
- Check for token reuse
- Implement additional CSRF protections
- Review form implementations

### 3. Input Validation Failures
- Review attack patterns
- Update validation rules
- Check for new attack vectors
- Implement additional sanitization

### 4. Security Header Violations
- Review CSP violations
- Update header policies
- Check for new security threats
- Implement additional headers

## Maintenance

### Regular Tasks
- Review and update rate limits
- Rotate secrets and keys
- Update security headers
- Review error logs
- Test security features
- Update dependencies

### Monthly Tasks
- Security audit
- Penetration testing
- Review access logs
- Update security policies
- Train team on security

## Support

For security-related issues or questions:
1. Check error logs first
2. Review security configuration
3. Test security features
4. Contact security team if needed

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Security Headers](https://securityheaders.com/)
- [Rate Limiting Best Practices](https://cloud.google.com/architecture/rate-limiting-strategies-techniques)
