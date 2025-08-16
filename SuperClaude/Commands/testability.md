---
allowed-tools: [Read, Grep, Glob, Edit, MultiEdit, Write, TodoWrite, Bash]
description: "Analyze code testability and recommend TDD best practices"
---

# /sc:testability - Testability Analysis & TDD Best Practices

## Purpose
Identify opportunities to improve code testability and recommend testing best practices including Test-Driven Development (TDD), mocking strategies, and test design.

## Usage
```
/sc:testability [file_path|code_block] [--focus tdd|mocking|coverage|isolation] [--generate-tests] [--tdd-guide]
```

## Arguments
- `file_path` - Path to file to analyze for testability issues
- `code_block` - Inline code to analyze (wrap in triple backticks)
- `--focus` - Focus on specific testability aspect
- `--generate-tests` - Generate example test cases for the analyzed code
- `--tdd-guide` - Include TDD cycle guidance and examples

## Testability Analysis Framework

### Core Testability Principles
1. **Dependency Injection** - Making dependencies explicit and replaceable
2. **Pure Functions** - Functions without side effects are easier to test
3. **Test Isolation** - Tests should be independent and not affect each other
4. **Mocking & Stubbing** - Isolating units under test from dependencies
5. **Error Testing** - Testable error conditions and recovery paths
6. **Time & Randomness Control** - Making non-deterministic elements controllable

### Testing Strategies
7. **Unit Testing** - Fast, isolated tests of individual components
8. **Integration Testing** - Testing component interactions and data flow
9. **Property-Based Testing** - Testing with generated inputs for edge cases
10. **Test Coverage** - Meaningful coverage of critical paths and scenarios

### Anti-Patterns Detection
- **Hard-to-test Code** - Tightly coupled, many hidden dependencies
- **Global State Dependencies** - Tests that interfere with each other
- **Untestable Side Effects** - Operations that can't be verified
- **Time-Dependent Code** - Tests that depend on current time/dates

## Execution Process

### 1. Testability Assessment
- Analyze code structure for testing barriers
- Identify hard dependencies and coupling issues
- Evaluate function purity and side effects
- Assess error handling and edge case coverage

### 2. TDD Recommendations
For each testability issue:
- **Testing Barrier**: What makes the code hard to test
- **Refactoring Strategy**: How to make it more testable
- **Test Design**: Specific testing approaches and patterns
- **Mock Strategy**: What dependencies should be mocked and how
- **TDD Guidance**: How to apply red-green-refactor cycle
- **Example Tests**: Concrete test cases demonstrating best practices

### 3. Testing Implementation Plan
- **Priority Order**: Most critical testability improvements first
- **Incremental Testing**: Step-by-step test implementation strategy
- **Coverage Strategy**: Which tests provide the most value
- **Automation Integration**: CI/CD pipeline integration recommendations

## Example Output Format

