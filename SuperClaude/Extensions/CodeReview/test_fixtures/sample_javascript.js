/**
 * Sample JavaScript code with various code quality issues for testing multi-agent code review.
 * This file intentionally contains problems that each agent should detect.
 */

// Hardcoded API key (security issue)
const API_KEY = 'sk-1234567890abcdef';

// Global variables (testability issue)
let userDatabase = null;
var currentUser = {};

class UserService { // God object (design patterns issue)
    constructor() {
        // Hard-coded dependency (testability issue)
        this.database = new SQLiteDatabase();
        this.emailService = new EmailService();
    }
    
    // Long function with multiple responsibilities (clean code issue)
    async processUserDataAndSendEmailAndLogActivity(userData) {
        // Generic variable names (clean code issue)
        let temp = userData;
        let d = new Date(); // Time dependency (testability)
        
        // SQL injection vulnerability (security issue)
        let query = `SELECT * FROM users WHERE email = '${temp.email}'`;
        let result = await this.database.execute(query);
        
        // Inefficient nested loops (performance issue)
        for (let user of result) {
            let permissions = await this.getAllPermissions(); // N+1 query problem
            for (let permission of permissions) {
                if (user.role === permission.role) {
                    this.grantPermission(user, permission);
                }
            }
        }
        
        // Error handling that silently fails (security/clean code issue)
        try {
            await this.logUserActivity(temp.userId, 'registration');
        } catch (error) {
            // Silent failure
        }
        
        return temp;
    }
    
    async getAllPermissions() {
        // Another database query in loop (performance issue)
        return await this.database.execute('SELECT * FROM permissions');
    }
    
    grantPermission(user, permission) {
        // Using Math.random for security-sensitive operation (security issue)
        let token = Math.floor(Math.random() * 900000) + 100000;
        
        // String concatenation in loop (performance issue)
        let logMessage = '';
        for (let i = 0; i < permission.length; i++) {
            logMessage += permission[i] + ', ';
        }
        
        console.log(`Granted permission with token: ${token}`);
    }
    
    // Functions with too many parameters (clean code issue)
    createUserProfile(firstName, lastName, email, phone, address, city, 
                     state, zipCode, country, dateOfBirth, gender, 
                     occupation, company) {
        // Complex conditional logic (testability issue)
        if (firstName && lastName && email && phone && address && city && state) {
            // File operation without abstraction (testability issue)
            const fs = require('fs');
            fs.appendFileSync('/tmp/user_profiles.log', 
                            `${firstName},${lastName},${email}\n`);
            return true;
        }
        return false;
    }
    
    // Type checking instead of polymorphism (design patterns issue)
    logUserActivity(userId, action) {
        if (typeof action === 'string') {
            this.logStringAction(action);
        } else if (typeof action === 'object' && Array.isArray(action)) {
            this.logArrayAction(action);
        } else if (typeof action === 'object') {
            this.logObjectAction(action);
        }
    }
}

// Function that should use Strategy pattern (design patterns issue)
function processPayment(paymentType, amount) {
    if (paymentType === 'credit_card') {
        // Credit card processing logic
        console.log('Processing credit card payment');
        let fee = amount * 0.03;
        return amount + fee;
    } else if (paymentType === 'paypal') {
        // PayPal processing logic
        console.log('Processing PayPal payment');
        let fee = amount * 0.025;
        return amount + fee;
    } else if (paymentType === 'bank_transfer') {
        // Bank transfer logic
        console.log('Processing bank transfer');
        let fee = 5.00;
        return amount + fee;
    }
    // Adding new payment method requires modifying this function
}

// Function with poor algorithm choice (performance issue)
function findUserByEmail(users, targetEmail) {
    // Linear search when Map would be O(1)
    for (let user of users) {
        if (user.email === targetEmail) {
            return user;
        }
    }
    return null;
}

// Function with eval vulnerability (security issue)
function calculateExpression(expression) {
    // Dangerous: allows arbitrary code execution
    return eval(expression);
}

// Function using global state (testability issue)
function getUserCount() {
    // Accessing global variable
    return userDatabase.query('SELECT COUNT(*) FROM users')[0].count;
}

// Function with magic numbers and poor naming (clean code issue)
function processData(d) {
    let result = [];
    for (let i = 0; i < d.length; i++) {
        if (d[i] > 100) { // Magic number
            result.push(d[i] * 1.5); // Magic number
        } else if (d[i] > 50) { // Magic number
            result.push(d[i] * 1.2); // Magic number
        } else {
            result.push(d[i]);
        }
    }
    return result;
}

// Function with performance anti-pattern
function sortUsersByAge(users) {
    // Inefficient bubble sort when built-in sort is available
    for (let i = 0; i < users.length; i++) {
        for (let j = 0; j < users.length - i - 1; j++) {
            if (users[j].age > users[j + 1].age) {
                [users[j], users[j + 1]] = [users[j + 1], users[j]];
            }
        }
    }
    return users;
}

// Function that violates DRY principle (clean code issue)
function validateEmail(email) {
    if (!email.includes('@')) return false;
    if (!email.includes('.')) return false;
    if (email.length < 5) return false;
    return true;
}

function validateBackupEmail(backupEmail) {
    // Duplicate validation logic
    if (!backupEmail.includes('@')) return false;
    if (!backupEmail.includes('.')) return false;
    if (backupEmail.length < 5) return false;
    return true;
}

// XSS vulnerability (security issue)
function displayUserMessage(message) {
    document.getElementById('user-message').innerHTML = message; // Dangerous
}

// Missing input validation (security issue)
function updateUserProfile(userId, profileData) {
    // No validation of profileData
    return fetch(`/api/users/${userId}`, {
        method: 'PUT',
        body: JSON.stringify(profileData),
        headers: { 'Content-Type': 'application/json' }
    });
}

// Prototype pollution vulnerability (security issue)
function mergeConfig(userConfig) {
    let config = {};
    for (let key in userConfig) {
        config[key] = userConfig[key]; // Can modify Object.prototype
    }
    return config;
}

// Function with memory leak potential (performance issue)
function createEventListeners() {
    let data = new Array(1000000).fill('data'); // Large array
    
    document.addEventListener('click', function() {
        // Closure captures large data array
        console.log(data.length);
    });
    // Event listener never removed, creates memory leak
}

// Inefficient DOM manipulation (performance issue)
function updateUserList(users) {
    let container = document.getElementById('user-list');
    container.innerHTML = ''; // Triggers reflow
    
    for (let user of users) {
        let div = document.createElement('div');
        div.innerHTML = `<span>${user.name}</span>`; // Multiple DOM manipulations
        container.appendChild(div); // Triggers reflow for each append
    }
}

// Missing error handling for async operations (testability/reliability issue)
async function fetchUserData(userId) {
    // No try-catch block
    let response = await fetch(`/api/users/${userId}`);
    let userData = await response.json();
    return userData;
}