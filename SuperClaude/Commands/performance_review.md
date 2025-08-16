---
allowed-tools: [Read, Grep, Glob, Edit, MultiEdit, Write, TodoWrite, Bash]
description: "Performance analysis and optimization recommendations for algorithms and efficiency"
---

# /sc:performance_review - Performance Analysis & Optimization

## Purpose
Identify performance bottlenecks, analyze algorithmic complexity, and recommend optimizations for better speed, memory usage, and scalability.

## Usage
```
/sc:performance_review [file_path|code_block] [--focus algorithm|memory|io|database] [--scale small|medium|large] [--profile]
```

## Arguments
- `file_path` - Path to file to analyze for performance issues
- `code_block` - Inline code to analyze (wrap in triple backticks)
- `--focus` - Focus analysis on specific performance area
- `--scale` - Target scale for optimization recommendations
- `--profile` - Include performance profiling suggestions

## Performance Analysis Framework

### Algorithmic Complexity Analysis
1. **Time Complexity** - Big O analysis for scalability assessment
2. **Space Complexity** - Memory usage patterns and optimization
3. **Algorithm Selection** - Choosing optimal algorithms for the use case
4. **Data Structure Efficiency** - Appropriate data structure selection

### Performance Categories
5. **Database Performance** - Query optimization, N+1 problems, indexing
6. **I/O Optimization** - File operations, network calls, blocking operations
7. **Memory Management** - Object creation, garbage collection, memory leaks
8. **Caching Strategies** - Memoization, cache invalidation, storage optimization

### Scale-Based Recommendations
- **Small Scale (< 1K items)**: Focus on code clarity over micro-optimizations
- **Medium Scale (1K-100K items)**: Algorithm choice matters, avoid O(n²)
- **Large Scale (100K+ items)**: Critical algorithm selection, caching, databases
- **Real-time Systems**: Latency-sensitive optimizations, async patterns

## Execution Process

### 1. Complexity Analysis
- Analyze algorithmic complexity (Big O notation)
- Identify performance bottlenecks and hot paths
- Evaluate data structure efficiency
- Assess scalability implications

### 2. Performance Impact Assessment
For each optimization opportunity:
- **Current Complexity**: Big O analysis of existing code
- **Performance Impact**: Quantified improvement estimates
- **Scale Threshold**: When optimization becomes critical
- **Optimization Strategy**: Specific improvement approach
- **Trade-offs**: Complexity vs. performance vs. maintainability
- **Implementation Effort**: Development cost estimation

### 3. Optimization Recommendations
- **Immediate Wins**: Low-effort, high-impact optimizations
- **Algorithmic Improvements**: Better algorithm selection
- **Architectural Changes**: Structural improvements for scalability
- **Monitoring Strategy**: How to measure performance improvements

## Example Output Format

```
⚡ Performance Analysis Results

🚨 CRITICAL: Quadratic Time Complexity
📍 Lines 15-25: Nested loop structure

⏱️ Current Complexity: O(n²) - Quadratic time
📊 Performance Impact: 
   - 1,000 items: ~1M operations
   - 10,000 items: ~100M operations  
   - 100,000 items: ~10B operations (unusable)

💡 Optimization Strategy: Hash Map Lookup
🔧 Recommended Implementation:
   # Instead of nested loops
   for item in list1:
       for target in list2:
           if item.id == target.id:
               process(item, target)
   
   # Use hash map for O(n) performance
   target_map = {target.id: target for target in list2}
   for item in list1:
       if item.id in target_map:
           process(item, target_map[item.id])

📈 Improved Complexity: O(n) - Linear time
🎯 Performance Gain: 1000x faster for 100K items
⚖️ Trade-offs: Slightly more memory usage, much better scalability

---

⚠️ HIGH: Database N+1 Query Problem  
📍 Line 42: User query inside loop

🐌 Current Issue:
   for user in User.objects.all():  # 1 query
       profile = user.profile.get()  # N queries
       
💥 Performance Impact:
   - 100 users = 101 database queries
   - Each query: ~5ms network latency
   - Total time: 500ms (very slow)

🔧 Optimization: Eager Loading
   users = User.objects.select_related('profile').all()  # 1 query
   for user in users:
       profile = user.profile  # No additional query
       
📈 Performance Gain: 50-100x faster
🎯 Scale Impact: Critical for any production load

---

💡 MEDIUM: String Concatenation in Loop
📍 Lines 78-82: Building result string

⏱️ Current Complexity: O(n²) for string building
🔧 Optimization: Use list.join()
   
   # Instead of:
   result = ""
   for item in items:
       result += str(item)  # O(n²) - creates new string each time
   
   # Use:
   result_parts = []
   for item in items:
       result_parts.append(str(item))
   result = ''.join(result_parts)  # O(n)

📈 Performance Gain: Significant for large strings
📊 Memory Impact: Reduced memory allocations
```

