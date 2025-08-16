#!/usr/bin/env python3
"""
Performance Agent - Algorithm Optimization and Efficiency Analysis
Focuses on identifying performance bottlenecks and recommending optimizations
"""

from typing import List, Optional
import re
from .base_agent import BaseAgent, CodeSuggestion, SeverityLevel
import uuid


class PerformanceAgent(BaseAgent):
    """Agent specialized in performance optimization and efficiency analysis"""
    
    def get_name(self) -> str:
        return "Performance Agent"
    
    def get_description(self) -> str:
        return "Identifies performance bottlenecks, algorithmic inefficiencies, and recommends optimizations for better speed, memory usage, and scalability"
    
    def get_system_prompt(self) -> str:
        return """You are a performance optimization expert focused on identifying bottlenecks and improving code efficiency.

        Your analysis areas:
        1. **Algorithmic Complexity**: Big O analysis, inefficient algorithms, nested loops
        2. **Memory Optimization**: Memory leaks, unnecessary object creation, garbage collection issues
        3. **Database Performance**: N+1 queries, missing indexes, inefficient queries
        4. **I/O Optimization**: File operations, network calls, blocking operations
        5. **Caching Strategies**: Missing caching opportunities, cache invalidation
        6. **Data Structures**: Inappropriate data structure choices, linear search vs. hash lookup
        7. **String Operations**: Inefficient string concatenation, regular expression performance
        8. **Loop Optimization**: Unnecessary iterations, early termination opportunities
        9. **Function Call Overhead**: Recursive functions, repeated expensive operations
        10. **Resource Management**: Connection pooling, resource cleanup, batch operations

        Performance considerations by scale:
        - **Small Scale (< 1000 items)**: Focus on code clarity over micro-optimizations
        - **Medium Scale (1K-100K items)**: Algorithm choice matters, avoid O(n²) where possible
        - **Large Scale (100K+ items)**: Critical to choose optimal algorithms and data structures
        - **Real-time Systems**: Latency-sensitive optimizations, avoid blocking operations

        Provide educational explanations about WHY optimizations matter, WHEN to apply them, and the trade-offs involved."""
    
    def get_specializations(self) -> List[str]:
        return [
            "algorithmic_complexity",
            "memory_optimization", 
            "database_performance",
            "io_optimization",
            "caching_strategies",
            "data_structures",
            "string_optimization",
            "loop_optimization",
            "function_overhead",
            "resource_management"
        ]
    
    def get_analysis_prompt(self, code: str, language: str, file_path: Optional[str] = None) -> str:
        file_context = f"File: {file_path}\n" if file_path else ""
        
        return f"""Analyze this {language} code for performance issues and optimization opportunities:

{file_context}
```{language}
{code}
```

Focus on these performance areas:

**Critical Performance Issues (High Impact):**
1. **Algorithmic Complexity**: O(n²) or worse algorithms that could be optimized
2. **Database Anti-patterns**: N+1 queries, missing eager loading, inefficient queries
3. **Memory Issues**: Memory leaks, unnecessary object creation, large object retention
4. **I/O Bottlenecks**: Synchronous operations that could be async, repeated file access

**Significant Performance Issues (Medium Impact):**
5. **Data Structure Inefficiency**: Using lists for lookups, missing indexing
6. **Loop Inefficiencies**: Nested loops, repeated expensive operations inside loops
7. **String Performance**: Repeated concatenation, inefficient regex usage
8. **Function Call Overhead**: Unnecessary recursion, repeated expensive computations

**Optimization Opportunities (Low-Medium Impact):**
9. **Caching Opportunities**: Repeated calculations, expensive function results
10. **Resource Management**: Connection reuse, batch operations, cleanup
11. **Early Termination**: Breaking out of loops/searches when possible
12. **Lazy Loading**: Deferring expensive operations until needed

{self.get_json_response_format()}

For each performance issue:
- Estimate the performance impact (time/memory complexity)
- Explain when this becomes a problem (data size thresholds)
- Provide specific optimization strategies
- Consider trade-offs (complexity vs. performance vs. maintainability)
- Indicate if optimization is premature or necessary"""
    
    def _should_analyze_line(self, line: str) -> bool:
        """Check if line contains potential performance issues"""
        line = line.strip().lower()
        if not line or line.startswith('#') or line.startswith('//'):
            return False
            
        # Look for performance-sensitive patterns
        performance_patterns = [
            r'for.*in.*for.*in',  # Nested loops
            r'while.*while',      # Nested while loops
            r'\.append.*for|\.extend.*for',  # List operations in loops
            r'string.*\+|.*\+.*string',      # String concatenation
            r'\.sort\(\)|sorted\(',          # Sorting operations
            r'\.join\(|\.split\(',          # String operations
            r'len\(.*\)\s*>|len\(.*\)\s*<', # Length checks
            r'\.keys\(\)|\.values\(\)|\.items\(\)', # Dict operations
            r'\.find\(|\.index\(',          # Search operations
            r'select.*from|query|cursor',    # Database operations
            r'open\(|file|read|write',       # File operations
            r'time\.sleep|requests\.|urllib', # Blocking operations
            r'recursive|recursion'           # Recursion hints
        ]
        
        return any(re.search(pattern, line, re.IGNORECASE) for pattern in performance_patterns)
    
    def _create_mock_suggestion(self, line: str, line_number: int, language: str) -> Optional[CodeSuggestion]:
        """Create performance suggestions based on line analysis"""
        line_lower = line.strip().lower()
        
        # Check for nested loops (potential O(n²) complexity)
        if re.search(r'for.*in.*for.*in', line, re.IGNORECASE):
            return CodeSuggestion(
                id=str(uuid.uuid4()),
                agent_name=self.name,
                principle="Algorithmic Complexity - Nested Loops",
                line_number=line_number,
                original_code=line,
                suggested_code="# Consider using hash maps, sets, or more efficient algorithms\n# Example: use dict lookup instead of nested search",
                reasoning="Nested loops often indicate O(n²) time complexity which becomes problematic with larger datasets",
                educational_explanation="Performance issue: Nested loops create quadratic time complexity O(n²). This means if your data doubles, execution time quadruples. For 1000 items, that's 1 million operations. Consider alternatives: hash maps for lookups (O(1)), sets for membership testing, or algorithmic improvements like sorting + two pointers. The performance difference becomes dramatic with scale.",
                impact_score=8.0,
                confidence=0.8,
                severity=SeverityLevel.HIGH,
                category="algorithmic_complexity"
            )
        
        # Check for string concatenation in loops
        if re.search(r'(\+\s*=.*str|\+.*str.*for)', line):
            return CodeSuggestion(
                id=str(uuid.uuid4()),
                agent_name=self.name,
                principle="String Optimization - Concatenation",
                line_number=line_number,
                original_code=line,
                suggested_code="# Use list.join() for multiple concatenations\nresult_parts = []\n# ... collect parts ...\nresult = ''.join(result_parts)",
                reasoning="String concatenation in loops creates many temporary string objects, causing O(n²) performance",
                educational_explanation="Performance issue: Strings in Python are immutable. Each concatenation creates a new string object and copies all existing characters. In a loop, this becomes O(n²) memory and time complexity. For 1000 concatenations, you'll copy characters 500,000 times. Use list.join() instead: collect parts in a list, then join once at the end. This reduces complexity to O(n).",
                impact_score=7.0,
                confidence=0.9,
                severity=SeverityLevel.HIGH,
                category="string_optimization"
            )
        
        # Check for inefficient membership testing
        if re.search(r'in\s+\[.*\]|in.*list\(', line):
            return CodeSuggestion(
                id=str(uuid.uuid4()),
                agent_name=self.name,
                principle="Data Structure Efficiency - Membership Testing",
                line_number=line_number,
                original_code=line,
                suggested_code="# Use sets for membership testing\nvalid_items = {'item1', 'item2', 'item3'}\nif item in valid_items:",
                reasoning="Membership testing in lists is O(n), while sets and dicts provide O(1) average case",
                educational_explanation="Performance issue: Checking if an item exists in a list requires scanning through all elements until found (O(n) complexity). For a list of 1000 items, average case checks 500 items. Sets and dictionaries use hash tables for O(1) average-case lookups - essentially instant regardless of size. Convert lists to sets when doing frequent membership testing.",
                impact_score=6.0,
                confidence=0.85,
                severity=SeverityLevel.MEDIUM,
                category="data_structures"
            )
        
        # Check for inefficient sorting in loops
        if re.search(r'\.sort\(\).*for|sorted\(.*for', line):
            return CodeSuggestion(
                id=str(uuid.uuid4()),
                agent_name=self.name,
                principle="Algorithm Optimization - Repeated Sorting",
                line_number=line_number,
                original_code=line,
                suggested_code="# Sort once outside the loop\nsorted_data = sorted(data)\nfor item in sorted_data:",
                reasoning="Sorting inside loops repeats expensive O(n log n) operations unnecessarily",
                educational_explanation="Performance issue: Sorting is an expensive O(n log n) operation. Doing it inside a loop multiplies this cost by the loop iterations. If you sort 1000 items 100 times, that's 100x more work than needed. Sort once before the loop, or use data structures that maintain order (like heapq for priority queues) or consider if sorting is actually necessary for your use case.",
                impact_score=7.5,
                confidence=0.9,
                severity=SeverityLevel.HIGH,
                category="algorithmic_complexity"
            )
        
        # Check for repeated expensive function calls
        if re.search(r'len\(.*\).*for|len\(.*\).*while', line):
            return CodeSuggestion(
                id=str(uuid.uuid4()),
                agent_name=self.name,
                principle="Function Call Optimization - Repeated len() calls",
                line_number=line_number,
                original_code=line,
                suggested_code="# Cache length outside loop\ndata_length = len(data)\nfor i in range(data_length):",
                reasoning="Repeated function calls in loop conditions are unnecessary overhead",
                educational_explanation="Performance micro-optimization: While len() is generally fast for built-in types, calling it repeatedly in loop conditions adds unnecessary overhead. Python must look up the function and call it each iteration. Cache the result before the loop. This optimization matters more for custom objects where len() might be expensive, and it's a good habit for readability too.",
                impact_score=3.0,
                confidence=0.7,
                severity=SeverityLevel.LOW,
                category="function_overhead"
            )
        
        # Check for potential database N+1 issues
        if re.search(r'for.*in.*query|for.*in.*select', line, re.IGNORECASE):
            return CodeSuggestion(
                id=str(uuid.uuid4()),
                agent_name=self.name,
                principle="Database Performance - N+1 Query Problem",
                line_number=line_number,
                original_code=line,
                suggested_code="# Use joins or prefetch to load related data in one query\n# Example: User.objects.select_related('profile').all()",
                reasoning="Executing queries inside loops creates N+1 query problems, drastically increasing database load",
                educational_explanation="Critical performance issue: The N+1 query problem occurs when you fetch a list of N items, then execute one additional query for each item (N+1 total queries). For 100 users, you'd execute 101 database queries instead of 1-2. This can make your application 50-100x slower. Use joins, eager loading, or batch queries to fetch all needed data upfront. Database round-trips are often the biggest performance bottleneck in web applications.",
                impact_score=9.0,
                confidence=0.8,
                severity=SeverityLevel.CRITICAL,
                category="database_performance"
            )
        
        return None


