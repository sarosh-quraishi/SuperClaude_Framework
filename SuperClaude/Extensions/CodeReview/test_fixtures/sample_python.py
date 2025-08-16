#!/usr/bin/env python3
"""
Sample Python code with various code quality issues for testing multi-agent code review.
This file intentionally contains problems that each agent should detect.
"""

import os
import datetime
import random
import sqlite3

# Global variable (testability issue)
user_database = sqlite3.connect('users.db')

# Hardcoded secret (security issue)
API_KEY = "sk-1234567890abcdef"

class UserManager:  # God object (design patterns issue)
    def __init__(self):
        self.db = sqlite3.connect('users.db')  # Hard-coded dependency (testability)
    
    # Long function with multiple responsibilities (clean code issue)
    def process_user_data_and_send_email_and_log_activity(self, user_data):
        # Generic variable names (clean code issue)
        temp = user_data
        d = datetime.datetime.now()  # Time dependency (testability)
        
        # SQL injection vulnerability (security issue)
        query = f"SELECT * FROM users WHERE email = '{temp['email']}'"
        result = self.db.execute(query).fetchall()
        
        # Inefficient nested loops (performance issue)
        for user in result:
            for permission in self.get_all_permissions():  # N+1 query problem
                if user[2] == permission[1]:  # Magic numbers (clean code)
                    self.grant_permission(user, permission)
        
        # Hard-coded email service (testability issue)
        email_service = SMTPEmailService()
        email_service.send_email(temp['email'], "Welcome!")
        
        # Error handling that silently fails (security/clean code issue)
        try:
            self.log_user_activity(temp['user_id'], "registration")
        except:
            pass  # Silent failure
        
        return temp
    
    def get_all_permissions(self):
        # Another database query in loop (performance issue)
        return self.db.execute("SELECT * FROM permissions").fetchall()
    
    def grant_permission(self, user, permission):
        # Using random for security-sensitive operation (security issue)
        token = random.randint(100000, 999999)
        
        # String concatenation in loop (performance issue)
        log_message = ""
        for i in range(len(permission)):
            log_message += str(permission[i]) + ", "
        
        print(f"Granted permission with token: {token}")
    
    def log_user_activity(self, uid, action):
        # Type checking instead of polymorphism (design patterns issue)
        if isinstance(action, str):
            self.log_string_action(action)
        elif isinstance(action, dict):
            self.log_dict_action(action)
        elif isinstance(action, list):
            self.log_list_action(action)
    
    # Functions with too many parameters (clean code issue)
    def create_user_profile(self, first_name, last_name, email, phone, address, 
                           city, state, zip_code, country, date_of_birth, 
                           gender, occupation, company):
        # Complex conditional logic (testability issue)
        if first_name and last_name and email and phone and address and city and state:
            # File operation without abstraction (testability issue)
            with open('/tmp/user_profiles.log', 'a') as f:
                f.write(f"{first_name},{last_name},{email}\n")
            return True
        return False

class SMTPEmailService:  # Should use dependency injection
    def send_email(self, email, message):
        # Direct network call (testability issue)
        import smtplib
        # Hardcoded SMTP server (security/configuration issue)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.send_message(message)

# Function that should use Strategy pattern (design patterns issue)
def process_payment(payment_type, amount):
    if payment_type == 'credit_card':
        # Credit card processing logic (15 lines)
        print("Processing credit card payment")
        fee = amount * 0.03
        total = amount + fee
        return total
    elif payment_type == 'paypal':
        # PayPal processing logic (12 lines)  
        print("Processing PayPal payment")
        fee = amount * 0.025
        total = amount + fee
        return total
    elif payment_type == 'bank_transfer':
        # Bank transfer logic (10 lines)
        print("Processing bank transfer")
        fee = 5.00
        total = amount + fee
        return total
    # Adding new payment method requires modifying this function

# Function with poor algorithm choice (performance issue)
def find_user_by_email(users, target_email):
    # Linear search when hash map would be O(1)
    for user in users:
        if user.email == target_email:
            return user
    return None

# Function with eval vulnerability (security issue)
def calculate_expression(expression):
    # Dangerous: allows arbitrary code execution
    result = eval(expression)
    return result

# Function using global state (testability issue)
def get_user_count():
    global user_database
    cursor = user_database.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    return cursor.fetchone()[0]

# Function with magic numbers and poor naming (clean code issue)
def process_data(d):
    result = []
    for i in range(len(d)):
        if d[i] > 100:  # Magic number
            result.append(d[i] * 1.5)  # Magic number
        elif d[i] > 50:  # Magic number
            result.append(d[i] * 1.2)  # Magic number
        else:
            result.append(d[i])
    return result

# Function with performance anti-pattern
def sort_users_by_age(users):
    # Inefficient bubble sort when built-in sort is available
    n = len(users)
    for i in range(n):
        for j in range(0, n-i-1):
            if users[j].age > users[j+1].age:
                users[j], users[j+1] = users[j+1], users[j]
    return users

# Function that violates DRY principle (clean code issue)
def validate_email(email):
    if '@' not in email:
        return False
    if '.' not in email:
        return False
    if len(email) < 5:
        return False
    return True

def validate_backup_email(backup_email):
    # Duplicate validation logic
    if '@' not in backup_email:
        return False
    if '.' not in backup_email:
        return False
    if len(backup_email) < 5:
        return False
    return True