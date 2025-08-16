#!/usr/bin/env python3
"""
Testability Agent - TDD and Testing Best Practices
Focuses on improving code testability and identifying testing opportunities
"""

from typing import List, Optional
import re
from .base_agent import BaseAgent, CodeSuggestion, SeverityLevel
import uuid


class TestabilityAgent(BaseAgent):
    """Agent specialized in testability and testing best practices"""
    
    def get_name(self) -> str:
        return "Testability Agent"
    
    def get_description(self) -> str:
        return "Identifies opportunities to improve code testability and recommends testing best practices including TDD, mocking, and test design"
    
    def get_system_prompt(self) -> str:
        return """You are a testing expert focused on Test-Driven Development (TDD) and code testability.

        **Testing Principles & Practices:**
        1. **Test-Driven Development (TDD)**: Red-Green-Refactor cycle for better design
        2. **Unit Test Design**: Arrange-Act-Assert pattern, single responsibility per test
        3. **Test Isolation**: Tests should be independent and not affect each other
        4. **Mocking & Stubbing**: Isolating units under test from dependencies
        5. **Test Coverage**: Meaningful coverage of critical paths and edge cases
        6. **Integration Testing**: Testing component interactions and data flow
        7. **Test Maintainability**: Clear, readable tests that serve as documentation

        **Testability Factors:**
        - **Dependency Injection**: Making dependencies explicit and replaceable
        - **Pure Functions**: Functions without side effects are easier to test
        - **Small Functions**: Focused functions are easier to test thoroughly
        - **Avoid Global State**: Global variables make tests interdependent
        - **Error Handling**: Testable error conditions and recovery paths
        - **Time & Randomness**: Making time and random values controllable in tests

        **Test Types & Strategies:**
        - **Unit Tests**: Fast, isolated tests of individual components
        - **Integration Tests**: Testing component interactions
        - **Property-Based Testing**: Testing with generated inputs to find edge cases
        - **Mutation Testing**: Validating test quality by introducing bugs
        - **Performance Tests**: Ensuring code meets performance requirements

        **Anti-Patterns to Identify:**
        - Hard-to-test code (tightly coupled, many dependencies)
        - Tests that are too complex or test multiple things
        - Missing test coverage for error conditions
        - Tests that depend on external systems or timing
        - Fragile tests that break with unrelated changes

        Provide educational explanations about WHY testability matters, HOW to make code more testable, and WHEN different testing strategies are appropriate."""
    
    def get_specializations(self) -> List[str]:
        return [
            "test_driven_development",
            "dependency_injection",
            "test_isolation",
            "mocking_strategies", 
            "test_coverage",
            "pure_functions",
            "error_testing",
            "integration_testing",
            "test_maintainability",
            "performance_testing"
        ]
    
    def get_analysis_prompt(self, code: str, language: str, file_path: Optional[str] = None) -> str:
        file_context = f"File: {file_path}\n" if file_path else ""
        
        return f"""Analyze this {language} code for testability issues and testing opportunities:

{file_context}
```{language}
{code}
```

Focus on these testability aspects:

**Critical Testability Issues:**
1. **Hard Dependencies**: Hard-coded dependencies that prevent mocking/substitution
2. **Global State**: Global variables that make tests interdependent
3. **Side Effects**: Functions that modify state making them hard to test in isolation
4. **External Dependencies**: Direct calls to databases, APIs, file systems without abstraction

**Testing Design Issues:**
5. **Large Functions**: Functions doing too much, making comprehensive testing difficult
6. **Complex Conditionals**: Nested if/else logic requiring many test cases
7. **Error Handling**: Missing or untestable error conditions
8. **Time Dependencies**: Code that depends on current time or dates

**Missing Test Opportunities:**
9. **Edge Cases**: Boundary conditions, empty inputs, invalid data
10. **Error Scenarios**: Exception handling, failure modes, recovery paths
11. **Integration Points**: Where components interact or communicate
12. **Performance Scenarios**: Load testing, timeout handling, resource limits

**Test Quality Issues:**
13. **Test Coverage Gaps**: Important code paths without test coverage
14. **Fragile Tests**: Tests that break due to unrelated changes
15. **Complex Test Setup**: Tests requiring extensive mocking or setup

{self.get_json_response_format()}

For each testability suggestion:
- Explain how to make the code more testable
- Suggest specific testing strategies and tools
- Provide concrete test examples where helpful
- Explain the testing principle being applied
- Consider the balance between test complexity and value"""
    
    def _should_analyze_line(self, line: str) -> bool:
        """Check if line contains testability concerns"""
        line = line.strip().lower()
        if not line or line.startswith('#') or line.startswith('//'):
            return False
            
        # Look for testability-related patterns
        testability_patterns = [
            r'def\s+\w+\(',  # Function definitions
            r'class\s+\w+',  # Class definitions
            r'import.*|from.*import',  # Dependencies
            r'global|nonlocal',  # Global state
            r'time\.|datetime\.|random\.',  # Time/randomness dependencies
            r'open\(|file|read|write',  # File operations
            r'print\(|logging\.|logger\.',  # Output operations
            r'input\(|raw_input\(',  # Input operations
            r'requests\.|urllib|http',  # Network operations
            r'database|cursor|query|sql',  # Database operations
            r'if.*and.*or|if.*or.*and',  # Complex conditionals
            r'try:|except:|raise',  # Error handling
            r'=.*\(\)',  # Object instantiation
            r'while|for.*in',  # Loops that might need testing
        ]
        
        return any(re.search(pattern, line, re.IGNORECASE) for pattern in testability_patterns)
    
    def _create_mock_suggestion(self, line: str, line_number: int, language: str) -> Optional[CodeSuggestion]:
        """Create testability suggestions based on line analysis"""
        line_lower = line.strip().lower()
        
        # Check for hard-coded dependencies
        if re.search(r'=\s*\w+\(.*\)', line) and not re.search(r'(print|len|str|int|float|bool|list|dict|set)', line):
            return CodeSuggestion(
                id=str(uuid.uuid4()),
                agent_name=self.name,
                principle="Dependency Injection for Testability",
                line_number=line_number,
                original_code=line,
                suggested_code="# Inject dependencies to enable mocking\ndef __init__(self, database_service: DatabaseService = None):\n    self.database = database_service or ProductionDatabaseService()",
                reasoning="Hard-coded object instantiation makes it impossible to substitute mock objects during testing",
                educational_explanation="Testability principle: Hard-coded dependencies create tight coupling that prevents you from substituting test doubles (mocks, stubs, fakes) during testing. This means you can't isolate the unit under test from its dependencies, making tests slow, fragile, and dependent on external systems. Use dependency injection to make dependencies explicit and replaceable. This enables fast, isolated unit tests that can run without databases, APIs, or file systems.",
                impact_score=7.0,
                confidence=0.8,
                severity=SeverityLevel.HIGH,
                category="dependency_injection"
            )
        
        # Check for time dependencies
        if re.search(r'time\.|datetime\.now|datetime\.today', line):
            return CodeSuggestion(
                id=str(uuid.uuid4()),
                agent_name=self.name,
                principle="Testable Time Dependencies",
                line_number=line_number,
                original_code=line,
                suggested_code="# Make time injectable for testing\ndef process_data(self, current_time=None):\n    current_time = current_time or datetime.now()",
                reasoning="Direct time dependencies make tests non-deterministic and time-dependent",
                educational_explanation="Testing principle: Code that depends on the current time is hard to test because time constantly changes. Tests become non-deterministic - they might pass at one time and fail at another. You can't easily test time-based logic like expiration, scheduling, or time zones. Make time injectable as a parameter with a sensible default, or use a time service that can be mocked. This allows you to control time in tests and verify time-based behavior reliably.",
                impact_score=6.0,
                confidence=0.9,
                severity=SeverityLevel.MEDIUM,
                category="pure_functions"
            )
        
        # Check for global state usage
        if re.search(r'global\s+\w+', line):
            return CodeSuggestion(
                id=str(uuid.uuid4()),
                agent_name=self.name,
                principle="Avoid Global State for Test Isolation",
                line_number=line_number,
                original_code=line,
                suggested_code="# Pass state as parameters or use dependency injection\ndef process_data(self, config_manager: ConfigManager):",
                reasoning="Global variables create hidden dependencies between tests and make test isolation impossible",
                educational_explanation="Testing principle: Global state is the enemy of test isolation. When functions modify global variables, tests can affect each other in unpredictable ways. The order of test execution matters, tests can't run in parallel, and test failures cascade. Global state also creates hidden dependencies that make it hard to understand what a function actually needs to work. Replace global variables with explicit parameters or dependency injection to achieve test isolation.",
                impact_score=8.0,
                confidence=0.9,
                severity=SeverityLevel.HIGH,
                category="test_isolation"
            )
        
        # Check for complex functions that are hard to test
        if re.search(r'def\s+\w+\(.*\):', line) and self._likely_complex_function(line):
            return CodeSuggestion(
                id=str(uuid.uuid4()),
                agent_name=self.name,
                principle="Break Down Complex Functions",
                line_number=line_number,
                original_code=line,
                suggested_code="# Break into smaller, focused functions\ndef validate_input(data): pass\ndef process_data(data): pass\ndef save_result(result): pass",
                reasoning="Large, complex functions are difficult to test comprehensively and understand",
                educational_explanation="Testing principle: Large functions with multiple responsibilities are hard to test because you need many test cases to cover all paths, and it's unclear what each test is actually verifying. They violate the Single Responsibility Principle and often mix business logic with infrastructure concerns. Break large functions into smaller, focused functions that each do one thing well. This makes each function easier to test, understand, and reuse.",
                impact_score=6.5,
                confidence=0.7,
                severity=SeverityLevel.MEDIUM,
                category="test_coverage"
            )
        
        # Check for file operations without abstraction
        if re.search(r'open\(|file.*=|\.read\(\)|\.write\(', line):
            return CodeSuggestion(
                id=str(uuid.uuid4()),
                agent_name=self.name,
                principle="Abstract File Operations for Testing",
                line_number=line_number,
                original_code=line,
                suggested_code="# Use file service abstraction\ndef __init__(self, file_service: FileService):\n    self.file_service = file_service",
                reasoning="Direct file operations make tests dependent on the file system and harder to isolate",
                educational_explanation="Testing principle: Direct file operations create external dependencies that make tests slow, fragile, and environment-dependent. Tests might fail if files don't exist, have wrong permissions, or if the file system is read-only. They can't run in parallel safely and leave test artifacts. Abstract file operations behind an interface that can be mocked or use in-memory implementations for testing. This makes tests fast, reliable, and independent of the file system.",
                impact_score=6.0,
                confidence=0.8,
                severity=SeverityLevel.MEDIUM,
                category="mocking_strategies"
            )
        
        # Check for network operations
        if re.search(r'requests\.|urllib|http|api', line, re.IGNORECASE):
            return CodeSuggestion(
                id=str(uuid.uuid4()),
                agent_name=self.name,
                principle="Mock External Services",
                line_number=line_number,
                original_code=line,
                suggested_code="# Inject HTTP client for easy mocking\ndef __init__(self, http_client: HttpClient):\n    self.http_client = http_client",
                reasoning="Direct network calls make tests slow, unreliable, and dependent on external services",
                educational_explanation="Testing principle: Tests that make real network calls are slow (seconds vs. milliseconds), unreliable (network issues, service downtime), and can accidentally modify production data. They can't test error conditions like timeouts or API failures reliably. Abstract network operations behind an interface and inject the HTTP client. Use mock HTTP clients in tests to simulate responses, errors, and edge cases. This enables fast, reliable tests that can verify your error handling logic.",
                impact_score=7.5,
                confidence=0.9,
                severity=SeverityLevel.HIGH,
                category="mocking_strategies"
            )
        
        # Check for complex conditionals that need thorough testing
        if re.search(r'if.*and.*or|if.*or.*and', line):
            return CodeSuggestion(
                id=str(uuid.uuid4()),
                agent_name=self.name,
                principle="Comprehensive Testing of Complex Logic",
                line_number=line_number,
                original_code=line,
                suggested_code="# Consider simplifying or ensure comprehensive test coverage\n# Test all combinations: (A and B) or (C and D)",
                reasoning="Complex boolean expressions require many test cases to ensure all logical paths are covered",
                educational_explanation="Testing principle: Complex boolean expressions with multiple AND/OR operators create many logical paths that need testing. For 'if (A and B) or (C and D)', you need tests for when each combination is true/false. Missing test cases can hide bugs in the logic. Consider simplifying the condition into a well-named function, or ensure you have comprehensive test coverage with a truth table approach to verify all logical combinations work correctly.",
                impact_score=5.0,
                confidence=0.8,
                severity=SeverityLevel.MEDIUM,
                category="test_coverage"
            )
        
        return None
    
    def _likely_complex_function(self, line: str) -> bool:
        """Heuristic to determine if this might be a complex function"""
        # Look for signs of complexity in function definition
        return (len(line) > 50 or  # Long function signature
                line.count(',') > 3 or  # Many parameters
                'manager' in line.lower() or 
                'processor' in line.lower() or
                'handler' in line.lower())


