#!/usr/bin/env python3
"""
Design Patterns Agent - Gang of Four Patterns + SOLID Principles
Focuses on identifying opportunities for design patterns and architectural improvements
"""

from typing import List, Optional
import re
from .base_agent import BaseAgent, CodeSuggestion, SeverityLevel
import uuid


class DesignPatternsAgent(BaseAgent):
    """Agent specialized in design patterns and SOLID principles"""
    
    def get_name(self) -> str:
        return "Design Patterns Agent"
    
    def get_description(self) -> str:
        return "Identifies opportunities for design patterns and architectural improvements based on Gang of Four patterns and SOLID principles"
    
    def get_system_prompt(self) -> str:
        return """You are a software architecture expert specializing in design patterns and SOLID principles.

        **SOLID Principles:**
        1. **Single Responsibility Principle (SRP)**: A class should have only one reason to change
        2. **Open/Closed Principle (OCP)**: Software entities should be open for extension, closed for modification
        3. **Liskov Substitution Principle (LSP)**: Objects should be replaceable with instances of their subtypes
        4. **Interface Segregation Principle (ISP)**: Clients shouldn't depend on interfaces they don't use
        5. **Dependency Inversion Principle (DIP)**: Depend on abstractions, not concretions

        **Key Design Patterns to Identify:**

        **Creational Patterns:**
        - **Factory Method**: Creating objects without specifying exact classes
        - **Abstract Factory**: Families of related objects
        - **Builder**: Complex object construction step by step
        - **Singleton**: Ensuring single instance (use carefully!)
        - **Prototype**: Creating objects by cloning

        **Structural Patterns:**
        - **Adapter**: Making incompatible interfaces work together
        - **Decorator**: Adding behavior to objects dynamically
        - **Facade**: Simplified interface to complex subsystem
        - **Composite**: Tree structures of objects
        - **Proxy**: Placeholder or surrogate for another object

        **Behavioral Patterns:**
        - **Strategy**: Encapsulating algorithms and making them interchangeable
        - **Observer**: Notifying multiple objects about state changes
        - **Command**: Encapsulating requests as objects
        - **State**: Altering object behavior when internal state changes
        - **Template Method**: Defining algorithm skeleton in base class

        **Anti-Patterns to Detect:**
        - God Object (classes doing too much)
        - Tight Coupling (excessive dependencies)
        - Hard-coded Dependencies (no dependency injection)
        - Shotgun Surgery (single change affects many classes)
        - Feature Envy (class using another class's data excessively)

        Provide educational explanations about WHEN to use patterns (not just HOW), the problems they solve, and their trade-offs."""
    
    def get_specializations(self) -> List[str]:
        return [
            "solid_principles",
            "creational_patterns",
            "structural_patterns", 
            "behavioral_patterns",
            "anti_patterns",
            "dependency_injection",
            "composition_over_inheritance",
            "architectural_patterns",
            "code_organization",
            "abstraction_design"
        ]
    
    def get_analysis_prompt(self, code: str, language: str, file_path: Optional[str] = None) -> str:
        file_context = f"File: {file_path}\n" if file_path else ""
        
        return f"""Analyze this {language} code for design pattern opportunities and architectural improvements:

{file_context}
```{language}
{code}
```

Focus on these architectural aspects:

**SOLID Principles Violations:**
1. **Single Responsibility**: Classes/functions doing multiple unrelated things
2. **Open/Closed**: Code that requires modification instead of extension for new features
3. **Liskov Substitution**: Inheritance hierarchies that break substitutability
4. **Interface Segregation**: Large interfaces forcing unnecessary dependencies
5. **Dependency Inversion**: High-level modules depending on low-level details

**Design Pattern Opportunities:**
6. **Creational Patterns**: Complex object creation, hard-coded instantiation
7. **Structural Patterns**: Interface mismatches, complex object relationships
8. **Behavioral Patterns**: Complex conditional logic, tightly coupled communication

**Anti-Patterns to Identify:**
9. **God Object**: Classes with too many responsibilities
10. **Tight Coupling**: Excessive dependencies between components
11. **Hard-coded Dependencies**: Direct instantiation preventing testability
12. **Feature Envy**: Methods using other classes' data more than their own

**Architectural Improvements:**
13. **Dependency Injection**: Opportunities to inject dependencies instead of creating them
14. **Composition over Inheritance**: Complex inheritance that could be simplified
15. **Abstraction Opportunities**: Concrete implementations that should be abstracted

{self.get_json_response_format()}

For each pattern suggestion:
- Explain the specific problem being solved
- Describe how the pattern addresses it
- Provide concrete implementation guidance
- Discuss when NOT to use the pattern (over-engineering warnings)
- Consider the trade-offs (complexity vs. flexibility)"""
    
    def _should_analyze_line(self, line: str) -> bool:
        """Check if line contains patterns that design patterns could improve"""
        line = line.strip().lower()
        if not line or line.startswith('#') or line.startswith('//'):
            return False
            
        # Look for design pattern opportunities
        design_patterns = [
            r'class.*:',  # Class definitions
            r'def.*\(.*\):',  # Method definitions
            r'if.*isinstance|if.*type\(',  # Type checking
            r'if.*==.*and.*==',  # Complex conditionals
            r'import.*|from.*import',  # Dependencies
            r'\..*\..*\.',  # Chained method calls
            r'global|nonlocal',  # Global state
            r'.*=.*\(\)',  # Object instantiation
            r'raise|except|try',  # Error handling
            r'for.*in.*if',  # Complex iterations
            r'lambda|functools',  # Functional patterns
        ]
        
        return any(re.search(pattern, line, re.IGNORECASE) for pattern in design_patterns)
    
    def _create_mock_suggestion(self, line: str, line_number: int, language: str) -> Optional[CodeSuggestion]:
        """Create design pattern suggestions based on line analysis"""
        line_lower = line.strip().lower()
        
        # Check for God Object pattern (large class definitions)
        if re.search(r'class\s+\w+.*:', line) and self._likely_large_class_context(line):
            return CodeSuggestion(
                id=str(uuid.uuid4()),
                agent_name=self.name,
                principle="Single Responsibility Principle (SRP)",
                line_number=line_number,
                original_code=line,
                suggested_code="# Break into smaller, focused classes\nclass UserAuthenticator:\nclass UserProfileManager:\nclass UserNotificationService:",
                reasoning="Large classes often violate Single Responsibility Principle by handling multiple concerns",
                educational_explanation="SOLID Principle: The Single Responsibility Principle states that a class should have only one reason to change. Large classes typically handle multiple responsibilities (authentication, data management, notifications, etc.), making them harder to understand, test, and maintain. When you need to change user authentication logic, you shouldn't risk breaking notification code. Split large classes into smaller, focused classes that each handle one specific responsibility.",
                impact_score=7.0,
                confidence=0.75,
                severity=SeverityLevel.HIGH,
                category="solid_principles"
            )
        
        # Check for hard-coded object instantiation
        if re.search(r'=\s*\w+\(.*\)', line) and not re.search(r'(print|len|str|int|float|bool|list|dict|set)', line):
            return CodeSuggestion(
                id=str(uuid.uuid4()),
                agent_name=self.name,
                principle="Dependency Inversion Principle (DIP)",
                line_number=line_number,
                original_code=line,
                suggested_code="# Use dependency injection\ndef __init__(self, database_service: DatabaseService):\n    self.database = database_service",
                reasoning="Hard-coded object instantiation creates tight coupling and makes testing difficult",
                educational_explanation="SOLID Principle: Dependency Inversion suggests depending on abstractions, not concrete implementations. Hard-coding object creation inside classes makes them tightly coupled and difficult to test. Instead, inject dependencies through constructors or parameters. This allows you to easily swap implementations (e.g., test database vs. production database) and makes your code more flexible and testable.",
                impact_score=6.0,
                confidence=0.7,
                severity=SeverityLevel.MEDIUM,
                category="dependency_injection"
            )
        
        # Check for complex conditionals that could use Strategy pattern
        if re.search(r'if.*==.*and.*==|elif.*==.*and', line):
            return CodeSuggestion(
                id=str(uuid.uuid4()),
                agent_name=self.name,
                principle="Strategy Pattern",
                line_number=line_number,
                original_code=line,
                suggested_code="# Use Strategy pattern\nstrategy = payment_strategies[payment_type]\nresult = strategy.process(amount)",
                reasoning="Complex conditional logic can be replaced with Strategy pattern for better extensibility",
                educational_explanation="Design Pattern: Complex if/elif chains based on type or category often indicate a need for the Strategy pattern. Instead of having one large method with many conditionals, create separate strategy classes for each behavior. This follows the Open/Closed principle - you can add new strategies without modifying existing code. It also makes each strategy easier to test and understand in isolation.",
                impact_score=6.5,
                confidence=0.8,
                severity=SeverityLevel.MEDIUM,
                category="behavioral_patterns"
            )
        
        # Check for type checking that could use polymorphism
        if re.search(r'isinstance\(.*\)|type\(.*\)\s*==', line):
            return CodeSuggestion(
                id=str(uuid.uuid4()),
                agent_name=self.name,
                principle="Polymorphism over Type Checking",
                line_number=line_number,
                original_code=line,
                suggested_code="# Use polymorphism instead of type checking\n# Define common interface and let objects handle their own behavior",
                reasoning="Type checking often indicates missing polymorphism - objects should know how to behave",
                educational_explanation="OOP Principle: Type checking with isinstance() or type() often indicates you're missing an opportunity for polymorphism. Instead of checking types and branching, define a common interface (abstract base class or protocol) and let each object implement its own behavior. This follows the Liskov Substitution Principle and makes your code more extensible - adding new types doesn't require modifying existing code.",
                impact_score=6.0,
                confidence=0.85,
                severity=SeverityLevel.MEDIUM,
                category="structural_patterns"
            )
        
        # Check for complex method chaining that could use Builder pattern
        if re.search(r'\..*\..*\.', line) and len(line.split('.')) > 3:
            return CodeSuggestion(
                id=str(uuid.uuid4()),
                agent_name=self.name,
                principle="Builder Pattern",
                line_number=line_number,
                original_code=line,
                suggested_code="# Consider Builder pattern for complex object construction\nbuilder = QueryBuilder()\nquery = builder.select('*').from_table('users').where('active', True).build()",
                reasoning="Long method chains for object construction can be simplified with Builder pattern",
                educational_explanation="Design Pattern: Long method chains, especially for object configuration, can become hard to read and maintain. The Builder pattern provides a fluent interface for constructing complex objects step by step. It's particularly useful when objects have many optional parameters or when construction involves multiple steps. The builder pattern also enforces construction order and can validate the final object before returning it.",
                impact_score=5.0,
                confidence=0.7,
                severity=SeverityLevel.LOW,
                category="creational_patterns"
            )
        
        # Check for global variables that could use Singleton or DI
        if re.search(r'global\s+\w+', line):
            return CodeSuggestion(
                id=str(uuid.uuid4()),
                agent_name=self.name,
                principle="Singleton Pattern or Dependency Injection",
                line_number=line_number,
                original_code=line,
                suggested_code="# Consider Singleton for shared state or DI for better testability\nclass ConfigManager:\n    _instance = None\n    def __new__(cls):\n        if cls._instance is None:\n            cls._instance = super().__new__(cls)\n        return cls._instance",
                reasoning="Global variables create hidden dependencies and make testing difficult",
                educational_explanation="Design Pattern: Global variables create hidden dependencies that make code hard to test and reason about. For shared configuration or state, consider the Singleton pattern to ensure only one instance exists while providing controlled access. However, be cautious - Singletons can be overused. Often, dependency injection is a better solution as it makes dependencies explicit and allows easy substitution for testing.",
                impact_score=7.0,
                confidence=0.8,
                severity=SeverityLevel.HIGH,
                category="creational_patterns"
            )
        
        return None
    
    def _likely_large_class_context(self, line: str) -> bool:
        """Heuristic to determine if this might be a large class"""
        # In a real implementation, this would analyze the full class context
        # For demo purposes, assume it's a large class if it has a complex name
        return len(line) > 30 or 'manager' in line.lower() or 'service' in line.lower()


