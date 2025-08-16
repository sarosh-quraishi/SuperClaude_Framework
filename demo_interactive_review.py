#!/usr/bin/env python3
"""
Demo Script for Interactive Code Review System
Shows the capabilities and usage patterns of the interactive diff reviewer
"""

import os
import tempfile
from pathlib import Path

# Create a sample file with code that needs improvement
sample_code = '''# Calculator with some code quality issues
def calc(x, y):
    return x + y

def multiply(a, b):
    result = a * b
    return result

def divide(x, y):
    return x / y  # No error checking!

class User:
    def __init__(self, n, a, e):
        self.n = n
        self.a = a  
        self.e = e
    
    def getName(self):
        return self.n
    
    def getAge(self):
        return self.a
        
    def getEmail(self):
        return self.e

def process_users(users):
    result = []
    for user in users:
        if user.getAge() > 18:
            result.append(user.getName())
    return result

def insecure_input():
    user_input = input("Enter SQL query: ")
    return f"SELECT * FROM users WHERE name = '{user_input}'"  # SQL injection risk!

def inefficient_search(data, target):
    found = False
    for i in range(len(data)):
        for j in range(len(data)):
            if data[i] == target:
                found = True
    return found
'''

def create_demo_file():
    """Create a temporary demo file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(sample_code)
        return f.name

def main():
    """Main demo function"""
    print("🎯 Interactive Code Review Demo")
    print("=" * 60)
    
    # Create demo file
    demo_file = create_demo_file()
    print(f"📁 Created demo file: {demo_file}")
    
    print(f"\n📋 Sample code with multiple issues:")
    print("-" * 40)
    print(sample_code)
    print("-" * 40)
    
    print(f"\n🔍 Issues this code has:")
    print("✅ Clean Code: Non-descriptive variable names (x, y, n, a, e)")
    print("✅ Security: SQL injection vulnerability in insecure_input()")  
    print("✅ Performance: O(n²) algorithm in inefficient_search()")
    print("✅ Design: Violates encapsulation principles in User class")
    print("✅ Safety: No error handling in divide() function")
    
    print(f"\n🚀 To run interactive review:")
    print(f"   python -m SuperClaude.Extensions.CodeReview.interactive_review_coordinator {demo_file}")
    
    print(f"\n📖 Interactive Review Features:")
    print("• Git-style diff visualization")
    print("• Accept/Reject/Skip individual suggestions")
    print("• Edit suggestions before accepting")
    print("• Educational explanations for each issue")
    print("• Batch accept/reject options")
    print("• Session saving and patch export")
    
    print(f"\n🎮 Controls:")
    print("• [a] Accept suggestion")
    print("• [r] Reject suggestion")  
    print("• [s] Skip for later")
    print("• [e] Edit before accepting")
    print("• [l] Learn more (detailed explanation)")
    print("• [A] Accept all remaining")
    print("• [R] Reject all remaining")
    print("• [q] Quit review")
    
    print(f"\n💡 Example workflow:")
    print("1. Review shows first suggestion with diff")
    print("2. Press 'l' to learn why it matters")
    print("3. Press 'a' to accept, 'r' to reject, or 'e' to edit")
    print("4. Continue through all suggestions")
    print("5. Get final improved code with all accepted changes")
    
    print(f"\n🏁 Try it now:")
    print(f"   cd {Path(demo_file).parent}")
    print(f"   python -m SuperClaude.Extensions.CodeReview.interactive_review_coordinator {Path(demo_file).name}")
    
    # Keep the file for user to try
    print(f"\n📝 Demo file will remain at: {demo_file}")
    print("   (You can delete it manually when done)")

if __name__ == "__main__":
    main()