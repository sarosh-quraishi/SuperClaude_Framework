#!/usr/bin/env python3
"""
Clean Code Agent - Robert C. Martin's Clean Code Principles
Focuses on meaningful names, small functions, single responsibility, and readability
"""

from typing import List, Optional
import re
from .base_agent import BaseAgent, CodeSuggestion, SeverityLevel
import uuid


class CleanCodeAgent(BaseAgent):
    """Agent specialized in Clean Code principles by Robert C. Martin"""
    
    def get_name(self) -> str:
        return "Clean Code Agent"
    
    def get_description(self) -> str:
        return "Applies Robert C. Martin's Clean Code principles focusing on meaningful names, small functions, single responsibility, and code readability"
    
    def get_system_prompt(self) -> str:
        return """You are a Clean Code expert based on Robert C. Martin's principles from "Clean Code: A Handbook of Agile Software Craftsmanship".

        Your core focus areas:
        1. **Meaningful Names**: Variables, functions, and classes should have intention-revealing names
        2. **Small Functions**: Functions should be small and do one thing well
        3. **Single Responsibility**: Each class/function should have one reason to change
        4. **DRY Principle**: Don't repeat yourself - eliminate code duplication
        5. **Comments**: Code should be self-documenting, comments should explain WHY not WHAT
        6. **Error Handling**: Proper exception handling, no ignored errors
        7. **Code Structure**: Clear organization, proper formatting, logical flow
        8. **Function Arguments**: Minimize function parameters, avoid flag arguments

        Provide educational explanations that teach WHY each principle matters for maintainability, readability, and team collaboration."""
    
    def get_specializations(self) -> List[str]:
        return [
            "meaningful_names",
            "function_size", 
            "single_responsibility",
            "dry_principle",
            "comments",
            "error_handling",
            "code_structure",
            "function_parameters"
        ]
    
    def get_analysis_prompt(self, code: str, language: str, file_path: Optional[str] = None) -> str:
        file_context = f"File: {file_path}\n" if file_path else ""
        
        return f"""Analyze this {language} code using Clean Code principles:

{file_context}
```{language}
{code}
```

Focus on these Clean Code principles:
1. **Meaningful Names**: Are variables, functions, classes named clearly?
2. **Function Size**: Are functions small and focused on one task?
3. **Single Responsibility**: Does each function/class have one clear purpose?
4. **DRY Principle**: Is there any code duplication to eliminate?
5. **Comments**: Are there unnecessary comments or missing explanations?
6. **Error Handling**: Are errors handled properly without being ignored?
7. **Structure**: Is the code well-organized and formatted?
8. **Parameters**: Do functions have too many parameters or confusing signatures?

{self.get_json_response_format()}

Prioritize suggestions that will have the biggest impact on code maintainability and team productivity."""
    
    def _should_analyze_line(self, line: str) -> bool:
        """Check if line contains patterns that Clean Code principles address"""
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('//'):
            return False
            
        # Look for Clean Code anti-patterns
        patterns = [
            r'def .{20,}',  # Long function names
            r'def .*\(.*,.*,.*,.*,.*\)',  # Many parameters
            r'[a-z][0-9]+',  # Variables with numbers
            r'[a-z]{1,2}[^a-z]',  # Single/double letter variables
            r'temp|tmp|data|info|obj',  # Generic names
            r'#.*TODO|#.*FIXME|#.*HACK',  # Code smell comments
        ]
        
        return any(re.search(pattern, line, re.IGNORECASE) for pattern in patterns)
    
    def _create_mock_suggestion(self, line: str, line_number: int, language: str) -> Optional[CodeSuggestion]:
        """Create Clean Code suggestions based on line analysis"""
        line = line.strip()
        
        # Check for long function names
        if re.search(r'def .{20,}', line):
            return CodeSuggestion(
                id=str(uuid.uuid4()),
                agent_name=self.name,
                principle="Meaningful Names - Function Length",
                line_number=line_number,
                original_code=line,
                suggested_code=None,
                reasoning="Function name is very long, which may indicate it's doing too much",
                educational_explanation="Clean Code principle: Function names should be concise yet descriptive. Long names often indicate the function has multiple responsibilities. Consider breaking it into smaller, single-purpose functions.",
                impact_score=6.0,
                confidence=0.8,
                severity=SeverityLevel.MEDIUM,
                category="naming"
            )
        
        # Check for too many parameters
        if re.search(r'def .*\(.*,.*,.*,.*,.*\)', line):
            return CodeSuggestion(
                id=str(uuid.uuid4()),
                agent_name=self.name,
                principle="Function Parameters",
                line_number=line_number,
                original_code=line,
                suggested_code=None,
                reasoning="Function has too many parameters (5+), making it hard to understand and test",
                educational_explanation="Clean Code principle: Functions should have 3 or fewer parameters. Many parameters indicate the function is doing too much. Consider grouping related parameters into objects or breaking the function apart.",
                impact_score=7.0,
                confidence=0.9,
                severity=SeverityLevel.HIGH,
                category="structure"
            )
        
        # Check for generic variable names
        if re.search(r'\b(temp|tmp|data|info|obj|item)\b', line, re.IGNORECASE):
            return CodeSuggestion(
                id=str(uuid.uuid4()),
                agent_name=self.name,
                principle="Meaningful Names - Avoid Generic Names",
                line_number=line_number,
                original_code=line,
                suggested_code=None,
                reasoning="Generic variable names like 'temp', 'data', 'info' don't reveal intention",
                educational_explanation="Clean Code principle: Names should reveal intention. Generic names force readers to understand context from surrounding code. Use descriptive names that explain what the variable contains or represents.",
                impact_score=5.0,
                confidence=0.7,
                severity=SeverityLevel.MEDIUM,
                category="naming"
            )
        
        # Check for single letter variables (except common loop counters)
        if re.search(r'\b[a-z]\b(?!\s*[=:])', line) and not re.search(r'\b[ijk]\s*=', line):
            return CodeSuggestion(
                id=str(uuid.uuid4()),
                agent_name=self.name,
                principle="Meaningful Names - Single Letter Variables",
                line_number=line_number,
                original_code=line,
                suggested_code=None,
                reasoning="Single letter variable names don't convey meaning",
                educational_explanation="Clean Code principle: Variable names should be searchable and meaningful. Single letters are only acceptable for short loop counters. Use descriptive names that explain the variable's purpose.",
                impact_score=4.0,
                confidence=0.6,
                severity=SeverityLevel.LOW,
                category="naming"
            )
        
        # Check for TODO/FIXME comments
        if re.search(r'#.*(TODO|FIXME|HACK)', line, re.IGNORECASE):
            return CodeSuggestion(
                id=str(uuid.uuid4()),
                agent_name=self.name,
                principle="Code Debt Comments",
                line_number=line_number,
                original_code=line,
                suggested_code=None,
                reasoning="TODO/FIXME comments indicate incomplete or problematic code",
                educational_explanation="Clean Code principle: Code should be production-ready. TODO comments accumulate as technical debt. Either implement the TODO immediately, create a proper ticket/issue, or remove the comment if it's no longer relevant.",
                impact_score=6.0,
                confidence=0.8,
                severity=SeverityLevel.MEDIUM,
                category="structure"
            )
        
        return None


