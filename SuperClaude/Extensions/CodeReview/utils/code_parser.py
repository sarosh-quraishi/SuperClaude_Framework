#!/usr/bin/env python3
"""
Code Parser Utilities for Multi-Agent Code Review System
Handles code parsing, language detection, and context extraction
"""

import re
import ast
import os
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from dataclasses import dataclass
from enum import Enum


class SupportedLanguage(Enum):
    """Supported programming languages for code review"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CSHARP = "csharp"
    CPP = "cpp"
    C = "c"
    GO = "go"
    RUST = "rust"
    PHP = "php"
    RUBY = "ruby"
    KOTLIN = "kotlin"
    SWIFT = "swift"
    UNKNOWN = "unknown"


@dataclass
class CodeContext:
    """Represents parsed code with metadata"""
    content: str
    language: SupportedLanguage
    file_path: Optional[str]
    lines: List[str]
    functions: List[Dict[str, Any]]
    classes: List[Dict[str, Any]]
    imports: List[str]
    complexity_indicators: Dict[str, int]
    

class LanguageDetector:
    """Detects programming language from file extension or content"""
    
    EXTENSION_MAP = {
        '.py': SupportedLanguage.PYTHON,
        '.js': SupportedLanguage.JAVASCRIPT,
        '.jsx': SupportedLanguage.JAVASCRIPT,
        '.ts': SupportedLanguage.TYPESCRIPT,
        '.tsx': SupportedLanguage.TYPESCRIPT,
        '.java': SupportedLanguage.JAVA,
        '.cs': SupportedLanguage.CSHARP,
        '.cpp': SupportedLanguage.CPP,
        '.cxx': SupportedLanguage.CPP,
        '.cc': SupportedLanguage.CPP,
        '.c': SupportedLanguage.C,
        '.go': SupportedLanguage.GO,
        '.rs': SupportedLanguage.RUST,
        '.php': SupportedLanguage.PHP,
        '.rb': SupportedLanguage.RUBY,
        '.kt': SupportedLanguage.KOTLIN,
        '.swift': SupportedLanguage.SWIFT,
    }
    
    CONTENT_PATTERNS = {
        SupportedLanguage.PYTHON: [
            r'^\s*def\s+\w+\s*\(',
            r'^\s*class\s+\w+',
            r'^\s*import\s+\w+',
            r'^\s*from\s+\w+\s+import',
        ],
        SupportedLanguage.JAVASCRIPT: [
            r'function\s+\w+\s*\(',
            r'const\s+\w+\s*=',
            r'let\s+\w+\s*=',
            r'var\s+\w+\s*=',
        ],
        SupportedLanguage.JAVA: [
            r'public\s+class\s+\w+',
            r'private\s+\w+\s+\w+',
            r'public\s+static\s+void\s+main',
        ],
        SupportedLanguage.GO: [
            r'package\s+\w+',
            r'func\s+\w+\s*\(',
            r'import\s+\(',
        ],
    }
    
    @classmethod
    def detect_from_file_path(cls, file_path: str) -> SupportedLanguage:
        """Detect language from file extension"""
        if not file_path:
            return SupportedLanguage.UNKNOWN
            
        extension = Path(file_path).suffix.lower()
        return cls.EXTENSION_MAP.get(extension, SupportedLanguage.UNKNOWN)
    
    @classmethod
    def detect_from_content(cls, content: str) -> SupportedLanguage:
        """Detect language from code content patterns"""
        for language, patterns in cls.CONTENT_PATTERNS.items():
            matches = sum(1 for pattern in patterns 
                         if re.search(pattern, content, re.MULTILINE))
            # If multiple patterns match, likely this language
            if matches >= 2:
                return language
        
        return SupportedLanguage.UNKNOWN
    
    @classmethod
    def detect_language(cls, content: str, file_path: Optional[str] = None) -> SupportedLanguage:
        """Detect language using file path and content"""
        # Try file extension first
        if file_path:
            lang_from_path = cls.detect_from_file_path(file_path)
            if lang_from_path != SupportedLanguage.UNKNOWN:
                return lang_from_path
        
        # Fall back to content analysis
        return cls.detect_from_content(content)


class PythonCodeParser:
    """Specialized parser for Python code"""
    
    @staticmethod
    def parse_functions(content: str) -> List[Dict[str, Any]]:
        """Extract function definitions and metadata"""
        functions = []
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append({
                        'name': node.name,
                        'line_number': node.lineno,
                        'args': [arg.arg for arg in node.args.args],
                        'num_args': len(node.args.args),
                        'has_decorators': len(node.decorator_list) > 0,
                        'is_async': isinstance(node, ast.AsyncFunctionDef),
                        'docstring': ast.get_docstring(node)
                    })
        except SyntaxError:
            # Fall back to regex parsing for invalid syntax
            functions.extend(PythonCodeParser._parse_functions_regex(content))
        
        return functions
    
    @staticmethod
    def _parse_functions_regex(content: str) -> List[Dict[str, Any]]:
        """Regex fallback for function parsing"""
        functions = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            match = re.match(r'^\s*(async\s+)?def\s+(\w+)\s*\((.*?)\):', line)
            if match:
                is_async = bool(match.group(1))
                func_name = match.group(2)
                args_str = match.group(3).strip()
                
                # Count arguments
                args = [arg.strip().split('=')[0].strip() 
                       for arg in args_str.split(',') if arg.strip()]
                args = [arg for arg in args if arg not in ['self', 'cls']]
                
                functions.append({
                    'name': func_name,
                    'line_number': i,
                    'args': args,
                    'num_args': len(args),
                    'has_decorators': False,  # Can't detect easily with regex
                    'is_async': is_async,
                    'docstring': None
                })
        
        return functions
    
    @staticmethod
    def parse_classes(content: str) -> List[Dict[str, Any]]:
        """Extract class definitions and metadata"""
        classes = []
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                    classes.append({
                        'name': node.name,
                        'line_number': node.lineno,
                        'bases': [base.id if isinstance(base, ast.Name) else str(base) 
                                 for base in node.bases],
                        'num_methods': len(methods),
                        'method_names': [method.name for method in methods],
                        'has_decorators': len(node.decorator_list) > 0,
                        'docstring': ast.get_docstring(node)
                    })
        except SyntaxError:
            # Fall back to regex parsing
            classes.extend(PythonCodeParser._parse_classes_regex(content))
        
        return classes
    
    @staticmethod
    def _parse_classes_regex(content: str) -> List[Dict[str, Any]]:
        """Regex fallback for class parsing"""
        classes = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            match = re.match(r'^\s*class\s+(\w+)(?:\s*\((.*?)\))?:', line)
            if match:
                class_name = match.group(1)
                bases_str = match.group(2) or ""
                bases = [base.strip() for base in bases_str.split(',') if base.strip()]
                
                classes.append({
                    'name': class_name,
                    'line_number': i,
                    'bases': bases,
                    'num_methods': 0,  # Can't count easily with regex
                    'method_names': [],
                    'has_decorators': False,
                    'docstring': None
                })
        
        return classes
    
    @staticmethod
    def parse_imports(content: str) -> List[str]:
        """Extract import statements"""
        imports = []
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}" if module else alias.name)
        except SyntaxError:
            # Fall back to regex parsing
            imports.extend(PythonCodeParser._parse_imports_regex(content))
        
        return imports
    
    @staticmethod
    def _parse_imports_regex(content: str) -> List[str]:
        """Regex fallback for import parsing"""
        imports = []
        lines = content.split('\n')
        
        for line in lines:
            # Handle "import module" statements
            import_match = re.match(r'^\s*import\s+([\w\.]+)', line)
            if import_match:
                imports.append(import_match.group(1))
                continue
            
            # Handle "from module import ..." statements
            from_match = re.match(r'^\s*from\s+([\w\.]+)\s+import\s+(.+)', line)
            if from_match:
                module = from_match.group(1)
                imported_items = from_match.group(2)
                # Simple parsing - doesn't handle all edge cases
                for item in imported_items.split(','):
                    item = item.strip().split(' as ')[0].strip()
                    if item != '*':
                        imports.append(f"{module}.{item}")
        
        return imports


class ComplexityAnalyzer:
    """Analyzes code complexity indicators"""
    
    @staticmethod
    def analyze_complexity(content: str, language: SupportedLanguage) -> Dict[str, int]:
        """Calculate various complexity metrics"""
        lines = content.split('\n')
        
        metrics = {
            'lines_of_code': len([line for line in lines if line.strip()]),
            'total_lines': len(lines),
            'blank_lines': len([line for line in lines if not line.strip()]),
            'comment_lines': ComplexityAnalyzer._count_comment_lines(lines, language),
            'nested_depth': ComplexityAnalyzer._calculate_nesting_depth(lines, language),
            'cyclomatic_complexity': ComplexityAnalyzer._estimate_cyclomatic_complexity(content),
            'function_count': ComplexityAnalyzer._count_functions(content, language),
            'class_count': ComplexityAnalyzer._count_classes(content, language),
        }
        
        return metrics
    
    @staticmethod
    def _count_comment_lines(lines: List[str], language: SupportedLanguage) -> int:
        """Count comment lines based on language"""
        comment_patterns = {
            SupportedLanguage.PYTHON: [r'^\s*#'],
            SupportedLanguage.JAVASCRIPT: [r'^\s*//', r'^\s*/\*', r'^\s*\*'],
            SupportedLanguage.JAVA: [r'^\s*//', r'^\s*/\*', r'^\s*\*'],
            SupportedLanguage.CPP: [r'^\s*//', r'^\s*/\*', r'^\s*\*'],
        }
        
        patterns = comment_patterns.get(language, [r'^\s*#'])
        count = 0
        
        for line in lines:
            if any(re.match(pattern, line) for pattern in patterns):
                count += 1
        
        return count
    
    @staticmethod
    def _calculate_nesting_depth(lines: List[str], language: SupportedLanguage) -> int:
        """Calculate maximum nesting depth"""
        max_depth = 0
        current_depth = 0
        
        # Language-specific indentation patterns
        if language == SupportedLanguage.PYTHON:
            for line in lines:
                if line.strip():
                    # Count leading whitespace
                    indent = len(line) - len(line.lstrip())
                    # Assume 4 spaces per indent level
                    depth = indent // 4
                    max_depth = max(max_depth, depth)
        else:
            # For brace-based languages, count braces
            for line in lines:
                current_depth += line.count('{') - line.count('}')
                max_depth = max(max_depth, current_depth)
        
        return max_depth
    
    @staticmethod
    def _estimate_cyclomatic_complexity(content: str) -> int:
        """Estimate cyclomatic complexity by counting decision points"""
        # Basic estimation - count if, while, for, case, catch, &&, ||
        decision_keywords = ['if', 'while', 'for', 'case', 'catch', 'except']
        complexity = 1  # Base complexity
        
        for keyword in decision_keywords:
            complexity += len(re.findall(rf'\b{keyword}\b', content, re.IGNORECASE))
        
        # Count logical operators
        complexity += len(re.findall(r'&&|\|\|', content))
        complexity += len(re.findall(r'\band\b|\bor\b', content))
        
        return complexity
    
    @staticmethod
    def _count_functions(content: str, language: SupportedLanguage) -> int:
        """Count function definitions"""
        patterns = {
            SupportedLanguage.PYTHON: r'^\s*def\s+\w+',
            SupportedLanguage.JAVASCRIPT: r'function\s+\w+|=>\s*{|\w+\s*:\s*function',
            SupportedLanguage.JAVA: r'(public|private|protected).*\s+\w+\s*\(',
            SupportedLanguage.CPP: r'^\s*\w+.*\w+\s*\([^)]*\)\s*{',
        }
        
        pattern = patterns.get(language, r'function|def|method')
        return len(re.findall(pattern, content, re.MULTILINE | re.IGNORECASE))
    
    @staticmethod
    def _count_classes(content: str, language: SupportedLanguage) -> int:
        """Count class definitions"""
        patterns = {
            SupportedLanguage.PYTHON: r'^\s*class\s+\w+',
            SupportedLanguage.JAVASCRIPT: r'class\s+\w+',
            SupportedLanguage.JAVA: r'(public|private|protected)?\s*class\s+\w+',
            SupportedLanguage.CPP: r'class\s+\w+',
        }
        
        pattern = patterns.get(language, r'class\s+\w+')
        return len(re.findall(pattern, content, re.MULTILINE | re.IGNORECASE))


class CodeParser:
    """Main code parser that coordinates language-specific parsing"""
    
    def __init__(self):
        self.language_detector = LanguageDetector()
        self.python_parser = PythonCodeParser()
        self.complexity_analyzer = ComplexityAnalyzer()
    
    def parse_code(self, content: str, file_path: Optional[str] = None) -> CodeContext:
        """Parse code and extract comprehensive context"""
        # Detect language
        language = self.language_detector.detect_language(content, file_path)
        
        # Split into lines
        lines = content.split('\n')
        
        # Parse functions and classes (currently only Python supported)
        functions = []
        classes = []
        imports = []
        
        if language == SupportedLanguage.PYTHON:
            functions = self.python_parser.parse_functions(content)
            classes = self.python_parser.parse_classes(content)
            imports = self.python_parser.parse_imports(content)
        
        # Analyze complexity
        complexity_indicators = self.complexity_analyzer.analyze_complexity(content, language)
        
        return CodeContext(
            content=content,
            language=language,
            file_path=file_path,
            lines=lines,
            functions=functions,
            classes=classes,
            imports=imports,
            complexity_indicators=complexity_indicators
        )
    
    def parse_file(self, file_path: str) -> CodeContext:
        """Parse code from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self.parse_code(content, file_path)
        except Exception as e:
            # Return minimal context on error
            return CodeContext(
                content="",
                language=SupportedLanguage.UNKNOWN,
                file_path=file_path,
                lines=[],
                functions=[],
                classes=[],
                imports=[],
                complexity_indicators={'error': str(e)}
            )
    
    def extract_code_block(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract code block from markdown-style text"""
        # Look for code blocks with language specification
        pattern = r'```(\w+)?\n(.*?)```'
        match = re.search(pattern, text, re.DOTALL)
        
        if match:
            language_hint = match.group(1)
            code = match.group(2).strip()
            return code, language_hint
        
        # Look for simple code blocks without language
        pattern = r'```\n(.*?)```'
        match = re.search(pattern, text, re.DOTALL)
        
        if match:
            code = match.group(1).strip()
            return code, None
        
        return None, None