## Performance Profiling Integration

### Profiling Recommendations
```python
# CPU Profiling
import cProfile
import pstats

def profile_function():
    profiler = cProfile.Profile()
    profiler.enable()
    # Your code here
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative').print_stats(10)

# Memory Profiling  
from memory_profiler import profile

@profile
def memory_intensive_function():
    # Code to analyze memory usage
    pass

# Performance Benchmarking
import timeit

execution_time = timeit.timeit(
    lambda: your_function(),
    number=1000
)
```

### Monitoring Strategy
- **Key Metrics**: Response time, throughput, memory usage, CPU utilization
- **Benchmarking**: Before/after performance comparisons
- **Load Testing**: Performance under realistic loads
- **Continuous Monitoring**: Performance regression detection

## Optimization Patterns

### Data Structure Optimizations
- **Lists → Sets**: O(n) to O(1) for membership testing
- **Linear Search → Binary Search**: O(n) to O(log n) for sorted data
- **Nested Loops → Hash Maps**: O(n²) to O(n) for lookups
- **Repeated Calculations → Memoization**: Cache expensive computations

### Algorithmic Improvements
- **Sorting**: Use built-in sort() (Timsort O(n log n))
- **Searching**: Binary search for sorted data
- **Graph Traversal**: Choose BFS vs DFS based on use case
- **Dynamic Programming**: Avoid redundant recursive calculations

### I/O Optimizations
- **Batch Operations**: Group database/API calls
- **Async Operations**: Non-blocking I/O for concurrent tasks
- **Connection Pooling**: Reuse database connections
- **Lazy Loading**: Load data only when needed

## Integration with SuperClaude Framework

### Persona Integration
- Automatically activates **Performance** persona for optimization focus
- Integration with **Analyzer** persona for systematic bottleneck identification
- **Architect** persona for scalability and system-level optimizations

### MCP Server Usage
- **Sequential**: Systematic performance analysis across code paths
- **Context7**: Access performance best practices and optimization patterns
- **Playwright**: Performance testing and real-world benchmarking

### Quality Gates
- ✅ Big O complexity analysis for all suggestions
- ✅ Quantified performance impact estimates
- ✅ Scale thresholds for optimization criticality
- ✅ Trade-off analysis (performance vs. complexity)
- ✅ Concrete implementation examples

## Performance Learning Outcomes

After using `/performance_review`, developers will understand:
- How to analyze algorithmic complexity (Big O notation)
- When and how to optimize for different scales
- Common performance anti-patterns and their solutions
- Trade-offs between performance, complexity, and maintainability
- How to measure and validate performance improvements

## Performance Testing Integration

### Benchmarking Tools
- **Python**: `timeit`, `cProfile`, `memory_profiler`
- **JavaScript**: `console.time()`, Chrome DevTools, `benchmark.js`
- **Java**: JMH, VisualVM, JProfiler
- **Load Testing**: Artillery, JMeter, K6

### Performance Metrics
- **Latency**: Response time for individual operations
- **Throughput**: Operations per second under load
- **Resource Usage**: CPU, memory, disk, network utilization
- **Scalability**: Performance degradation with increased load

## Related Commands
- `/sc:code_review` - Comprehensive analysis including performance
- `/sc:analyze --focus performance` - Deep performance architecture analysis
- `/sc:improve --perf` - Performance-focused code improvements
- `/sc:benchmark` - Automated performance testing and validation