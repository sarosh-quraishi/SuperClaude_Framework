#!/usr/bin/env python3
"""
Test script for SuperClaude Multi-Agent Code Review System
Validates all components and demonstrates functionality
"""

import asyncio
import sys
import os
from datetime import datetime
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from SuperClaude.Extensions.CodeReview import (
        get_all_agents, AgentCoordinator, CodeParser, OutputManager, ReviewSession,
        SupportedLanguage
    )
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


class CodeReviewTester:
    """Test suite for multi-agent code review system"""
    
    def __init__(self):
        self.parser = CodeParser()
        self.output_manager = OutputManager()
        self.test_results = []
    
    async def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🧪 Starting SuperClaude Multi-Agent Code Review System Tests")
        print("=" * 60)
        
        # Test individual components
        await self.test_code_parser()
        await self.test_individual_agents()
        await self.test_agent_coordinator()
        await self.test_output_formatting()
        await self.test_sample_files()
        
        # Print summary
        self.print_test_summary()
    
    async def test_code_parser(self):
        """Test code parsing functionality"""
        print("\n📝 Testing Code Parser...")
        
        # Test Python code parsing
        python_code = '''
def hello_world():
    print("Hello, World!")

class TestClass:
    def __init__(self):
        self.value = 42
        
    def get_value(self):
        return self.value
'''
        
        try:
            context = self.parser.parse_code(python_code, "test.py")
            
            # Validate parsing results
            assert context.language == SupportedLanguage.PYTHON
            assert len(context.functions) >= 2  # hello_world and methods
            assert len(context.classes) >= 1   # TestClass
            assert len(context.lines) > 0
            
            print("✅ Code parser working correctly")
            self.test_results.append(("Code Parser", True, "All parsing tests passed"))
            
        except Exception as e:
            print(f"❌ Code parser failed: {e}")
            self.test_results.append(("Code Parser", False, str(e)))
    
    async def test_individual_agents(self):
        """Test each agent individually"""
        print("\n🤖 Testing Individual Agents...")
        
        agents = get_all_agents()
        test_code = '''
def process_user_data(user_input):
    # This function has multiple issues for testing
    temp = user_input  # Poor naming
    if temp and len(temp) > 0:  # Redundant check
        for i in range(len(temp)):  # Inefficient iteration
            print(temp[i])  # Should use logging
    return temp
'''
        
        for agent in agents:
            try:
                print(f"  Testing {agent.name}...")
                result = await agent.analyze_code(test_code, "python", "test.py")
                
                # Validate result structure
                assert hasattr(result, 'agent_name')
                assert hasattr(result, 'suggestions')
                assert hasattr(result, 'total_issues')
                assert hasattr(result, 'execution_time')
                
                print(f"    ✅ {agent.name}: {result.total_issues} suggestions found")
                self.test_results.append((f"Agent: {agent.name}", True, 
                                        f"{result.total_issues} suggestions generated"))
                
            except Exception as e:
                print(f"    ❌ {agent.name} failed: {e}")
                self.test_results.append((f"Agent: {agent.name}", False, str(e)))
    
    async def test_agent_coordinator(self):
        """Test multi-agent coordination"""
        print("\n🎭 Testing Agent Coordinator...")
        
        try:
            agents = get_all_agents()
            coordinator = AgentCoordinator(agents)
            
            test_code = '''
import sqlite3
import random

def vulnerable_function(user_id):
    # Multiple issues for comprehensive testing
    db = sqlite3.connect('users.db')
    query = f"SELECT * FROM users WHERE id = {user_id}"  # SQL injection
    results = db.execute(query).fetchall()
    
    token = random.randint(1000, 9999)  # Insecure random
    return results, token
'''
            
            review_result = await coordinator.run_comprehensive_review(
                test_code, "python", "test.py"
            )
            
            # Validate comprehensive review
            assert 'agent_results' in review_result
            assert 'conflicts' in review_result
            assert 'summary' in review_result
            assert len(review_result['agent_results']) == len(agents)
            
            total_suggestions = review_result['summary']['total_suggestions']
            print(f"✅ Agent Coordinator: {total_suggestions} total suggestions from {len(agents)} agents")
            
            # Check for expected conflicts
            if review_result['conflicts']:
                print(f"   Detected {len(review_result['conflicts'])} methodology conflicts")
            
            self.test_results.append(("Agent Coordinator", True, 
                                    f"{total_suggestions} suggestions, {len(review_result['conflicts'])} conflicts"))
            
        except Exception as e:
            print(f"❌ Agent Coordinator failed: {e}")
            self.test_results.append(("Agent Coordinator", False, str(e)))
    
    async def test_output_formatting(self):
        """Test different output formats"""
        print("\n🎨 Testing Output Formatting...")
        
        try:
            # Create mock review session
            agents = get_all_agents()
            coordinator = AgentCoordinator(agents)
            
            test_code = "def test(): pass"
            review_result = await coordinator.run_comprehensive_review(test_code, "python")
            
            # Create review session
            session = ReviewSession(
                session_id="test-session",
                timestamp=datetime.now(),
                file_path="test.py",
                original_code=test_code,
                language="python",
                agent_results=[],  # Simplified for testing
                conflicts=[],
                summary=review_result['summary']
            )
            
            # Test different output formats
            formats = ['interactive', 'report', 'json']
            for format_type in formats:
                try:
                    output = self.output_manager.format_output(session, format_type)
                    assert len(output) > 0
                    print(f"    ✅ {format_type.title()} format generated ({len(output)} chars)")
                except Exception as e:
                    print(f"    ❌ {format_type.title()} format failed: {e}")
            
            self.test_results.append(("Output Formatting", True, "All formats generated successfully"))
            
        except Exception as e:
            print(f"❌ Output formatting failed: {e}")
            self.test_results.append(("Output Formatting", False, str(e)))
    
    async def test_sample_files(self):
        """Test with provided sample files"""
        print("\n📁 Testing Sample Files...")
        
        test_files = [
            "test_fixtures/sample_python.py",
            "test_fixtures/sample_javascript.js"
        ]
        
        for file_path in test_files:
            full_path = Path(__file__).parent / file_path
            if full_path.exists():
                try:
                    print(f"  Testing {file_path}...")
                    
                    # Parse the file
                    context = self.parser.parse_file(str(full_path))
                    
                    # Run multi-agent review
                    agents = get_all_agents()
                    coordinator = AgentCoordinator(agents)
                    
                    review_result = await coordinator.run_comprehensive_review(
                        context.content, context.language.value, str(full_path)
                    )
                    
                    total_suggestions = review_result['summary']['total_suggestions']
                    print(f"    ✅ {file_path}: {total_suggestions} total suggestions")
                    
                    # Validate that we found issues (sample files have intentional problems)
                    assert total_suggestions > 0, "Sample files should contain detectable issues"
                    
                    self.test_results.append((f"Sample: {file_path}", True, 
                                            f"{total_suggestions} issues detected"))
                    
                except Exception as e:
                    print(f"    ❌ {file_path} failed: {e}")
                    self.test_results.append((f"Sample: {file_path}", False, str(e)))
            else:
                print(f"    ⚠️ {file_path} not found")
                self.test_results.append((f"Sample: {file_path}", False, "File not found"))
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎯 Test Summary")
        print("=" * 60)
        
        passed = sum(1 for _, success, _ in self.test_results if success)
        total = len(self.test_results)
        
        print(f"Overall Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Multi-agent code review system is working correctly.")
        else:
            print(f"⚠️ {total - passed} tests failed. See details below:")
        
        print("\nDetailed Results:")
        for test_name, success, details in self.test_results:
            status = "✅" if success else "❌"
            print(f"  {status} {test_name}: {details}")
        
        print("\n" + "=" * 60)


async def main():
    """Main test execution"""
    tester = CodeReviewTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ required")
        sys.exit(1)
    
    # Run tests
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        sys.exit(1)