```
🧪 Testability Analysis Results

🚨 CRITICAL: Hard-Coded Dependencies
📍 Class: UserService (Line 15)

❌ Current Testability Issue:
   class UserService:
       def __init__(self):
           self.database = PostgreSQLDatabase()  # Hard-coded!
           self.email_service = SMTPEmailService()  # Hard-coded!
       
       def create_user(self, user_data):
           user = self.database.save(user_data)
           self.email_service.send_welcome_email(user)
           return user

🧪 Testability Problems:
   - Cannot test without real database connection
   - Cannot test without real email service
   - Tests are slow and fragile
   - Cannot test error scenarios easily

🔧 Dependency Injection Solution:
✅ Testable Implementation:
   class UserService:
       def __init__(self, database: Database, email_service: EmailService):
           self.database = database
           self.email_service = email_service
       
       def create_user(self, user_data):
           user = self.database.save(user_data)
           self.email_service.send_welcome_email(user)
           return user

🧪 Example Test Implementation:
   import pytest
   from unittest.mock import Mock, MagicMock
   
   class TestUserService:
       def setup_method(self):
           self.mock_database = Mock(spec=Database)
           self.mock_email = Mock(spec=EmailService)
           self.user_service = UserService(self.mock_database, self.mock_email)
       
       def test_create_user_success(self):
           # Arrange
           user_data = {'email': 'test@example.com', 'name': 'Test User'}
           expected_user = User(id=1, email='test@example.com', name='Test User')
           self.mock_database.save.return_value = expected_user
           
           # Act
           result = self.user_service.create_user(user_data)
           
           # Assert
           assert result == expected_user
           self.mock_database.save.assert_called_once_with(user_data)
           self.mock_email.send_welcome_email.assert_called_once_with(expected_user)
       
       def test_create_user_database_error(self):
           # Arrange
           self.mock_database.save.side_effect = DatabaseException("Connection failed")
           
           # Act & Assert
           with pytest.raises(DatabaseException):
               self.user_service.create_user({'email': 'test@example.com'})
           
           # Email should not be sent if database fails
           self.mock_email.send_welcome_email.assert_not_called()

💡 Testing Principle: Dependency Injection
📚 Why This Improves Testability:
   - Fast Tests: No real database/email connections
   - Reliable Tests: Not dependent on external services
   - Isolated Tests: Each test controls its own dependencies
   - Error Testing: Easy to simulate failure scenarios
   - Parallel Execution: Tests don't interfere with each other

🎯 TDD Cycle Application:
   🔴 RED: Write failing test for create_user
   🟢 GREEN: Implement minimal code to pass
   🔵 REFACTOR: Improve design while keeping tests green

---

⚠️ HIGH: Time Dependencies Make Tests Non-Deterministic
📍 Line 42: Direct datetime.now() usage

❌ Current Problem:
   def process_subscription(self, user):
       current_time = datetime.now()  # Non-deterministic!
       if user.subscription_expires < current_time:
           user.deactivate()
       return user

🧪 Testing Issues:
   - Tests pass/fail based on when they run
   - Cannot test specific time scenarios
   - Difficult to test edge cases around expiration
   - Time-zone dependent behavior

🔧 Testable Time Solution:
✅ Injectable Time Implementation:
   def process_subscription(self, user, current_time=None):
       current_time = current_time or datetime.now()
       if user.subscription_expires < current_time:
           user.deactivate()
       return user

🧪 Example Time-Controlled Tests:
   def test_process_subscription_expired(self):
       # Arrange
       expiry_time = datetime(2024, 1, 1, 12, 0, 0)
       user = User(subscription_expires=expiry_time)
       test_time = datetime(2024, 1, 2, 12, 0, 0)  # After expiry
       
       # Act
       result = service.process_subscription(user, current_time=test_time)
       
       # Assert
       assert user.is_active == False
   
   def test_process_subscription_active(self):
       # Arrange
       expiry_time = datetime(2024, 1, 1, 12, 0, 0)
       user = User(subscription_expires=expiry_time)
       test_time = datetime(2023, 12, 31, 12, 0, 0)  # Before expiry
       
       # Act
       result = service.process_subscription(user, current_time=test_time)
       
       # Assert
       assert user.is_active == True

💡 Testing Principle: Controllable Non-Determinism
📚 Benefits:
   - Deterministic Tests: Same result every time
   - Edge Case Testing: Test exact boundary conditions
   - Time Zone Testing: Control timezone behavior
   - Future/Past Scenarios: Test with any date/time

---

💡 MEDIUM: Function Too Complex for Comprehensive Testing
📍 Lines 65-95: Complex function with multiple responsibilities

❌ Current Complexity:
   def process_order(self, order_data):  # 30 lines, multiple concerns
       # Validate input (5 lines)
       # Calculate pricing (8 lines)
       # Apply discounts (7 lines)
       # Update inventory (6 lines)
       # Send notifications (4 lines)
       return result

🧪 Testing Challenges:
   - Need many test cases for complete coverage
   - Hard to test individual concerns in isolation
   - Complex setup required for comprehensive testing
   - Difficult to identify which part failed

🔧 Testability Refactoring:
✅ Break into Focused Functions:
   def process_order(self, order_data):
       validated_data = self.validate_order_input(order_data)
       pricing = self.calculate_pricing(validated_data)
       final_price = self.apply_discounts(pricing, validated_data)
       self.update_inventory(validated_data)
       self.send_order_notifications(validated_data)
       return self.create_order_result(validated_data, final_price)

🧪 Improved Testing Strategy:
   # Test each function independently
   def test_validate_order_input(self): ...
   def test_calculate_pricing(self): ...
   def test_apply_discounts(self): ...
   def test_update_inventory(self): ...
   def test_send_order_notifications(self): ...
   
   # Integration test for the main flow
   def test_process_order_integration(self): ...

💡 Testing Principle: Single Responsibility for Functions
📚 Benefits:
   - Focused Tests: Each test verifies one concern
   - Clear Failures: Easy to identify what broke
   - Reusable Components: Functions can be tested and reused independently
   - Comprehensive Coverage: Easier to test all edge cases
```

## TDD Methodology Integration

