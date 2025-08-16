---
allowed-tools: [Read, Grep, Glob, Edit, MultiEdit, Write, TodoWrite]
description: "Analyze code using Clean Code principles by Robert C. Martin"
---

# /clean_code - Clean Code Analysis

## Purpose
Apply Robert C. Martin's Clean Code principles to analyze code for meaningful names, small functions, single responsibility, and readability improvements.

## Usage
```
/clean_code [file_path|code_block] [--format text|json] [--severity all|high|critical] [--examples]
```

## Arguments
- `file_path` - Path to file to analyze (if not provided, analyzes current context)
- `code_block` - Inline code to analyze (wrap in triple backticks)
- `--format` - Output format (text for human-readable, json for structured data)
- `--severity` - Filter suggestions by severity level
- `--examples` - Include before/after code examples in output

## Educational Focus Areas

### Core Clean Code Principles
1. **Meaningful Names** - Variables, functions, and classes should reveal intention
2. **Small Functions** - Functions should be small and do one thing well
3. **Single Responsibility** - Each function/class should have one reason to change
4. **DRY Principle** - Don't repeat yourself, eliminate code duplication
5. **Comments** - Code should be self-documenting, comments explain WHY not WHAT
6. **Error Handling** - Proper exception handling, no ignored errors
7. **Function Parameters** - Minimize parameters, avoid flag arguments
8. **Code Structure** - Clear organization, proper formatting, logical flow

## Execution Process

### 1. Code Analysis
- Load and parse the target code
- Apply Clean Code agent analysis
- Identify violations of Clean Code principles
- Generate educational suggestions with examples

### 2. Educational Output
For each suggestion, provide:
- **Principle Applied**: Which Clean Code rule is being violated
- **Current Issue**: What makes the current code problematic
- **Educational Explanation**: Why this principle matters for maintainability
- **Suggested Improvement**: Concrete example of better approach
- **Impact Assessment**: How this change improves code quality

### 3. Implementation Guidance
- Prioritize suggestions by impact on code maintainability
- Provide specific refactoring steps
- Include code examples showing before/after
- Explain long-term benefits of applying the principle

## Example Output Format

```
🧹 Clean Code Analysis Results

📍 Line 15: Variable Naming Issue
❌ Current: temp_data = process(input)
✅ Suggested: processed_user_profile = process(user_input)

💡 Clean Code Principle: Meaningful Names
📚 Why This Matters: Generic names like 'temp_data' don't reveal intention. 
    Readers must examine surrounding code to understand what the variable contains.
    Meaningful names make code self-documenting and easier to maintain.

🎯 Impact: Medium (Improves code readability and maintainability)
📊 Confidence: 85%

---

📍 Lines 23-45: Function Length Issue
❌ Current: process_user_data_and_send_notification() [23 lines]
✅ Suggested: Break into smaller functions:
    - validate_user_data()
    - save_user_profile()  
    - send_welcome_notification()

💡 Clean Code Principle: Small Functions
📚 Why This Matters: Large functions violate Single Responsibility Principle.
    They're harder to understand, test, and reuse. Small functions with
    descriptive names serve as documentation and are easier to maintain.

🎯 Impact: High (Significantly improves testability and maintainability)
📊 Confidence: 90%
```

## Integration with SuperClaude Framework

### Persona Integration
- Automatically activates **Refactorer** persona for code quality focus
- Educational explanations tailored to teaching clean coding practices
- Integration with **Mentor** persona for learning-focused output

### MCP Server Usage
- **Context7**: Access official Clean Code documentation and examples
- **Sequential**: Systematic analysis of code structure and organization
- Uses Read/Grep tools for comprehensive code examination

### Quality Gates
Applies SuperClaude quality standards:
- ✅ All suggestions include educational explanations
- ✅ Concrete examples provided for improvements
- ✅ Impact assessment for prioritization
- ✅ Respects existing code style and conventions

## Learning Outcomes

After using `/clean_code`, developers will understand:
- How to write intention-revealing names
- When and how to break down large functions
- How to eliminate code duplication effectively
- Why comments should explain intent, not implementation
- How Clean Code principles improve long-term maintainability

## Related Commands
- `/code_review` - Comprehensive multi-agent analysis including Clean Code
- `/improve --quality` - General quality improvements
- `/refactor` - Systematic code restructuring
- `/document` - Generate documentation for cleaned code