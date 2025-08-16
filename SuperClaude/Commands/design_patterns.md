---
allowed-tools: [Read, Grep, Glob, Edit, MultiEdit, Write, TodoWrite]
description: "Analyze code for design pattern opportunities and SOLID principle violations"
---

# /design_patterns - Design Patterns & SOLID Principles Analysis

## Purpose
Identify opportunities for design patterns and architectural improvements based on Gang of Four patterns and SOLID principles to improve code structure and maintainability.

## Usage
```
/design_patterns [file_path|code_block] [--focus solid|creational|structural|behavioral] [--patterns] [--refactor]
```

## Arguments
- `file_path` - Path to file to analyze for design pattern opportunities
- `code_block` - Inline code to analyze (wrap in triple backticks)
- `--focus` - Focus on specific pattern category or SOLID principles
- `--patterns` - Include design pattern catalog explanations
- `--refactor` - Provide step-by-step refactoring guidance

## Architectural Analysis Framework

### SOLID Principles Assessment
1. **Single Responsibility Principle (SRP)** - One reason to change per class
2. **Open/Closed Principle (OCP)** - Open for extension, closed for modification
3. **Liskov Substitution Principle (LSP)** - Subtypes must be substitutable
4. **Interface Segregation Principle (ISP)** - Clients shouldn't depend on unused interfaces
5. **Dependency Inversion Principle (DIP)** - Depend on abstractions, not concretions

### Design Pattern Categories
**Creational Patterns** - Object creation mechanisms
- Factory Method, Abstract Factory, Builder, Singleton, Prototype

**Structural Patterns** - Object composition and relationships
- Adapter, Decorator, Facade, Composite, Proxy, Bridge

**Behavioral Patterns** - Communication and responsibility distribution
- Strategy, Observer, Command, State, Template Method, Chain of Responsibility

### Anti-Pattern Detection
- **God Object** - Classes with too many responsibilities
- **Tight Coupling** - Excessive dependencies between components
- **Feature Envy** - Classes using other classes' data excessively
- **Shotgun Surgery** - Single changes affecting many classes

## Execution Process

### 1. Architectural Assessment
- Analyze class structure and responsibilities
- Identify SOLID principle violations
- Detect design pattern opportunities
- Evaluate component coupling and cohesion

### 2. Pattern Recommendation Engine
For each design opportunity:
- **Current Problem**: What architectural issue exists
- **Recommended Pattern**: Which pattern solves this problem
- **Implementation Strategy**: How to apply the pattern
- **Code Examples**: Before/after implementation
- **Benefits Analysis**: What improvements the pattern provides
- **Trade-offs**: Complexity vs. flexibility considerations

### 3. Refactoring Roadmap
- **Priority Order**: Most impactful architectural improvements first
- **Step-by-step Implementation**: Gradual refactoring approach
- **Risk Assessment**: Potential breaking changes and mitigation
- **Testing Strategy**: How to validate architectural changes

## Example Output Format

```
🏗️ Design Patterns & Architecture Analysis

🚨 SOLID Violation: Single Responsibility Principle
📍 Class: UserManager (Lines 15-85)

❌ Current Issues:
   class UserManager:
       def authenticate_user(self, credentials): ...
       def send_welcome_email(self, user): ...
       def calculate_user_age(self, birthdate): ...
       def log_user_activity(self, action): ...

🏗️ Recommended Refactoring: Separate Responsibilities
✅ Proposed Structure:
   class UserAuthenticator:
       def authenticate_user(self, credentials): ...
   
   class EmailService:
       def send_welcome_email(self, user): ...
   
   class AgeCalculator:
       def calculate_user_age(self, birthdate): ...
   
   class ActivityLogger:
       def log_user_activity(self, action): ...

💡 SOLID Principle: Single Responsibility
📚 Why This Matters:
   Large classes handling multiple concerns are harder to understand,
   test, and maintain. When authentication logic changes, you shouldn't
   risk breaking email functionality. Separate responsibilities into
   focused classes that each have one reason to change.

🎯 Benefits: Improved testability, maintainability, and reusability
⚖️ Trade-offs: More classes to manage, but clearer responsibilities

---

💡 PATTERN OPPORTUNITY: Strategy Pattern
📍 Lines 42-68: Complex conditional logic

❌ Current Implementation:
   def process_payment(self, payment_type, amount):
       if payment_type == 'credit_card':
           # Credit card processing logic (15 lines)
       elif payment_type == 'paypal':
           # PayPal processing logic (12 lines)
       elif payment_type == 'bank_transfer':
           # Bank transfer logic (18 lines)
       # Adding Bitcoin requires modifying this method

🏗️ Strategy Pattern Implementation:
✅ Proposed Refactoring:

   # 1. Define Strategy Interface
   from abc import ABC, abstractmethod
   
   class PaymentStrategy(ABC):
       @abstractmethod
       def process(self, amount): pass
   
   # 2. Implement Concrete Strategies
   class CreditCardPayment(PaymentStrategy):
       def process(self, amount):
           # Credit card logic here
           pass
   
   class PayPalPayment(PaymentStrategy):
       def process(self, amount):
           # PayPal logic here
           pass
   
   # 3. Context Class
   class PaymentProcessor:
       def __init__(self, strategy: PaymentStrategy):
           self.strategy = strategy
       
       def process_payment(self, amount):
           return self.strategy.process(amount)

🎯 Pattern Benefits:
   - Open/Closed Principle: Add new payment methods without modification
   - Single Responsibility: Each payment method in its own class
   - Testability: Easy to test each payment strategy independently
   - Runtime Flexibility: Switch payment strategies dynamically

📚 When to Use Strategy Pattern:
   - Multiple ways to perform the same task
   - Complex conditional logic based on type
   - Need to switch algorithms at runtime
   - Want to add new behaviors without modifying existing code

⚖️ Trade-offs: More classes and interfaces, but much more flexible

---

🔧 DEPENDENCY INJECTION OPPORTUNITY
📍 Line 23: Hard-coded database instantiation

❌ Current Problem:
   class UserService:
       def __init__(self):
           self.database = PostgreSQLDatabase()  # Hard-coded!
   
🏗️ Dependency Injection Solution:
✅ Improved Design:
   class UserService:
       def __init__(self, database: Database):
           self.database = database
   
   # Usage with dependency injection
   database = PostgreSQLDatabase()
   user_service = UserService(database)
   
   # Easy testing with mocks
   mock_database = MockDatabase()
   test_service = UserService(mock_database)

💡 SOLID Principle: Dependency Inversion
📚 Benefits:
   - Testability: Easy to inject mock dependencies
   - Flexibility: Switch database implementations
   - Loose Coupling: Class doesn't depend on concrete implementation
   - Configuration: Dependencies can be configured externally
```