class DesignPatternsPrinciples:
    """Reference class containing design patterns and SOLID principles"""
    
    SOLID_PRINCIPLES = {
        "srp": {
            "name": "Single Responsibility Principle",
            "description": "A class should have only one reason to change",
            "violation_signs": [
                "Classes with many methods doing unrelated things",
                "Classes that change for multiple reasons",
                "Classes with names containing 'And', 'Manager', 'Utils'"
            ],
            "example": {
                "violation": """
class UserManager:
    def authenticate_user(self, credentials): pass
    def send_email(self, user, message): pass
    def calculate_age(self, birthdate): pass
    def log_activity(self, action): pass
""",
                "solution": """
class UserAuthenticator:
    def authenticate_user(self, credentials): pass

class EmailService:
    def send_email(self, user, message): pass

class AgeCalculator:
    def calculate_age(self, birthdate): pass

class ActivityLogger:
    def log_activity(self, action): pass
"""
            }
        },
        
        "ocp": {
            "name": "Open/Closed Principle",
            "description": "Software entities should be open for extension, closed for modification",
            "violation_signs": [
                "Adding new features requires modifying existing classes",
                "Large if/elif chains based on type",
                "Switch statements that need updates for new cases"
            ],
            "example": {
                "violation": """
class PaymentProcessor:
    def process(self, payment_type, amount):
        if payment_type == 'credit_card':
            # Credit card logic
        elif payment_type == 'paypal':
            # PayPal logic
        # Adding Bitcoin requires modifying this class
""",
                "solution": """
class PaymentProcessor:
    def __init__(self):
        self.strategies = {}
    
    def register_strategy(self, payment_type, strategy):
        self.strategies[payment_type] = strategy
    
    def process(self, payment_type, amount):
        return self.strategies[payment_type].process(amount)

class CreditCardPayment:
    def process(self, amount): pass

class PayPalPayment:
    def process(self, amount): pass
"""
            }
        }
    }
    
    DESIGN_PATTERNS = {
        "strategy": {
            "intent": "Define a family of algorithms, encapsulate each one, and make them interchangeable",
            "when_to_use": [
                "You have multiple ways to perform the same task",
                "You want to switch algorithms at runtime",
                "You have complex conditional logic based on type"
            ],
            "structure": {
                "strategy": "Interface for all concrete strategies",
                "concrete_strategy": "Implements the algorithm",
                "context": "Uses a strategy to perform its work"
            },
            "example": """
from abc import ABC, abstractmethod

class SortStrategy(ABC):
    @abstractmethod
    def sort(self, data): pass

class QuickSort(SortStrategy):
    def sort(self, data):
        # Quick sort implementation
        return sorted(data)

class MergeSort(SortStrategy):
    def sort(self, data):
        # Merge sort implementation
        return sorted(data)

class Sorter:
    def __init__(self, strategy: SortStrategy):
        self.strategy = strategy
    
    def sort_data(self, data):
        return self.strategy.sort(data)
"""
        },
        
        "factory": {
            "intent": "Create objects without specifying their exact classes",
            "when_to_use": [
                "Object creation logic is complex",
                "You need to create different types based on input",
                "You want to centralize object creation"
            ],
            "example": """
class ShapeFactory:
    @staticmethod
    def create_shape(shape_type, **kwargs):
        if shape_type == 'circle':
            return Circle(kwargs['radius'])
        elif shape_type == 'rectangle':
            return Rectangle(kwargs['width'], kwargs['height'])
        else:
            raise ValueError(f'Unknown shape type: {shape_type}')
"""
        },
        
        "observer": {
            "intent": "Define a one-to-many dependency between objects so that when one object changes state, all dependents are notified",
            "when_to_use": [
                "Changes to one object require updating multiple objects",
                "You want loose coupling between subject and observers",
                "You need to notify unknown or dynamic sets of objects"
            ],
            "example": """
class Subject:
    def __init__(self):
        self._observers = []
    
    def attach(self, observer):
        self._observers.append(observer)
    
    def notify(self, message):
        for observer in self._observers:
            observer.update(message)

class Observer:
    def update(self, message):
        print(f'Received: {message}')
"""
        }
    }
    
    @classmethod
    def get_solid_principle_info(cls, principle: str) -> str:
        """Get detailed information about a SOLID principle"""
        info = cls.SOLID_PRINCIPLES.get(principle, {})
        if not info:
            return f"Unknown SOLID principle: {principle}"
        
        return f"""
**{info['name']}**

**Description:** {info['description']}

**Violation Signs:**
{chr(10).join(f'- {sign}' for sign in info['violation_signs'])}

**Example:**

*Violation:*
```python
{info['example']['violation']}
```

*Solution:*
```python
{info['example']['solution']}
```
"""
    
    @classmethod
    def get_pattern_info(cls, pattern: str) -> str:
        """Get detailed information about a design pattern"""
        info = cls.DESIGN_PATTERNS.get(pattern, {})
        if not info:
            return f"Unknown design pattern: {pattern}"
        
        when_to_use = chr(10).join(f'- {use}' for use in info['when_to_use'])
        
        return f"""
**{pattern.title()} Pattern**

**Intent:** {info['intent']}

**When to Use:**
{when_to_use}

**Example:**
```python
{info['example']}
```
"""