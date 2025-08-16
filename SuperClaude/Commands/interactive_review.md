# /sc:interactive_review - Interactive Code Review with Diff-Style Feedback

## Overview
Interactive code review interface with Git-style diff visualization, allowing you to accept, reject, or modify code suggestions with real-time feedback and decision tracking.

## Usage
```bash
/sc:interactive_review [file_path] [options]
```

## Features

### 🔍 Git-Style Diff Visualization
- **Unified Diff Format**: Clear before/after code visualization
- **Syntax Highlighting**: Color-coded additions, deletions, and context
- **Line Numbers**: Accurate line positioning and context
- **Hunk Headers**: Clear indication of change scope

### ⚡ Interactive Decision Making
- **Accept/Reject**: Individual suggestion control
- **Skip**: Defer decisions for later review  
- **Edit**: Modify suggestions before accepting
- **Batch Actions**: Accept/reject all remaining suggestions
- **Learn More**: Detailed educational explanations

### 📊 Decision Tracking
- **Session Recording**: Complete decision history
- **Metrics**: Track acceptance rates and impact
- **Export**: Save sessions for future reference
- **Rollback**: Undo decisions if needed

### 🎯 Review Workflows
- **File-Based**: Review entire files with comprehensive analysis
- **Code-Block**: Review specific code snippets
- **Multi-Agent**: Combined analysis from all specialized agents
- **Single-Agent**: Focus on specific expertise areas

## Interactive Controls

### Primary Actions
- **[a]** Accept suggestion and apply changes
- **[r]** Reject suggestion and keep original code
- **[s]** Skip suggestion for later review
- **[e]** Edit suggestion before accepting
- **[l]** Learn more - detailed educational explanation

### Batch Actions
- **[A]** Accept all remaining suggestions
- **[R]** Reject all remaining suggestions
- **[q]** Quit review session

### Navigation
- **Clear Display**: Each suggestion shown in focused view
- **Progress Tracking**: Current position in review queue
- **Context Preservation**: Maintain file state across decisions

## Display Format

### Suggestion Header
```
================================================================================
🔍 Clean Code Agent | MEDIUM | Line 45
================================================================================

📋 Principle: Meaningful Variable Names
💡 Why: Variable names should clearly express their purpose and intention

📊 Impact: 7/10 | Confidence: 85%
```

### Diff Display
```
@@ -42,3 +42,3 @@ calculateUserScore
 def process_data():
     connection = get_db_connection()
-    d = fetch_user_data(connection)
+    user_data = fetch_user_data(connection)
     return process_results(d)
```

### Educational Context
```
📚 Educational Context:
Clean Code principle: Use intention-revealing names. The variable 'd' doesn't 
tell us what data it contains. 'user_data' immediately communicates its purpose
and makes the code self-documenting.
```

## Examples

### Basic File Review
```bash
/sc:interactive_review src/main.py
```
- Reviews entire file with all agents
- Interactive diff for each suggestion
- Applies accepted changes to generate final version

### Code Block Review
```bash
/sc:interactive_review --code "def calc(x,y): return x+y"
```
- Reviews provided code snippet
- Shows improvements in diff format
- Returns modified code based on decisions

### Single Agent Focus
```bash
/sc:interactive_review src/auth.py --agent security
```
- Security-focused review only
- Specialized security analysis
- Security-specific educational content

### Batch Processing Mode
```bash
/sc:interactive_review src/ --recursive --format json
```
- Process multiple files
- Generate structured review reports
- Track decisions across entire codebase

## Options

### Core Options
- `--agent <name>`: Focus on specific agent (clean_code, security, performance, design_patterns, testability)
- `--format <type>`: Output format (interactive, report, json, diff)
- `--context <lines>`: Number of context lines in diff (default: 3)
- `--no-color`: Disable colored output
- `--auto-accept <severity>`: Auto-accept suggestions below severity threshold

### File Options
- `--recursive`: Process directories recursively
- `--include <patterns>`: File patterns to include
- `--exclude <patterns>`: File patterns to exclude
- `--backup`: Create backup before applying changes

### Session Options
- `--save-session <file>`: Save review session to JSON
- `--load-session <file>`: Resume previous review session
- `--export-diff <file>`: Export final diff to patch file

### Educational Options
- `--explain-all`: Show educational context for all suggestions
- `--learning-mode`: Enhanced educational explanations
- `--principles-only`: Show only principles without code changes

## Integration with SuperClaude

### Auto-Activation
- **Frontend Persona**: Enhanced UI component review
- **Security Persona**: Security-focused vulnerability analysis  
- **Performance Persona**: Optimization-focused review
- **Quality Focus**: Comprehensive code quality assessment

### MCP Integration
- **Context7**: Library best practices and patterns
- **Sequential**: Complex multi-step analysis
- **Magic**: UI component enhancement suggestions

### Flag Integration
- `--think`: Enable detailed analysis mode
- `--validate`: Additional validation checks
- `--uc`: Compressed output for large reviews

## Output Management

### Applied Changes
```bash
# Show final modified code
cat result.py

# Generate patch file
diff -u original.py result.py > changes.patch

# Review session summary
{
  "total_suggestions": 15,
  "accepted": 8,
  "rejected": 4,
  "skipped": 3,
  "modified": 2
}
```

### Session Persistence
- **JSON Export**: Complete session data and decisions
- **Patch Files**: Git-compatible diff files
- **Summary Reports**: High-level review metrics
- **Learning Logs**: Educational insights captured

## Educational Value

### Learning Integration
- **Principle Explanations**: Why each suggestion matters
- **Best Practice Context**: Industry standard practices
- **Impact Analysis**: Real-world consequences of code quality
- **Progressive Learning**: Build understanding over time

### Code Quality Metrics
- **Before/After Comparison**: Measurable improvements
- **Quality Scores**: Objective assessment criteria
- **Technical Debt Tracking**: Long-term maintainability impact
- **Team Standards**: Consistent code quality across projects

## Performance Characteristics

### Efficiency
- **Interactive Response**: Sub-100ms decision processing
- **Memory Usage**: Efficient handling of large files
- **Terminal Optimization**: Smooth display updates
- **Batch Processing**: Scalable for large codebases

### Scalability
- **File Size**: Handles files up to 10K lines efficiently
- **Suggestion Volume**: Manages 100+ suggestions per session
- **Session Persistence**: Reliable state management
- **Cross-Platform**: Works on Linux, macOS, and Windows

## Best Practices

### Review Strategy
1. **Start Small**: Begin with single files or focused agents
2. **Learn First**: Use 'l' to understand principles before deciding
3. **Edit When Needed**: Customize suggestions to fit your context
4. **Track Progress**: Save sessions for complex reviews
5. **Batch Wisely**: Use A/R for clear-cut decisions only

### Quality Improvement
- **Critical First**: Address security and performance issues immediately
- **Educational Focus**: Take time to understand underlying principles
- **Team Alignment**: Share sessions to establish team standards
- **Iterative Improvement**: Regular reviews build better coding habits

### Session Management
- **Save Progress**: Use session files for complex reviews
- **Export Results**: Generate patches for version control
- **Track Metrics**: Monitor improvement over time
- **Share Learning**: Use educational exports for team training

---

**Note**: This command requires terminal support for interactive input and color display. Use `--no-color` flag in environments with limited terminal capabilities.