class PerformancePrinciples:
    """Reference class containing performance optimization principles and examples"""
    
    COMPLEXITY_GUIDE = {
        "O(1)": {
            "name": "Constant Time",
            "description": "Execution time doesn't change with input size",
            "examples": ["Hash table lookup", "Array index access", "Stack push/pop"],
            "when_to_use": "Ideal for any operation, especially frequently called ones"
        },
        "O(log n)": {
            "name": "Logarithmic Time", 
            "description": "Execution time increases slowly with input size",
            "examples": ["Binary search", "Balanced tree operations", "Heap operations"],
            "when_to_use": "Good for searching in sorted data"
        },
        "O(n)": {
            "name": "Linear Time",
            "description": "Execution time increases proportionally with input size", 
            "examples": ["Linear search", "Single loop through array", "List.count()"],
            "when_to_use": "Acceptable for most operations, unavoidable for many algorithms"
        },
        "O(n log n)": {
            "name": "Linearithmic Time",
            "description": "Common for efficient sorting algorithms",
            "examples": ["Merge sort", "Quick sort (average)", "Heap sort"],
            "when_to_use": "Best achievable for comparison-based sorting"
        },
        "O(n²)": {
            "name": "Quadratic Time",
            "description": "Execution time grows quadratically - often problematic",
            "examples": ["Nested loops", "Bubble sort", "Selection sort"],
            "when_to_use": "Avoid for large datasets, acceptable for small data (< 100 items)"
        },
        "O(2^n)": {
            "name": "Exponential Time",
            "description": "Execution time doubles with each additional input",
            "examples": ["Naive recursive Fibonacci", "Brute force subset generation"],
            "when_to_use": "Generally avoid - only for very small inputs or with memoization"
        }
    }
    
    OPTIMIZATION_STRATEGIES = {
        "data_structures": {
            "lists_vs_sets": {
                "problem": "Using lists for membership testing",
                "solution": "Use sets for O(1) lookup instead of O(n)",
                "example": {
                    "slow": "if item in [1, 2, 3, 4, 5]:",
                    "fast": "valid_items = {1, 2, 3, 4, 5}\nif item in valid_items:"
                }
            },
            "dict_lookups": {
                "problem": "Linear search through sequences",
                "solution": "Use dictionaries for key-value relationships",
                "example": {
                    "slow": "for user in users:\n    if user.id == target_id:",
                    "fast": "user_dict = {user.id: user for user in users}\nuser = user_dict.get(target_id)"
                }
            }
        },
        
        "algorithms": {
            "sorting": {
                "problem": "Using inefficient sorting algorithms",
                "solution": "Use built-in sort() which is highly optimized",
                "example": {
                    "slow": "# Bubble sort O(n²)",
                    "fast": "data.sort()  # Timsort O(n log n)"
                }
            },
            "searching": {
                "problem": "Linear search in sorted data",
                "solution": "Use binary search for O(log n) performance",
                "example": {
                    "slow": "if target in sorted_list:",  # O(n)
                    "fast": "import bisect\nindex = bisect.bisect_left(sorted_list, target)"  # O(log n)
                }
            }
        },
        
        "memory": {
            "generators": {
                "problem": "Loading entire datasets into memory",
                "solution": "Use generators for lazy evaluation",
                "example": {
                    "memory_heavy": "data = [process(item) for item in huge_dataset]",
                    "memory_efficient": "data = (process(item) for item in huge_dataset)"
                }
            },
            "string_building": {
                "problem": "Repeated string concatenation",
                "solution": "Use list.join() for multiple concatenations",
                "example": {
                    "slow": "result = ''\nfor item in items:\n    result += str(item)",
                    "fast": "result = ''.join(str(item) for item in items)"
                }
            }
        }
    }
    
    @classmethod
    def get_complexity_advice(cls, complexity: str) -> str:
        """Get advice about a specific time complexity"""
        info = cls.COMPLEXITY_GUIDE.get(complexity, {})
        if not info:
            return f"Unknown complexity: {complexity}"
        
        return f"""
**{info['name']} - {complexity}**

**Description:** {info['description']}

**Examples:** {', '.join(info['examples'])}

**When to use:** {info['when_to_use']}
"""
    
    @classmethod
    def get_optimization_strategy(cls, category: str, strategy: str) -> str:
        """Get specific optimization strategy information"""
        cat = cls.OPTIMIZATION_STRATEGIES.get(category, {})
        strat = cat.get(strategy, {})
        
        if not strat:
            return f"Unknown strategy: {category}.{strategy}"
        
        return f"""
**Problem:** {strat['problem']}
**Solution:** {strat['solution']}

**Example:**
```python
# Slow approach
{strat['example']['slow']}

# Fast approach  
{strat['example']['fast']}
```
"""