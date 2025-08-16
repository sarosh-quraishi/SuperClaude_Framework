---
allowed-tools: [Read, Grep, Glob, Edit, MultiEdit, Write, TodoWrite, Task]
description: "Comprehensive multi-agent code review with 5 specialized AI agents providing educational feedback"
---

# /sc:code_review - Multi-Agent Code Review System

## Purpose
Execute comprehensive code review using 5 specialized AI agents that provide educational feedback through systematic analysis of Clean Code principles, security vulnerabilities, performance optimizations, design patterns, and testability improvements.

## Usage
```
/sc:code_review [file_path|code_block] [--agents all|selective] [--format interactive|report|json] [--conflicts] [--learn]
```

## Arguments
- `file_path` - Path to file to review (if not provided, analyzes current context)
- `code_block` - Inline code to review (wrap in triple backticks)
- `--agents` - Run all agents or select specific ones interactively
- `--format` - Output format (interactive diff-style, comprehensive report, or structured JSON)
- `--conflicts` - Show methodology conflicts and resolution recommendations
- `--learn` - Include educational explanations and learning insights

## Multi-Agent Architecture

### 5 Specialized Review Agents

#### 🧹 Clean Code Agent
- **Focus**: Robert C. Martin's Clean Code principles
- **Specializations**: Meaningful names, small functions, single responsibility, DRY principle
- **Educational Value**: Code readability and maintainability best practices

#### 🛡️ Security Agent  
- **Focus**: OWASP Top 10 and security best practices
- **Specializations**: Injection vulnerabilities, authentication, cryptographic failures, access control
- **Educational Value**: Security mindset and threat modeling

#### ⚡ Performance Agent
- **Focus**: Algorithm optimization and efficiency analysis
- **Specializations**: Big O complexity, memory optimization, database performance, caching
- **Educational Value**: Scalability and performance engineering

#### 🏗️ Design Patterns Agent
- **Focus**: Gang of Four patterns and SOLID principles
- **Specializations**: Creational, structural, behavioral patterns, architectural improvements
- **Educational Value**: Software architecture and design principles

#### 🧪 Testability Agent
- **Focus**: TDD best practices and code testability
- **Specializations**: Dependency injection, test isolation, mocking strategies, test coverage
- **Educational Value**: Testing mindset and quality assurance

## Execution Process

### 1. Parallel Agent Analysis
```
🤖 Initializing Multi-Agent Code Review...

⚡ Starting parallel analysis:
├── 🧹 Clean Code Agent: Analyzing code structure and naming...
├── 🛡️ Security Agent: Scanning for vulnerabilities...  
├── ⚡ Performance Agent: Evaluating algorithmic complexity...
├── 🏗️ Design Patterns Agent: Assessing architecture...
└── 🧪 Testability Agent: Checking test coverage and design...

✅ All agents completed analysis in 3.2 seconds
```

### 2. Conflict Detection & Resolution
The system automatically detects when agents provide conflicting recommendations:

```
⚠️ Methodology Conflict Detected

🧹 Clean Code Agent suggests: "Extract this into smaller functions"
⚡ Performance Agent suggests: "Keep inline for performance optimization"

📍 Conflict Location: Line 45-67 (complex calculation function)

🎯 Resolution Recommendation:
   Priority: Performance is critical for this hot path
   Compromise: Extract complex logic but keep performance-critical parts inline
   Alternative: Use profiling to measure actual impact before optimizing

📚 Learning Insight:
   This illustrates the classic trade-off between code clarity and performance.
   Always measure performance impact before sacrificing readability.
```

### 3. Educational Diff Interface
Interactive interface showing suggestions with before/after examples:

```
📁 File: user_service.py
═══════════════════════════════════════════════════════════════

📍 Line 15-18: Variable Naming Issue
┌─ 🧹 Clean Code Agent ─────────────────────────────────────────
│ 
│ ❌ Current Code:
│    temp_data = process_user_input(raw_input)
│    temp_result = validate_data(temp_data)
│    final = save_to_db(temp_result)
│ 
│ ✅ Suggested Improvement:
│    validated_user_profile = process_user_input(raw_input)
│    sanitized_profile_data = validate_data(validated_user_profile)
│    saved_user = save_to_db(sanitized_profile_data)
│ 
│ 💡 Clean Code Principle: Meaningful Names
│ 📚 Educational Explanation:
│    Generic names like 'temp_data' and 'final' don't reveal intention.
│    Readers must examine surrounding code to understand what these
│    variables contain. Meaningful names make code self-documenting.
│ 
│ 🎯 Impact: Medium | 📊 Confidence: 85%
│ 
│ [ Accept ] [ Reject ] [ Learn More ]
└───────────────────────────────────────────────────────────────

📍 Line 23: Security Vulnerability  
┌─ 🛡️ Security Agent ──────────────────────────────────────────
│ 
│ 🚨 CRITICAL: SQL Injection Vulnerability
│ 
│ ❌ Vulnerable Code:
│    query = f"SELECT * FROM users WHERE id = {user_id}"
│    cursor.execute(query)
│ 
│ ✅ Secure Fix:
│    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
│ 
│ ⚔️ Attack Vector:
│    Attacker could inject: user_id = "1; DROP TABLE users; --"
│ 
│ 💥 Potential Impact:
│    - Complete database compromise
│    - Data theft and manipulation
│    - System takeover
│ 
│ 📚 Why Parameterized Queries Work:
│    They separate SQL logic from user data, making injection impossible.
│    The database treats user input as pure data, never as executable code.
│ 
│ 🎯 OWASP: A01:2021 – Injection | 📊 CVSS: 9.8 (Critical)
│ 
│ [ Accept ] [ Reject ] [ Security Tutorial ]
└───────────────────────────────────────────────────────────────

📍 Line 35-50: Performance Optimization Opportunity
┌─ ⚡ Performance Agent ────────────────────────────────────────
│ 
│ ⚠️ Quadratic Time Complexity Detected
│ 
│ ❌ Current Implementation (O(n²)):
│    for user in users:
│        for permission in permissions:
│            if user.role == permission.role:
│                grant_permission(user, permission)
│ 
│ ✅ Optimized Implementation (O(n)):
│    permission_map = {p.role: p for p in permissions}
│    for user in users:
│        if user.role in permission_map:
│            grant_permission(user, permission_map[user.role])
│ 
│ 📊 Performance Impact:
│    - 1,000 users: 1M operations → 2K operations (500x faster)
│    - 10,000 users: 100M operations → 20K operations (5000x faster)
│ 
│ 📚 Algorithm Insight:
│    Nested loops create quadratic complexity. Hash maps provide O(1)
│    lookup time, converting the overall algorithm from O(n²) to O(n).
│ 
│ 🎯 Impact: High | 📊 Scale Threshold: >100 items
│ 
│ [ Accept ] [ Reject ] [ Benchmark ]
└───────────────────────────────────────────────────────────────
```

### 4. Comprehensive Review Summary

```
🎯 Multi-Agent Code Review Summary
═══════════════════════════════════════════════════════════════

📊 Overall Assessment:
├── 🧹 Clean Code: 7 suggestions (2 high, 3 medium, 2 low)
├── 🛡️ Security: 3 vulnerabilities (1 critical, 1 high, 1 medium)  
├── ⚡ Performance: 4 optimizations (1 high, 2 medium, 1 low)
├── 🏗️ Design Patterns: 5 opportunities (3 medium, 2 low)
└── 🧪 Testability: 6 improvements (1 high, 4 medium, 1 low)

🚨 Priority Actions (Fix Immediately):
1. 🛡️ Line 23: SQL Injection vulnerability (CVSS 9.8)
2. 🛡️ Line 8: Hardcoded API key exposure (CVSS 7.5)
3. ⚡ Line 35: O(n²) algorithm causing performance issues

💡 High-Impact Improvements:
1. 🧹 Break down UserManager class (violates SRP)
2. 🏗️ Apply Strategy pattern to payment processing
3. 🧪 Inject dependencies for better testability

📚 Learning Insights:
├── Security: Your code is vulnerable to injection attacks - always use parameterized queries
├── Performance: Nested loops become problematic with >1000 items - consider hash maps
├── Architecture: Large classes with multiple responsibilities are hard to maintain
└── Testing: Hard-coded dependencies make unit testing nearly impossible

⚖️ Methodology Conflicts Detected: 2
├── Clean Code vs Performance (Line 45): Resolved in favor of performance
└── Design Patterns vs Simplicity (Line 78): Recommended gradual introduction

🎯 Recommended Action Plan:
1. Fix critical security vulnerabilities (30 minutes)
2. Implement dependency injection for testability (2 hours)  
3. Optimize performance bottlenecks (1 hour)
4. Refactor large classes following SRP (4 hours)
5. Add comprehensive test coverage (6 hours)

📈 Code Quality Improvement: 73% → 91% (projected)
```

