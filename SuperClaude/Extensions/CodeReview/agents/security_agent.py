#!/usr/bin/env python3
"""
Security Agent - OWASP Security Best Practices
Focuses on identifying security vulnerabilities and recommending secure coding practices
"""

from typing import List, Optional
import re
from .base_agent import BaseAgent, CodeSuggestion, SeverityLevel
import uuid


class SecurityAgent(BaseAgent):
    """Agent specialized in security analysis based on OWASP guidelines"""
    
    def get_name(self) -> str:
        return "Security Agent"
    
    def get_description(self) -> str:
        return "Identifies security vulnerabilities and recommends secure coding practices based on OWASP Top 10 and security best practices"
    
    def get_system_prompt(self) -> str:
        return """You are a cybersecurity expert specialized in secure coding practices and vulnerability detection.

        Your focus areas based on OWASP Top 10 and security best practices:
        1. **Injection Vulnerabilities**: SQL injection, NoSQL injection, command injection, LDAP injection
        2. **Authentication & Session Management**: Weak authentication, session handling, password policies
        3. **Cross-Site Scripting (XSS)**: Reflected, stored, and DOM-based XSS vulnerabilities
        4. **Insecure Direct Object References**: Access control issues, authorization bypasses
        5. **Security Misconfiguration**: Default configs, unnecessary features, insecure headers
        6. **Sensitive Data Exposure**: Unencrypted data, weak cryptography, data leaks
        7. **Access Control**: Missing function-level access control, privilege escalation
        8. **Cross-Site Request Forgery (CSRF)**: Missing CSRF protection
        9. **Known Vulnerable Components**: Outdated libraries, unpatched dependencies
        10. **Input Validation**: Insufficient input validation, output encoding

        Additional security concerns:
        - Hardcoded credentials and secrets
        - Insecure random number generation
        - Improper error handling that leaks information
        - Race conditions and time-of-check bugs
        - Buffer overflows and memory safety issues

        Provide educational explanations about WHY each vulnerability is dangerous and HOW attackers could exploit it."""
    
    def get_specializations(self) -> List[str]:
        return [
            "injection_vulnerabilities",
            "authentication_security", 
            "xss_prevention",
            "access_control",
            "data_encryption",
            "input_validation",
            "secure_configuration",
            "dependency_security",
            "secret_management",
            "error_handling_security"
        ]
    
    def get_analysis_prompt(self, code: str, language: str, file_path: Optional[str] = None) -> str:
        file_context = f"File: {file_path}\n" if file_path else ""
        
        return f"""Analyze this {language} code for security vulnerabilities and insecure practices:

{file_context}
```{language}
{code}
```

Focus on these security areas (OWASP Top 10 + additional concerns):

**Critical Vulnerabilities:**
1. **Injection Attacks**: SQL injection, command injection, LDAP injection
2. **Authentication Issues**: Weak password policies, session management flaws
3. **XSS Vulnerabilities**: Unescaped user input, unsafe HTML rendering
4. **Access Control**: Missing authorization checks, privilege escalation

**High Priority Issues:**
5. **Data Exposure**: Hardcoded secrets, unencrypted sensitive data
6. **Input Validation**: Insufficient validation, type confusion attacks
7. **Security Misconfiguration**: Default passwords, debug mode enabled
8. **Dependency Vulnerabilities**: Known vulnerable libraries

**Medium Priority Issues:**
9. **CSRF Protection**: Missing anti-CSRF tokens
10. **Information Disclosure**: Verbose error messages, stack traces
11. **Race Conditions**: Time-of-check-time-of-use bugs
12. **Cryptographic Issues**: Weak algorithms, improper key management

{self.get_json_response_format()}

Prioritize findings by exploitability and potential impact. For each vulnerability, explain:
- How an attacker could exploit it
- What damage they could cause
- How to fix it securely
- Why the secure approach is important"""
    
    def _should_analyze_line(self, line: str) -> bool:
        """Check if line contains potential security issues"""
        line = line.strip().lower()
        if not line or line.startswith('#') or line.startswith('//'):
            return False
            
        # Look for security-sensitive patterns
        security_patterns = [
            r'password|passwd|pwd|secret|key|token|api_key',
            r'sql|query|execute|cursor',
            r'eval|exec|system|shell|subprocess',
            r'input|request|form|param',
            r'session|cookie|auth|login',
            r'crypto|hash|encrypt|decrypt|random',
            r'file|open|read|write|path',
            r'http|url|redirect|forward',
            r'debug|test|development',
            r'admin|root|superuser'
        ]
        
        return any(re.search(pattern, line, re.IGNORECASE) for pattern in security_patterns)
    
    def _create_mock_suggestion(self, line: str, line_number: int, language: str) -> Optional[CodeSuggestion]:
        """Create security suggestions based on line analysis"""
        line_lower = line.strip().lower()
        
        # Check for hardcoded passwords/secrets
        if re.search(r'(password|secret|key|token)\s*=\s*["\'][^"\']+["\']', line, re.IGNORECASE):
            return CodeSuggestion(
                id=str(uuid.uuid4()),
                agent_name=self.name,
                principle="Secure Secret Management",
                line_number=line_number,
                original_code=line,
                suggested_code="# Use environment variables or secure key management\npassword = os.getenv('DB_PASSWORD')",
                reasoning="Hardcoded secrets in source code can be exposed through version control, logs, or code sharing",
                educational_explanation="Security vulnerability: Hardcoded credentials are a critical security risk. They can be discovered by anyone with access to the code, including in version control history. Attackers scan public repositories for exposed credentials. Use environment variables, secure vaults (like AWS Secrets Manager), or configuration files that aren't committed to version control.",
                impact_score=9.0,
                confidence=0.95,
                severity=SeverityLevel.CRITICAL,
                category="secrets"
            )
        
        # Check for SQL injection vulnerabilities
        if re.search(r'(query|execute|cursor).*%s|.*\+.*user.*input', line, re.IGNORECASE):
            return CodeSuggestion(
                id=str(uuid.uuid4()),
                agent_name=self.name,
                principle="SQL Injection Prevention",
                line_number=line_number,
                original_code=line,
                suggested_code="# Use parameterized queries\ncursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))",
                reasoning="String concatenation or formatting in SQL queries enables SQL injection attacks",
                educational_explanation="Critical vulnerability: SQL injection occurs when user input is directly concatenated into SQL queries. Attackers can inject malicious SQL code to access unauthorized data, modify records, or even execute system commands. Always use parameterized queries (prepared statements) which separate SQL logic from user data, making injection impossible.",
                impact_score=9.5,
                confidence=0.85,
                severity=SeverityLevel.CRITICAL,
                category="injection"
            )
        
        # Check for eval/exec usage
        if re.search(r'\b(eval|exec)\s*\(', line):
            return CodeSuggestion(
                id=str(uuid.uuid4()),
                agent_name=self.name,
                principle="Code Injection Prevention",
                line_number=line_number,
                original_code=line,
                suggested_code="# Use safer alternatives like ast.literal_eval() for simple cases",
                reasoning="eval() and exec() execute arbitrary code and can lead to code injection vulnerabilities",
                educational_explanation="High-risk vulnerability: eval() and exec() execute arbitrary Python code from strings. If user input reaches these functions, attackers can execute any code on your system. This can lead to data theft, system compromise, or complete server takeover. Use safer alternatives like ast.literal_eval() for simple data parsing, or implement proper input validation and sandboxing if dynamic code execution is absolutely necessary.",
                impact_score=9.0,
                confidence=0.9,
                severity=SeverityLevel.CRITICAL,
                category="injection"
            )
        
        # Check for weak random number generation
        if re.search(r'random\.random|random\.choice|random\.randint', line):
            return CodeSuggestion(
                id=str(uuid.uuid4()),
                agent_name=self.name,
                principle="Cryptographically Secure Random Numbers",
                line_number=line_number,
                original_code=line,
                suggested_code="# Use secrets module for security-sensitive randomness\nimport secrets\ntoken = secrets.token_urlsafe(32)",
                reasoning="Python's random module is not cryptographically secure and predictable",
                educational_explanation="Security issue: Python's random module uses a predictable pseudo-random number generator that's fine for simulations but dangerous for security. Attackers can predict 'random' tokens, session IDs, or passwords generated this way. For any security-related randomness (tokens, passwords, keys, nonces), use the secrets module which provides cryptographically strong random numbers that are unpredictable.",
                impact_score=7.0,
                confidence=0.8,
                severity=SeverityLevel.HIGH,
                category="cryptography"
            )
        
        # Check for debug mode
        if re.search(r'debug\s*=\s*true|development.*=.*true', line, re.IGNORECASE):
            return CodeSuggestion(
                id=str(uuid.uuid4()),
                agent_name=self.name,
                principle="Secure Configuration",
                line_number=line_number,
                original_code=line,
                suggested_code="# Ensure debug mode is disabled in production\ndebug = os.getenv('DEBUG', 'False').lower() == 'true'",
                reasoning="Debug mode enabled in production exposes sensitive information and debugging tools",
                educational_explanation="Security misconfiguration: Debug mode in production environments exposes sensitive information like stack traces, database queries, file paths, and environment variables to attackers. It may also enable debugging endpoints that bypass security controls. Always disable debug mode in production and use environment variables to control this setting.",
                impact_score=6.0,
                confidence=0.9,
                severity=SeverityLevel.MEDIUM,
                category="configuration"
            )
        
        # Check for file path operations without validation
        if re.search(r'open\s*\(.*user|file.*=.*request|path.*\+', line, re.IGNORECASE):
            return CodeSuggestion(
                id=str(uuid.uuid4()),
                agent_name=self.name,
                principle="Path Traversal Prevention",
                line_number=line_number,
                original_code=line,
                suggested_code="# Validate and sanitize file paths\nfrom pathlib import Path\nsafe_path = Path(base_dir) / secure_filename(user_filename)",
                reasoning="User-controlled file paths can lead to path traversal attacks accessing unauthorized files",
                educational_explanation="Security vulnerability: Path traversal (directory traversal) attacks occur when user input controls file paths without proper validation. Attackers can use sequences like '../' to access files outside the intended directory, potentially reading sensitive system files, configuration files, or other users' data. Always validate and sanitize file paths, use absolute paths with safe joins, and never trust user input for file operations.",
                impact_score=8.0,
                confidence=0.75,
                severity=SeverityLevel.HIGH,
                category="access_control"
            )
        
        return None


