---
allowed-tools: [Read, Grep, Glob, Edit, MultiEdit, Write, TodoWrite]
description: "Security vulnerability analysis based on OWASP Top 10 and security best practices"
---

# /security_review - Security Vulnerability Analysis

## Purpose
Identify security vulnerabilities and recommend secure coding practices based on OWASP Top 10 and cybersecurity best practices.

## Usage
```
/security_review [file_path|code_block] [--focus injection|auth|xss|access|crypto] [--severity critical|high|medium] [--owasp]
```

## Arguments
- `file_path` - Path to file to analyze for security issues
- `code_block` - Inline code to analyze (wrap in triple backticks)
- `--focus` - Focus on specific vulnerability category
- `--severity` - Filter by vulnerability severity level
- `--owasp` - Include OWASP Top 10 references and explanations

## Security Analysis Framework

### OWASP Top 10 Focus Areas
1. **A01:2021 – Injection** - SQL, NoSQL, command, and LDAP injection vulnerabilities
2. **A02:2021 – Cryptographic Failures** - Weak encryption, exposed secrets, random number issues
3. **A03:2021 – Insecure Design** - Missing security controls, threat modeling failures
4. **A04:2021 – Security Misconfiguration** - Default settings, unnecessary features
5. **A05:2021 – Vulnerable Components** - Outdated libraries, unpatched dependencies
6. **A06:2021 – Identification and Authentication Failures** - Weak auth, session management
7. **A07:2021 – Software and Data Integrity Failures** - Untrusted updates, CI/CD vulnerabilities
8. **A08:2021 – Security Logging Failures** - Insufficient logging, monitoring gaps
9. **A09:2021 – Server-Side Request Forgery** - SSRF vulnerabilities
10. **A10:2021 – Insecure Deserialization** - Unsafe object deserialization

### Additional Security Concerns
- **Input Validation** - Insufficient validation, type confusion attacks
- **Output Encoding** - XSS prevention, safe HTML rendering
- **Access Control** - Authorization bypasses, privilege escalation
- **Secret Management** - Hardcoded credentials, insecure storage
- **Error Handling** - Information disclosure through error messages
- **Race Conditions** - Time-of-check-time-of-use vulnerabilities

## Execution Process

### 1. Vulnerability Scanning
- Analyze code for known vulnerability patterns
- Check for OWASP Top 10 issues
- Identify security anti-patterns and misconfigurations
- Assess attack surface and potential impact

### 2. Educational Security Analysis
For each vulnerability, provide:
- **Vulnerability Type**: Classification (e.g., SQL Injection, XSS)
- **Attack Vector**: How an attacker could exploit this
- **Potential Impact**: What damage could be caused
- **Exploitation Example**: Concrete attack scenario
- **Secure Fix**: Step-by-step remediation guidance
- **Prevention Strategy**: How to avoid this class of vulnerability

### 3. Risk Assessment
- **Exploitability**: How easy it is to exploit (Low/Medium/High)
- **Impact**: Potential damage if exploited (Low/Medium/High/Critical)
- **CVSS Score**: Industry-standard vulnerability scoring
- **Priority**: Recommended fix order based on risk

## Example Output Format

```
🛡️ Security Vulnerability Analysis

🚨 CRITICAL: SQL Injection Vulnerability
📍 Line 42: cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

⚔️ Attack Vector: 
   An attacker could inject malicious SQL by providing:
   user_id = "1; DROP TABLE users; --"
   
💥 Potential Impact:
   - Complete database compromise
   - Data theft and manipulation  
   - Potential system takeover
   
🔧 Secure Fix:
   cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
   
📚 Why This Works:
   Parameterized queries separate SQL logic from user data, making
   injection impossible. The database treats user input as pure data,
   never as executable code.

🎯 OWASP Reference: A01:2021 – Injection
📊 CVSS Score: 9.8 (Critical)

---

⚠️ HIGH: Hardcoded Secret Exposure  
📍 Line 8: API_KEY = "sk-1234567890abcdef"

⚔️ Attack Vector:
   - Secrets visible in source code
   - Exposed through version control
   - Discoverable in public repositories
   
💥 Potential Impact:
   - Unauthorized API access
   - Service abuse and billing theft
   - Data breach through compromised credentials
   
🔧 Secure Fix:
   import os
   API_KEY = os.getenv('API_KEY')
   if not API_KEY:
       raise ValueError("API_KEY environment variable required")
   
📚 Prevention Strategy:
   - Use environment variables for secrets
   - Implement secret rotation policies
   - Use secure key management services (AWS Secrets Manager, etc.)
   - Never commit secrets to version control

🎯 OWASP Reference: A02:2021 – Cryptographic Failures
📊 CVSS Score: 7.5 (High)
```

## Threat Modeling Integration

### Attack Surface Analysis
- **Entry Points**: User inputs, API endpoints, file uploads
- **Trust Boundaries**: Where data crosses security contexts
- **Data Flow**: How sensitive data moves through the system
- **Privilege Levels**: What permissions are required

### Common Attack Patterns
- **Injection Attacks**: SQL, NoSQL, Command, LDAP injection
- **Cross-Site Scripting**: Reflected, stored, DOM-based XSS
- **Authentication Bypass**: Weak passwords, session hijacking
- **Authorization Failures**: Privilege escalation, IDOR vulnerabilities
- **Data Exposure**: Unencrypted sensitive data, information leaks

## Integration with SuperClaude Framework

### Persona Integration
- Automatically activates **Security** persona for threat modeling mindset
- Integration with **Analyzer** persona for systematic vulnerability assessment
- Educational explanations focus on both technical and business risk

### MCP Server Usage
- **Context7**: Access latest OWASP guidelines and security patterns
- **Sequential**: Systematic security analysis across multiple attack vectors
- **Playwright**: Browser-based security testing for web applications

### Quality Gates
- ✅ All vulnerabilities include OWASP classification
- ✅ Concrete attack scenarios provided
- ✅ Step-by-step remediation guidance
- ✅ Risk assessment with CVSS scoring
- ✅ Prevention strategies for vulnerability classes

## Security Learning Outcomes

After using `/security_review`, developers will understand:
- How to identify and prevent OWASP Top 10 vulnerabilities
- Secure coding practices for their technology stack
- How attackers think and exploit vulnerabilities
- Risk assessment and vulnerability prioritization
- Implementing security controls and defense in depth

## Compliance and Standards

### Industry Standards
- **OWASP Top 10** - Web application security risks
- **SANS Top 25** - Most dangerous software errors  
- **CWE** - Common Weakness Enumeration
- **NIST Cybersecurity Framework** - Security controls

### Regulatory Compliance
- **PCI DSS** - Payment card industry security
- **HIPAA** - Healthcare data protection
- **GDPR** - European data protection regulation
- **SOX** - Financial reporting security

## Related Commands
- `/code_review` - Comprehensive analysis including security
- `/analyze --focus security` - Deep security architecture analysis
- `/improve --security` - Security-focused code improvements
- `/audit` - Comprehensive security audit with compliance checking