## Agent Coordination Features

### Intelligent Conflict Resolution
When agents provide conflicting advice, the system:
- **Identifies Conflicts**: Automatic detection of contradictory recommendations
- **Context Analysis**: Considers project requirements and constraints
- **Priority Assessment**: Weighs trade-offs based on business impact
- **Educational Explanation**: Teaches why conflicts occur and how to resolve them

### Cross-Agent Learning
- **Pattern Recognition**: Agents learn from each other's findings
- **Holistic Assessment**: Combined insights that no single agent could provide
- **Comprehensive Coverage**: Ensures no aspect of code quality is overlooked

## Integration with SuperClaude Framework

### Wave Mode Compatibility
- **Auto-Activation**: Triggers wave mode for complex multi-file analysis
- **Progressive Enhancement**: Each wave adds deeper analysis layers
- **Compound Intelligence**: Agents collaborate across wave boundaries

### Persona Orchestration  
- **Dynamic Activation**: Automatically activates relevant personas based on findings
- **Educational Focus**: Mentor persona enhances learning explanations
- **Expertise Synthesis**: Combines multiple expert perspectives

### MCP Server Coordination
- **Context7**: Official documentation for all methodologies
- **Sequential**: Systematic analysis coordination across agents
- **Magic**: UI components for interactive review interface
- **Playwright**: End-to-end testing validation for suggested changes

## Educational Learning Outcomes

### Code Quality Mastery
- **Clean Code Principles**: Practical application of readability and maintainability
- **Security Awareness**: Understanding of common vulnerabilities and prevention
- **Performance Engineering**: Algorithmic thinking and optimization strategies
- **Design Patterns**: Architectural patterns and when to apply them
- **Testing Excellence**: TDD practices and testability design

### Professional Development
- **Code Review Skills**: Learn to provide constructive, educational feedback
- **Trade-off Analysis**: Understanding when to prioritize different quality aspects
- **Collaborative Development**: Working with multiple perspectives and resolving conflicts
- **Continuous Learning**: Staying updated with best practices across domains

## Output Formats

### Interactive Mode (Default)
- Git diff-style interface with accept/reject options
- Educational tooltips and explanations
- Conflict resolution workflow
- Progressive disclosure of details

### Report Mode
- Comprehensive written analysis
- Prioritized action items
- Learning summaries and insights
- Printable/shareable format

### JSON Mode
- Structured data for tool integration
- API compatibility for automated workflows
- Metrics and scoring for dashboards
- CI/CD pipeline integration

## Quality Assurance

### Agent Validation
- **Consistency Checks**: Ensure recommendations align with stated principles
- **Educational Quality**: Verify explanations are clear and accurate
- **Practical Relevance**: Confirm suggestions are actionable and valuable
- **Conflict Detection**: Identify and resolve contradictory advice

### Continuous Improvement
- **Feedback Loop**: Learn from user acceptance/rejection patterns
- **Methodology Updates**: Stay current with evolving best practices
- **Agent Specialization**: Refine expertise areas based on effectiveness
- **Educational Enhancement**: Improve explanations based on user understanding

## Related Commands
- `/sc:clean_code` - Individual Clean Code analysis
- `/sc:security_review` - Individual security analysis
- `/sc:performance_review` - Individual performance analysis
- `/sc:design_patterns` - Individual design pattern analysis
- `/sc:testability` - Individual testability analysis
- `/sc:improve --comprehensive` - Apply all accepted suggestions
- `/sc:learn --code-quality` - Extended educational content on code quality principles