## Design Pattern Catalog Integration

### Creational Patterns
```python
# Factory Method Pattern
class ShapeFactory:
    @staticmethod
    def create_shape(shape_type, **kwargs):
        if shape_type == 'circle':
            return Circle(kwargs['radius'])
        elif shape_type == 'rectangle':
            return Rectangle(kwargs['width'], kwargs['height'])

# Builder Pattern
class QueryBuilder:
    def __init__(self):
        self.query_parts = {}
    
    def select(self, fields):
        self.query_parts['select'] = fields
        return self
    
    def from_table(self, table):
        self.query_parts['from'] = table
        return self
    
    def where(self, condition):
        self.query_parts['where'] = condition
        return self
    
    def build(self):
        return Query(self.query_parts)
```

### Structural Patterns
```python
# Decorator Pattern
class Coffee:
    def cost(self): return 5.0
    def description(self): return "Coffee"

class MilkDecorator:
    def __init__(self, coffee):
        self.coffee = coffee
    
    def cost(self): return self.coffee.cost() + 1.0
    def description(self): return self.coffee.description() + ", Milk"

# Adapter Pattern
class LegacyDatabase:
    def old_query(self, sql): pass

class DatabaseAdapter:
    def __init__(self, legacy_db):
        self.legacy_db = legacy_db
    
    def query(self, sql):  # Modern interface
        return self.legacy_db.old_query(sql)
```

### Behavioral Patterns
```python
# Observer Pattern
class Subject:
    def __init__(self):
        self._observers = []
    
    def attach(self, observer):
        self._observers.append(observer)
    
    def notify(self, message):
        for observer in self._observers:
            observer.update(message)

# Command Pattern
class Command(ABC):
    @abstractmethod
    def execute(self): pass

class SaveCommand(Command):
    def __init__(self, document):
        self.document = document
    
    def execute(self):
        self.document.save()
```

## Integration with SuperClaude Framework

### Persona Integration
- Automatically activates **Architect** persona for system-level thinking
- Integration with **Refactorer** persona for code improvement focus
- **Mentor** persona for educational pattern explanations

### MCP Server Usage
- **Context7**: Access Gang of Four pattern documentation and examples
- **Sequential**: Systematic analysis of architectural patterns and violations
- Comprehensive Read/Grep tools for class relationship analysis

### Quality Gates
- ✅ SOLID principle compliance assessment
- ✅ Design pattern applicability analysis
- ✅ Concrete implementation examples
- ✅ Trade-off analysis for each recommendation
- ✅ Step-by-step refactoring guidance

## Architectural Learning Outcomes

After using `/design_patterns`, developers will understand:
- How to identify and apply SOLID principles
- When and how to use common design patterns
- How to recognize architectural anti-patterns
- Trade-offs between flexibility and complexity
- Step-by-step refactoring techniques for better architecture

## Refactoring Safety

### Risk Mitigation Strategies
- **Incremental Changes**: Small, testable refactoring steps
- **Backward Compatibility**: Maintain existing interfaces during transition
- **Test Coverage**: Ensure comprehensive tests before refactoring
- **Feature Flags**: Gradual rollout of architectural changes

### Refactoring Patterns
- **Extract Class**: Split large classes into focused components
- **Extract Interface**: Create abstractions for better testability
- **Move Method**: Relocate methods to more appropriate classes
- **Replace Conditional with Polymorphism**: Use strategy/state patterns

## Related Commands
- `/code_review` - Comprehensive analysis including design patterns
- `/analyze --focus architecture` - Deep architectural analysis
- `/improve --arch` - Architecture-focused improvements
- `/refactor` - Systematic code restructuring with pattern application