### Red-Green-Refactor Cycle
```python
# 🔴 RED: Write failing test first
def test_calculate_discount_percentage():
    calculator = DiscountCalculator()
    result = calculator.calculate_discount(100, 'SAVE20')
    assert result == 20.0  # This will fail - no implementation yet

# 🟢 GREEN: Write minimal code to pass
class DiscountCalculator:
    def calculate_discount(self, amount, code):
        if code == 'SAVE20':
            return 20.0
        return 0.0

# 🔵 REFACTOR: Improve design while keeping tests green
class DiscountCalculator:
    def __init__(self):
        self.discount_codes = {
            'SAVE20': 0.20,
            'SAVE10': 0.10,
            'SAVE5': 0.05
        }
    
    def calculate_discount(self, amount, code):
        discount_rate = self.discount_codes.get(code, 0.0)
        return amount * discount_rate
```

### Test Design Patterns

#### AAA Pattern (Arrange-Act-Assert)
```python
def test_user_registration():
    # Arrange
    user_data = {'email': 'test@example.com', 'password': 'SecurePass123!'}
    user_service = UserService(mock_database, mock_email)
    
    # Act
    result = user_service.register_user(user_data)
    
    # Assert
    assert result.success == True
    assert result.user.email == 'test@example.com'
```

#### Test Fixtures and Factories
```python
@pytest.fixture
def user_service():
    mock_db = Mock(spec=Database)
    mock_email = Mock(spec=EmailService)
    return UserService(mock_db, mock_email)

@pytest.fixture
def sample_user():
    return User(
        id=1,
        email='test@example.com',
        name='Test User',
        created_at=datetime(2024, 1, 1)
    )

def test_user_activation(user_service, sample_user):
    # Test uses clean fixtures
    result = user_service.activate_user(sample_user)
    assert result.is_active == True
```

## Testing Frameworks Integration

### Python Testing Ecosystem
```python
# pytest - Modern testing framework
import pytest
from unittest.mock import Mock, patch, MagicMock

# Property-based testing with Hypothesis
from hypothesis import given, strategies as st

@given(st.integers(min_value=1, max_value=1000))
def test_discount_calculation_properties(amount):
    calculator = DiscountCalculator()
    discount = calculator.calculate_discount(amount, 'SAVE20')
    
    # Properties that should always hold
    assert discount >= 0
    assert discount <= amount
    assert isinstance(discount, (int, float))

# Coverage reporting
# pytest --cov=mymodule --cov-report=html
```

### Mocking Strategies
```python
# Mock external dependencies
@patch('requests.get')
def test_api_integration(mock_get):
    mock_get.return_value.json.return_value = {'status': 'success'}
    
    service = ExternalAPIService()
    result = service.fetch_data()
    
    assert result['status'] == 'success'
    mock_get.assert_called_once()

# Mock time-dependent operations
@patch('datetime.datetime')
def test_time_dependent_function(mock_datetime):
    mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0, 0)
    
    result = time_sensitive_function()
    
    assert result.timestamp == datetime(2024, 1, 1, 12, 0, 0)
```

## Integration with SuperClaude Framework

### Persona Integration
- Automatically activates **QA** persona for testing mindset
- Integration with **TDD Mentor** persona for educational testing guidance
- **Refactorer** persona for testability improvements

### MCP Server Usage
- **Sequential**: Systematic testability analysis across code components
- **Context7**: Access testing framework documentation and patterns
- **Playwright**: Browser-based testing for web applications

### Quality Gates
- ✅ Testability barrier identification
- ✅ Concrete test implementation examples
- ✅ TDD cycle application guidance
- ✅ Mocking strategy recommendations
- ✅ Coverage and quality metrics

## Testing Learning Outcomes

After using `/testability`, developers will understand:
- How to identify and remove testing barriers
- Test-Driven Development methodology and benefits
- Effective mocking and stubbing strategies
- How to design tests that are maintainable and valuable
- Property-based testing for finding edge cases

## Testing Automation Integration

### CI/CD Pipeline Integration
```yaml
# GitHub Actions example
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests with coverage
        run: pytest --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

### Quality Metrics
- **Test Coverage**: Line, branch, and function coverage
- **Test Quality**: Mutation testing, assertion coverage
- **Performance**: Test execution time, flaky test detection
- **Maintainability**: Test complexity, duplication metrics

## Related Commands
- `/sc:code_review` - Comprehensive analysis including testability
- `/sc:test` - Execute test suites and generate reports
- `/sc:improve --quality` - Quality improvements including testability
- `/sc:tdd` - Guided Test-Driven Development workflow