class CleanCodePrinciples:
    """Reference class containing Clean Code principles and examples"""
    
    PRINCIPLES = {
        "meaningful_names": {
            "description": "Use intention-revealing names",
            "examples": {
                "bad": "d = 5  # elapsed time in days",
                "good": "elapsed_time_in_days = 5"
            },
            "rationale": "Code is read far more often than it's written. Clear names eliminate the need for comments and mental mapping."
        },
        
        "small_functions": {
            "description": "Functions should be small and do one thing",
            "examples": {
                "bad": "def process_user_data_and_send_email(user):",
                "good": "def process_user_data(user):\ndef send_welcome_email(user):"
            },
            "rationale": "Small functions are easier to understand, test, and reuse. They follow the Single Responsibility Principle."
        },
        
        "function_parameters": {
            "description": "Minimize function parameters (ideally ≤3)",
            "examples": {
                "bad": "def create_user(name, email, age, address, phone, role, department):",
                "good": "def create_user(user_profile: UserProfile):"
            },
            "rationale": "Many parameters make functions harder to understand and test. Consider parameter objects or builder patterns."
        },
        
        "comments": {
            "description": "Express intent in code, not comments",
            "examples": {
                "bad": "# Check if employee is eligible for full benefits\nif employee.type == 'FULL_TIME' and employee.age >= 65:",
                "good": "if employee.is_eligible_for_full_benefits():"
            },
            "rationale": "Good code is self-documenting. Comments should explain WHY, not WHAT. They often become outdated and misleading."
        },
        
        "error_handling": {
            "description": "Handle errors gracefully, don't ignore them",
            "examples": {
                "bad": "try:\n    risky_operation()\nexcept:\n    pass",
                "good": "try:\n    risky_operation()\nexcept SpecificException as e:\n    logger.error(f'Operation failed: {e}')\n    raise"
            },
            "rationale": "Silent failures hide bugs and make debugging nearly impossible. Always handle errors explicitly."
        }
    }
    
    @classmethod
    def get_principle_explanation(cls, principle_name: str) -> str:
        """Get detailed explanation for a Clean Code principle"""
        principle = cls.PRINCIPLES.get(principle_name, {})
        if not principle:
            return f"Unknown principle: {principle_name}"
        
        return f"""
**{principle['description']}**

**Bad Example:**
```
{principle['examples']['bad']}
```

**Good Example:**
```
{principle['examples']['good']}
```

**Why This Matters:**
{principle['rationale']}
"""