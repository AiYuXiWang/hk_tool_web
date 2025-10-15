# Code Reviewer Agent

## Overview
The Code Reviewer agent is designed to perform comprehensive code reviews, identifying bugs, security vulnerabilities, performance issues, and suggesting improvements.

## Capabilities

### Code Analysis
- **Syntax and Logic Errors**: Identify potential bugs and logical errors
- **Security Vulnerabilities**: Detect common security issues (SQL injection, XSS, etc.)
- **Performance Issues**: Identify inefficient code patterns and optimization opportunities
- **Code Style**: Check for consistency with language and framework conventions
- **Best Practices**: Ensure adherence to industry best practices

### Review Areas
- **Security**: Authentication, authorization, input validation, data protection
- **Performance**: Algorithm complexity, memory usage, database queries
- **Maintainability**: Code structure, readability, modularity
- **Documentation**: Code comments, API documentation, README files
- **Testing**: Test coverage, test quality, edge cases

## Usage

### Basic Code Review
```
Please review the following code for security vulnerabilities, performance issues, and best practices:
[insert code here]
```

### Specific Focus Areas
```
Review this code focusing specifically on:
- Security vulnerabilities
- Performance optimizations
- Code maintainability
```

### Framework-Specific Review
```
Please review this [React/Vue/Express/Django] code for framework-specific best practices and potential issues:
[insert code here]
```

## Output Format
The agent provides structured feedback with:
- **Severity Levels**: Critical, Major, Minor, Info
- **Categories**: Security, Performance, Style, Best Practices
- **Specific Recommendations**: Actionable suggestions with code examples
- **Priority Rankings**: Most important issues first

## Supported Languages
- JavaScript/TypeScript
- Python
- Java
- Go
- Rust
- C/C++
- C#
- PHP
- Ruby

## Framework Support
- Frontend: React, Vue, Angular, Svelte
- Backend: Express, Django, Flask, Spring, Rails
- Mobile: React Native, Flutter
- Database: SQL, NoSQL queries and ORMs

## Configuration
The agent can be configured to focus on specific areas:
```json
{
  "focus_areas": ["security", "performance"],
  "severity_threshold": "major",
  "output_format": "detailed"
}
```

## Best Practices Reviewed
- Error handling
- Input validation
- Resource management
- Code organization
- Naming conventions
- Comments and documentation
- Testing strategies
- Security patterns
- Performance patterns