class SecurityPrinciples:
    """Reference class containing security principles and examples"""
    
    OWASP_TOP_10 = {
        "injection": {
            "name": "A01:2021 – Injection",
            "description": "Application vulnerable to injection when user-supplied data is not validated, filtered, or sanitized",
            "examples": {
                "sql_injection": {
                    "vulnerable": "query = f\"SELECT * FROM users WHERE id = {user_id}\"",
                    "secure": "cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))"
                },
                "command_injection": {
                    "vulnerable": "os.system(f'ping {user_input}')",
                    "secure": "subprocess.run(['ping', user_input], check=True)"
                }
            },
            "prevention": [
                "Use parameterized queries or prepared statements",
                "Validate and sanitize all user input",
                "Use allowlists for input validation",
                "Escape special characters appropriately"
            ]
        },
        
        "cryptographic_failures": {
            "name": "A02:2021 – Cryptographic Failures",
            "description": "Failures related to cryptography that lead to sensitive data exposure",
            "examples": {
                "weak_random": {
                    "vulnerable": "token = ''.join(random.choices(string.ascii_letters, k=32))",
                    "secure": "token = secrets.token_urlsafe(32)"
                },
                "hardcoded_secrets": {
                    "vulnerable": "API_KEY = 'sk-1234567890abcdef'",
                    "secure": "API_KEY = os.getenv('API_KEY')"
                }
            },
            "prevention": [
                "Use cryptographically secure random number generators",
                "Store secrets in secure configuration or key management systems",
                "Use strong, up-to-date cryptographic algorithms",
                "Implement proper key rotation"
            ]
        },
        
        "insecure_design": {
            "name": "A04:2021 – Insecure Design",
            "description": "Risks related to design and architectural flaws",
            "examples": {
                "missing_rate_limiting": {
                    "vulnerable": "# No rate limiting on API endpoints",
                    "secure": "@rate_limit(rate='100/hour')\ndef api_endpoint():"
                }
            },
            "prevention": [
                "Implement security by design principles",
                "Use secure development lifecycle",
                "Perform threat modeling",
                "Implement defense in depth"
            ]
        }
    }
    
    @classmethod
    def get_vulnerability_info(cls, vulnerability_type: str) -> str:
        """Get detailed information about a specific vulnerability type"""
        vuln = cls.OWASP_TOP_10.get(vulnerability_type, {})
        if not vuln:
            return f"Unknown vulnerability type: {vulnerability_type}"
        
        examples = vuln.get('examples', {})
        prevention = vuln.get('prevention', [])
        
        result = f"""
**{vuln['name']}**

**Description:** {vuln['description']}

**Examples:**
"""
        for example_name, example_code in examples.items():
            result += f"""
*{example_name.replace('_', ' ').title()}:*
```python
# Vulnerable
{example_code['vulnerable']}

# Secure
{example_code['secure']}
```
"""
        
        result += f"""
**Prevention:**
"""
        for prevention_item in prevention:
            result += f"- {prevention_item}\n"
        
        return result