class TestabilityPrinciples:
    """Reference class containing testability principles and examples"""
    
    TESTABILITY_PRINCIPLES = {
        "dependency_injection": {
            "principle": "Make dependencies explicit and injectable",
            "benefits": [
                "Enables mocking and stubbing",
                "Makes dependencies visible",
                "Allows easy substitution",
                "Improves test isolation"
            ],
            "example": {
                "hard_to_test": """
class UserService:
    def __init__(self):
        self.database = PostgreSQLDatabase()  # Hard-coded dependency
        self.email_service = SMTPEmailService()  # Hard-coded dependency
    
    def create_user(self, user_data):
        user = self.database.save(user_data)
        self.email_service.send_welcome_email(user)
        return user
""",
                "testable": """
class UserService:
    def __init__(self, database: Database, email_service: EmailService):
        self.database = database
        self.email_service = email_service
    
    def create_user(self, user_data):
        user = self.database.save(user_data)
        self.email_service.send_welcome_email(user)
        return user

# In tests:
def test_create_user():
    mock_db = Mock(spec=Database)
    mock_email = Mock(spec=EmailService)
    service = UserService(mock_db, mock_email)
    # Test with full control over dependencies
"""
            }
        },
        
        "pure_functions": {
            "principle": "Prefer pure functions (no side effects)",
            "benefits": [
                "Predictable output for given input",
                "Easy to test with simple assertions",
                "No setup or teardown required",
                "Can test with property-based testing"
            ],
            "example": {
                "impure": """
class Calculator:
    def __init__(self):
        self.history = []
    
    def add(self, a, b):
        result = a + b
        self.history.append(f'{a} + {b} = {result}')  # Side effect
        print(f'Result: {result}')  # Side effect
        return result
""",
                "pure": """
class Calculator:
    def add(self, a, b):
        return a + b  # Pure function
    
    def add_with_history(self, a, b, history):
        result = a + b
        new_history = history + [f'{a} + {b} = {result}']
        return result, new_history

# Easy to test:
def test_add():
    calc = Calculator()
    assert calc.add(2, 3) == 5
    assert calc.add(-1, 1) == 0
"""
            }
        },
        
        "test_isolation": {
            "principle": "Tests should be independent and not affect each other",
            "benefits": [
                "Tests can run in any order",
                "Parallel test execution possible",
                "Failed tests don't cascade",
                "Clear test responsibilities"
            ],
            "example": {
                "coupled_tests": """
# Bad: Tests depend on each other
counter = 0

def test_increment():
    global counter
    counter += 1
    assert counter == 1

def test_increment_twice():
    global counter  # Depends on previous test!
    counter += 1
    assert counter == 2  # Fails if tests run out of order
""",
                "isolated_tests": """
# Good: Each test is independent
class TestCounter:
    def test_increment(self):
        counter = Counter(initial_value=0)
        counter.increment()
        assert counter.value == 1
    
    def test_increment_twice(self):
        counter = Counter(initial_value=0)
        counter.increment()
        counter.increment()
        assert counter.value == 2
"""
            }
        }
    }
    
    TEST_STRATEGIES = {
        "unit_testing": {
            "when_to_use": "Testing individual components in isolation",
            "characteristics": ["Fast execution", "Isolated dependencies", "Single responsibility"],
            "example": """
def test_password_validator():
    validator = PasswordValidator()
    
    # Test valid password
    assert validator.is_valid('SecurePass123!') == True
    
    # Test edge cases
    assert validator.is_valid('') == False
    assert validator.is_valid('weak') == False
    assert validator.is_valid('NoSpecialChar123') == False
"""
        },
        
        "integration_testing": {
            "when_to_use": "Testing component interactions and data flow",
            "characteristics": ["Real dependencies", "End-to-end workflows", "Interface validation"],
            "example": """
def test_user_registration_flow():
    # Integration test with real database
    database = TestDatabase()
    email_service = MockEmailService()
    user_service = UserService(database, email_service)
    
    user_data = {'email': 'test@example.com', 'password': 'SecurePass123!'}
    user = user_service.create_user(user_data)
    
    # Verify user saved to database
    saved_user = database.get_user_by_email('test@example.com')
    assert saved_user is not None
    
    # Verify email was sent
    assert email_service.emails_sent == 1
"""
        },
        
        "property_based_testing": {
            "when_to_use": "Finding edge cases and testing invariants",
            "characteristics": ["Generated test inputs", "Property verification", "Edge case discovery"],
            "example": """
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def test_sorting_properties(numbers):
    sorted_numbers = sort_function(numbers)
    
    # Properties that should always hold
    assert len(sorted_numbers) == len(numbers)
    assert all(a <= b for a, b in zip(sorted_numbers, sorted_numbers[1:]))
    assert set(sorted_numbers) == set(numbers)
"""
        }
    }
    
    @classmethod
    def get_principle_info(cls, principle: str) -> str:
        """Get detailed information about a testability principle"""
        info = cls.TESTABILITY_PRINCIPLES.get(principle, {})
        if not info:
            return f"Unknown testability principle: {principle}"
        
        benefits = chr(10).join(f'- {benefit}' for benefit in info['benefits'])
        
        return f"""
**{info['principle']}**

**Benefits:**
{benefits}

**Example:**

*Hard to Test:*
```python
{info['example']['hard_to_test'] if 'hard_to_test' in info['example'] else info['example']['impure'] if 'impure' in info['example'] else info['example']['coupled_tests']}
```

*Testable Version:*
```python
{info['example']['testable'] if 'testable' in info['example'] else info['example']['pure'] if 'pure' in info['example'] else info['example']['isolated_tests']}
```
"""
    
    @classmethod
    def get_testing_strategy_info(cls, strategy: str) -> str:
        """Get information about a specific testing strategy"""
        info = cls.TEST_STRATEGIES.get(strategy, {})
        if not info:
            return f"Unknown testing strategy: {strategy}"
        
        characteristics = chr(10).join(f'- {char}' for char in info['characteristics'])
        
        return f"""
**{strategy.replace('_', ' ').title()}**

**When to Use:** {info['when_to_use']}

**Characteristics:**
{characteristics}

**Example:**
```python
{info['example']}
```
"""